from pathlib import Path
from typing import Dict, List

import numpy as np, pandas as pd, torch
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from .config import DEFAULT_DATA_PATH, DEFAULT_MODEL_PATH
from .data import EssayDataset
from .model_utils import get_device, load_model_artifacts
from .inference import run_model_inference

def evaluate_model(
	model: torch.nn.Module,
	data_loader: DataLoader,
	*,
	device: torch.device,
	temperature: float | None = None,
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

	with torch.no_grad():
		for batch in data_loader:
			batch = {key: value.to(device) for key, value in batch.items()}
			labels = batch["labels"]
			sample_ids = batch.get("sample_id")
			if sample_ids is not None:
				sample_ids_list = sample_ids.detach().cpu().tolist()
			else:
				sample_ids_list = [None] * labels.shape[0]

			inputs = {key: value for key, value in batch.items() if key not in {"labels", "sample_id"}}
			inference = run_model_inference(
				model,
				inputs,
				temperature=resolved_temperature,
			)
			mean_logits = inference["mean_logits"]
			mean_probs = inference["mean_probs"]
			raw_mean_probs = inference["raw_mean_probs"]
			std_probs = inference["std_probs"]
			entropy_values = inference["entropy"]
			variation_values = inference["variation"]

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
					"mc_dropout_passes": 16,
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
		"mc_dropout_passes": 16,
		"mc_dropout_enabled": True,
	}


def evaluate_saved_model(
	data_path: Path | str = DEFAULT_DATA_PATH,
	*,
	model_path: Path | str = DEFAULT_MODEL_PATH,
	batch_size: int = 32,
	max_length: int = 512,
	sample_size: float | None = None,
	random_state: int = 42,
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
	)

	return metrics
