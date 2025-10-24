from pathlib import Path
from typing import Dict

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

	with torch.no_grad():
		for batch in data_loader:
			batch = {key: value.to(device) for key, value in batch.items()}
			outputs = model(
				input_ids=batch["input_ids"],
				attention_mask=batch["attention_mask"],
				labels=batch["labels"]
			)
			losses.append(outputs.loss.item())
			logits = outputs.logits.detach().cpu()
			predictions.extend(torch.argmax(logits, dim=1).tolist())
			targets.extend(batch["labels"].detach().cpu().tolist())

	cm = confusion_matrix(targets, predictions)
	report = classification_report(targets, predictions, target_names=["human", "generated"], output_dict=True)
	accuracy = accuracy_score(targets, predictions)

	return {
		"loss": float(np.mean(losses)) if losses else 0.0,
		"accuracy": float(accuracy),
		"report": report,
		"confusion_matrix": cm
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
