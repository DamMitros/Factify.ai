from contextlib import nullcontext
from pathlib import Path
from typing import Dict, List

import numpy as np, pandas as pd, torch
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from .config import (DEFAULT_DATA_PATH, DEFAULT_MODEL_PATH,
	MC_DROPOUT_ENABLED,
	MC_DROPOUT_PASSES,
	MC_DROPOUT_RANDOM_SEED)
from .data import EssayDataset
from .model_utils import dropout_train_mode, get_device, load_model_artifacts

_PROB_EPS = 1e-12

def _prob_entropy(probs: torch.Tensor) -> torch.Tensor:
	return -(probs * (probs + _PROB_EPS).log()).sum(dim=1)

def _variation_ratio(predictions: torch.Tensor, num_classes: int) -> torch.Tensor:
	if predictions.ndim < 2:
		return torch.zeros(predictions.shape[-1], dtype=torch.float32, device=predictions.device)
	frequencies = F.one_hot(predictions, num_classes=num_classes).float().mean(dim=0)
	max_frequency = frequencies.max(dim=1).values
	return 1.0 - max_frequency

def evaluate_model(
	model: torch.nn.Module,
	data_loader: DataLoader,
	*,
	device: torch.device,
	temperature: float | None = None,
	mc_dropout_enabled: bool | None = None,
	mc_dropout_passes: int | None = None,
	mc_dropout_seed: int | None = None
) -> Dict[str, object]:
	model.eval()
	predictions: list[int] = []
	targets: list[int] = []
	losses: list[float] = []
	prob_records: List[Dict[str, object]] = []
	dataset = getattr(data_loader, "dataset", None)
	dataset_frame = getattr(dataset, "frame", None)
	resolved_temperature = float(temperature if temperature is not None else getattr(model, "_factify_temperature", 1.0))
	if resolved_temperature <= 0:
		resolved_temperature = 1.0

	resolved_mc_enabled = MC_DROPOUT_ENABLED if mc_dropout_enabled is None else mc_dropout_enabled
	resolved_mc_passes = mc_dropout_passes if mc_dropout_passes is not None else MC_DROPOUT_PASSES
	passes = max(1, resolved_mc_passes) if resolved_mc_enabled else 1
	seed_base = MC_DROPOUT_RANDOM_SEED if mc_dropout_seed is None else mc_dropout_seed
	if passes <= 1:
		seed_base = None
	use_mc_dropout = passes > 1

	with torch.no_grad():
		for batch in data_loader:
			batch = {key: value.to(device) for key, value in batch.items()}
			labels = batch["labels"]
			sample_ids = batch.get("sample_id")
			if sample_ids is not None:
				sample_ids_list = sample_ids.detach().cpu().tolist()
			else:
				sample_ids_list = [None] * labels.shape[0]

			context = dropout_train_mode(model) if use_mc_dropout else nullcontext()
			with context:
				if use_mc_dropout:
					raw_prob_trials: list[torch.Tensor] = []
					calibrated_logits_trials: list[torch.Tensor] = []
					prob_trials: list[torch.Tensor] = []
					pred_trials: list[torch.Tensor] = []
					for pass_idx in range(passes):
						if seed_base is not None:
							pass_seed = seed_base + pass_idx
							torch.manual_seed(pass_seed)
							if torch.cuda.is_available():
								torch.cuda.manual_seed_all(pass_seed)
						outputs = model(
							input_ids=batch["input_ids"],
							attention_mask=batch["attention_mask"]
						)
						logits = outputs.logits.detach()
						raw_prob_trials.append(torch.softmax(logits, dim=1))
						calibrated_logits_pass = (logits / resolved_temperature).detach()
						calibrated_logits_trials.append(calibrated_logits_pass)
						probs_pass = torch.softmax(calibrated_logits_pass, dim=1)
						prob_trials.append(probs_pass)
						pred_trials.append(torch.argmax(probs_pass, dim=1))
					calibrated_logits_tensor = torch.stack(calibrated_logits_trials, dim=0)
					probs_tensor = torch.stack(prob_trials, dim=0)
					raw_probs_tensor = torch.stack(raw_prob_trials, dim=0)
					mean_logits = calibrated_logits_tensor.mean(dim=0)
					mean_probs = probs_tensor.mean(dim=0)
					std_probs = probs_tensor.std(dim=0, unbiased=False)
					entropy_values = _prob_entropy(mean_probs)
					pred_tensor = torch.stack(pred_trials, dim=0)
					variation_values = _variation_ratio(pred_tensor, num_classes=mean_probs.shape[1])
					raw_mean_probs = raw_probs_tensor.mean(dim=0)
				else:
					outputs = model(
						input_ids=batch["input_ids"],
						attention_mask=batch["attention_mask"]
					)
					logits = outputs.logits.detach()
					raw_mean_probs = torch.softmax(logits, dim=1)
					mean_logits = (logits / resolved_temperature).detach()
					mean_probs = torch.softmax(mean_logits, dim=1)
					std_probs = torch.zeros_like(mean_probs)
					entropy_values = _prob_entropy(mean_probs)
					variation_values = torch.zeros(mean_probs.shape[0], dtype=torch.float32, device=mean_probs.device)

			loss = F.cross_entropy(mean_logits, labels)
			losses.append(float(loss.item()))
			batch_predictions_tensor = torch.argmax(mean_probs, dim=1)
			batch_predictions_list = batch_predictions_tensor.detach().cpu().tolist()
			predictions.extend(batch_predictions_list)
			target_batch = labels.detach().cpu().tolist()
			targets.extend(target_batch)

			mean_probs_cpu = mean_probs.detach().cpu()
			raw_mean_cpu = raw_mean_probs.detach().cpu()
			std_probs_cpu = std_probs.detach().cpu()
			entropy_cpu = entropy_values.detach().cpu()
			variation_cpu = variation_values.detach().cpu()

			for idx, (sid, true_label, pred_label) in enumerate(zip(sample_ids_list, target_batch, batch_predictions_list)):
				record: Dict[str, object] = {
					"sample_id": None if sid is None else int(sid),
					"true_label": int(true_label),
					"pred_label": int(pred_label),
					"prob_generated_raw": float(raw_mean_cpu[idx][1]),
					"prob_human_raw": float(raw_mean_cpu[idx][0]),
					"prob_generated": float(mean_probs_cpu[idx][1]),
					"prob_human": float(mean_probs_cpu[idx][0]),
					"prob_generated_std": float(std_probs_cpu[idx][1]),
					"prob_entropy": float(entropy_cpu[idx]),
					"prob_variation_ratio": float(variation_cpu[idx]),
					"temperature": float(resolved_temperature),
					"mc_dropout_passes": int(passes),
				}
				if dataset_frame is not None and sid is not None:
					text = dataset_frame.iloc[sid]["text"]
					record["text"] = str(text)
					record["word_count"] = len(str(text).split())
				prob_records.append(record)

	cm = confusion_matrix(targets, predictions)
	report = classification_report(targets, predictions, target_names=["human", "generated"], output_dict=True)
	accuracy = accuracy_score(targets, predictions)

	return {
		"loss": float(np.mean(losses)) if losses else 0.0,
		"accuracy": float(accuracy),
		"report": report,
		"confusion_matrix": cm,
		"records": prob_records,
		"mc_dropout_passes": int(passes),
		"mc_dropout_enabled": bool(use_mc_dropout),
	}


def evaluate_saved_model(
	data_path: Path | str = DEFAULT_DATA_PATH,
	*,
	model_path: Path | str = DEFAULT_MODEL_PATH,
	batch_size: int = 32,
	max_length: int = 512,
	sample_size: float | None = None,
	random_state: int = 42,
	mc_dropout_enabled: bool | None = None,
	mc_dropout_passes: int | None = None,
	mc_dropout_seed: int | None = None,
) -> Dict[str, object]:
	frame = pd.read_csv(data_path)
	frame = frame.dropna(subset=["text", "generated"]).copy()
	frame["generated"] = frame["generated"].astype(int)

	if sample_size is not None:
		_, frame = train_test_split(
			frame,
			test_size=sample_size,
			stratify=frame["generated"],
			random_state=random_state
		)

	device = get_device()
	tokenizer, model = load_model_artifacts(model_path=model_path, force_reload=True, device=device)
	loader = DataLoader(EssayDataset(frame, tokenizer, max_length=max_length), batch_size=batch_size)
	metrics = evaluate_model(
		model,
		loader,
		device=device,
		mc_dropout_enabled=mc_dropout_enabled,
		mc_dropout_passes=mc_dropout_passes,
		mc_dropout_seed=mc_dropout_seed,
	)

	return metrics

def predict_proba(
	text: str,
	model_path: Path | str = DEFAULT_MODEL_PATH,
	*,
	mc_dropout_enabled: bool | None = None,
	mc_dropout_passes: int | None = None,
	mc_dropout_seed: int | None = None,
	return_details: bool = False
) -> float | Dict[str, float]:
	tokenizer, model = load_model_artifacts(model_path)
	device = next(model.parameters()).device
	encoded = tokenizer(
		text,
		truncation=True,
		padding=True,
		max_length=512,
		return_tensors="pt",
	)
	encoded = {key: value.to(device) for key, value in encoded.items()}

	temperature = float(getattr(model, "_factify_temperature", 1.0))
	if temperature <= 0:
		temperature = 1.0

	resolved_mc_enabled = MC_DROPOUT_ENABLED if mc_dropout_enabled is None else mc_dropout_enabled
	resolved_mc_passes = mc_dropout_passes if mc_dropout_passes is not None else MC_DROPOUT_PASSES
	passes = max(1, resolved_mc_passes) if resolved_mc_enabled else 1
	seed_base = MC_DROPOUT_RANDOM_SEED if mc_dropout_seed is None else mc_dropout_seed
	if passes <= 1:
		seed_base = None
	use_mc_dropout = passes > 1

	with torch.no_grad():
		if use_mc_dropout:
			raw_prob_trials: list[torch.Tensor] = []
			prob_trials: list[torch.Tensor] = []
			logit_trials: list[torch.Tensor] = []
			pred_trials: list[torch.Tensor] = []
			context = dropout_train_mode(model)
			with context:
				for pass_idx in range(passes):
					if seed_base is not None:
						pass_seed = seed_base + pass_idx
						torch.manual_seed(pass_seed)
						if torch.cuda.is_available():
							torch.cuda.manual_seed_all(pass_seed)
					outputs = model(**encoded)
					logits = outputs.logits.detach()
					raw_prob_trials.append(torch.softmax(logits, dim=1))
					calibrated_logits = (logits / temperature).detach()
					logit_trials.append(calibrated_logits)
					probs = torch.softmax(calibrated_logits, dim=1)
					prob_trials.append(probs)
					pred_trials.append(torch.argmax(probs, dim=1))
			logits_tensor = torch.stack(logit_trials, dim=0)
			probs_tensor = torch.stack(prob_trials, dim=0)
			raw_probs_tensor = torch.stack(raw_prob_trials, dim=0)
			mean_logits = logits_tensor.mean(dim=0)
			mean_probs = probs_tensor.mean(dim=0)
			std_probs = probs_tensor.std(dim=0, unbiased=False)
			entropy_value = _prob_entropy(mean_probs)[0]
			pred_tensor = torch.stack(pred_trials, dim=0)
			variation_value = _variation_ratio(pred_tensor, num_classes=mean_probs.shape[1])[0]
			raw_mean_probs = raw_probs_tensor.mean(dim=0)
		else:
			outputs = model(**encoded)
			logits = outputs.logits.detach()
			raw_mean_probs = torch.softmax(logits, dim=1)
			mean_logits = (logits / temperature).detach()
			mean_probs = torch.softmax(mean_logits, dim=1)
			std_probs = torch.zeros_like(mean_probs)
			entropy_value = _prob_entropy(mean_probs)[0]
			variation_value = torch.tensor(0.0, device=mean_probs.device)

	prob_generated = float(mean_probs[0, 1].detach().cpu().item())
	if not return_details:
		return prob_generated

	return {
		"prob_generated": prob_generated,
		"prob_human": float(mean_probs[0, 0].detach().cpu().item()),
		"prob_generated_raw": float(raw_mean_probs[0, 1].detach().cpu().item()),
		"prob_human_raw": float(raw_mean_probs[0, 0].detach().cpu().item()),
		"prob_generated_std": float(std_probs[0, 1].detach().cpu().item()),
		"prob_human_std": float(std_probs[0, 0].detach().cpu().item()),
		"prob_entropy": float(entropy_value.detach().cpu().item()),
		"prob_variation_ratio": float(variation_value.detach().cpu().item()),
		"mc_dropout_passes": int(passes),
		"temperature": float(temperature),
	}
