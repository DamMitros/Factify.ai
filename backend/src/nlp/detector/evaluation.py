from pathlib import Path
from typing import Dict, List

import numpy as np, pandas as pd, torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from .config import DEFAULT_DATA_PATH, DEFAULT_MODEL_PATH
from .data import EssayDataset
from .model_utils import get_device, load_model_artifacts


def evaluate_model(model: torch.nn.Module, data_loader: DataLoader, *, device: torch.device) -> Dict[str, object]:
	model.eval()
	predictions: list[int] = []
	targets: list[int] = []
	losses: list[float] = []
	prob_records: List[Dict[str, object]] = []
	dataset = getattr(data_loader, "dataset", None)
	dataset_frame = getattr(dataset, "frame", None)

	with torch.no_grad():
		for batch in data_loader:
			batch = {key: value.to(device) for key, value in batch.items()}
			sample_ids = batch.get("sample_id")
			if sample_ids is not None:
				sample_ids_list = sample_ids.detach().cpu().tolist()
			else:
				sample_ids_list = [None] * batch["labels"].shape[0]
			outputs = model(
				input_ids=batch["input_ids"],
				attention_mask=batch["attention_mask"],
				labels=batch["labels"]
			)
			losses.append(outputs.loss.item())
			logits = outputs.logits.detach().cpu()
			batch_predictions = torch.argmax(logits, dim=1).tolist()
			predictions.extend(batch_predictions)
			target_batch = batch["labels"].detach().cpu().tolist()
			targets.extend(target_batch)
			probabilities = torch.softmax(outputs.logits, dim=1).detach().cpu().tolist()
			for sid, true_label, pred_label, probs in zip(sample_ids_list, target_batch, batch_predictions, probabilities):
				record: Dict[str, object] = {
					"sample_id": None if sid is None else int(sid),
					"true_label": int(true_label),
					"pred_label": int(pred_label),
					"prob_generated": float(probs[1]),
					"prob_human": float(probs[0])
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
		"records": prob_records
	}


def evaluate_saved_model(data_path: Path | str = DEFAULT_DATA_PATH, *, model_path: Path | str = DEFAULT_MODEL_PATH, 
												 batch_size: int = 32, max_length: int = 512, sample_size: float | None = None, 
												 random_state: int = 42) -> Dict[str, object]:
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
	metrics = evaluate_model(model, loader, device=device)

	return metrics

def predict_proba(text: str, model_path: Path | str = DEFAULT_MODEL_PATH) -> float:
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

	with torch.no_grad():
		outputs = model(**encoded)
		probabilities = torch.softmax(outputs.logits, dim=1)

	return float(probabilities[0, 1].detach().cpu().item())
