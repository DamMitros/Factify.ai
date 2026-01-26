from dataclasses import dataclass
from typing import Dict, List, Tuple

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader

@dataclass(frozen=True)
class CalibrationOutcome:
  temperature: float
  report: Dict[str, object]


def _gather_logits(model: torch.nn.Module, loader: DataLoader, *, device: torch.device
                   ) -> Tuple[torch.Tensor, torch.Tensor]:
  logits_batches: List[torch.Tensor] = []
  label_batches: List[torch.Tensor] = []

  model.eval()
  with torch.no_grad():
    for batch in loader:
      batch = {key: value.to(device) for key, value in batch.items() if key in {"input_ids", "attention_mask", "labels"}}
      if not batch:
        continue
      outputs = model(
        input_ids=batch.get("input_ids"),
        attention_mask=batch.get("attention_mask")
      )
      logits_batches.append(outputs.logits.detach())
      label_batches.append(batch["labels"].detach())

  if not logits_batches:
    return torch.empty(0, device=device), torch.empty(0, dtype=torch.long, device=device)

  logits = torch.cat(logits_batches, dim=0).to(device)
  labels = torch.cat(label_batches, dim=0).to(device)
  return logits, labels

def _compute_bin_stats(confidences: torch.Tensor, accuracies: torch.Tensor, *,
                        bin_boundaries: torch.Tensor) -> Tuple[float, float, List[Dict[str, float]]]:
  total = confidences.shape[0]
  if total == 0:
    return 0.0, 0.0, []

  ece = torch.tensor(0.0, device=confidences.device)
  mce = torch.tensor(0.0, device=confidences.device)
  bin_payload: List[Dict[str, float]] = []

  for idx in range(len(bin_boundaries) - 1):
    left = bin_boundaries[idx]
    right = bin_boundaries[idx + 1]
    if idx == len(bin_boundaries) - 2:
      mask = (confidences >= left) & (confidences <= right)
    else:
      mask = (confidences >= left) & (confidences < right)

    count = int(mask.sum().item())
    if count == 0:
      bin_payload.append({
        "bin_index": float(idx),
        "bin_start": float(left.item()),
        "bin_end": float(right.item()),
        "count": 0.0,
        "avg_confidence": 0.0,
        "avg_accuracy": 0.0,
      })
      continue

    bin_confidence = confidences[mask].mean()
    bin_accuracy = accuracies[mask].mean()
    gap = torch.abs(bin_confidence - bin_accuracy)
    weight = count / total
    ece += gap * weight
    mce = torch.maximum(mce, gap)

    bin_payload.append({
      "bin_index": float(idx),
      "bin_start": float(left.item()),
      "bin_end": float(right.item()),
      "count": float(count),
      "avg_confidence": float(bin_confidence.item()),
      "avg_accuracy": float(bin_accuracy.item()),
    })

  return float(ece.item()), float(mce.item()), bin_payload


def fit_temperature_scaling(
  model: torch.nn.Module,
  loader: DataLoader | None,
  *,
  device: torch.device,
  max_iter: int = 50,
  n_bins: int = 15
) -> CalibrationOutcome:
  if loader is None:
    return CalibrationOutcome(
      temperature=1.0,
      report={
        "temperature": 1.0,
        "samples": 0,
        "note": "Calibration skipped — no calibration loader provided."
      }
    )

  logits, labels = _gather_logits(model, loader, device=device)
  if logits.numel() == 0:
    return CalibrationOutcome(
      temperature=1.0,
      report={
        "temperature": 1.0,
        "samples": 0,
        "note": "Calibration skipped — no samples available."
      }
    )

  log_temperature = torch.zeros(1, device=device, requires_grad=True)
  optimizer = torch.optim.LBFGS([log_temperature], lr=0.01, max_iter=max_iter, line_search_fn="strong_wolfe")

  def _closure() -> torch.Tensor:
    optimizer.zero_grad()
    temperature = torch.exp(log_temperature)
    loss = F.cross_entropy(logits / temperature, labels)
    loss.backward()
    return loss

  optimizer.step(_closure)

  fitted_temperature = float(torch.exp(log_temperature.detach()).clamp(min=1e-3, max=100.0).item())

  calibrated_logits = logits / fitted_temperature
  probs_before = torch.softmax(logits, dim=1)
  probs_after = torch.softmax(calibrated_logits, dim=1)

  confidences_before, preds_before = torch.max(probs_before, dim=1)
  confidences_after, preds_after = torch.max(probs_after, dim=1)
  accuracies = preds_before.eq(labels).float()
  accuracies_after = preds_after.eq(labels).float()

  bin_boundaries = torch.linspace(0.0, 1.0, steps=n_bins + 1, device=logits.device)
  ece_before, mce_before, bins_before = _compute_bin_stats(confidences_before, accuracies, bin_boundaries=bin_boundaries)
  ece_after, mce_after, bins_after = _compute_bin_stats(confidences_after, accuracies_after, bin_boundaries=bin_boundaries)

  merged_bins: List[Dict[str, float]] = []
  for idx in range(len(bin_boundaries) - 1):
    before_payload = bins_before[idx] if idx < len(bins_before) else None
    after_payload = bins_after[idx] if idx < len(bins_after) else None
    merged_bins.append({
      "bin_index": float(idx),
      "bin_start": float(bin_boundaries[idx].item()),
      "bin_end": float(bin_boundaries[idx + 1].item()),
      "count": (before_payload or {}).get("count", 0.0),
      "avg_confidence_before": (before_payload or {}).get("avg_confidence", 0.0),
      "avg_accuracy_before": (before_payload or {}).get("avg_accuracy", 0.0),
      "avg_confidence_after": (after_payload or {}).get("avg_confidence", 0.0),
      "avg_accuracy_after": (after_payload or {}).get("avg_accuracy", 0.0),
    })

  report: Dict[str, object] = {
    "temperature": fitted_temperature,
    "samples": int(labels.shape[0]),
    "nll_before": float(F.cross_entropy(logits, labels).item()),
    "nll_after": float(F.cross_entropy(calibrated_logits, labels).item()),
    "ece_before": ece_before,
    "ece_after": ece_after,
    "mce_before": mce_before,
    "mce_after": mce_after,
    "bins": merged_bins,
  }

  return CalibrationOutcome(temperature=fitted_temperature, report=report)
