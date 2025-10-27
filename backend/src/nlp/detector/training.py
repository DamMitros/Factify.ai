from dataclasses import dataclass
from pathlib import Path

import numpy as np, torch
from transformers import AutoModelForSequenceClassification, get_linear_schedule_with_warmup

from .config import (
	DEFAULT_CONFUSION_MATRIX_PATH,
	DEFAULT_DATA_PATH,
	DEFAULT_METRICS_PATH,
	DEFAULT_MODEL_PATH,
	NLP_MODEL_NAME,
	NUM_LABELS
)
from .data import create_dataloaders, prepare_splits
from .evaluation import evaluate_model
from .model_utils import get_device, load_model_artifacts
from .reporting import plot_confusion_matrix, save_metrics

@dataclass
class TrainingArtifacts:
	model_path: Path
	metrics_path: Path
	confusion_matrix_path: Path

def train_model(
	data_path: Path | str = DEFAULT_DATA_PATH,
	*,
	epochs: int = 1,
	batch_size: int = 4,
	learning_rate: float = 2e-5,
	weight_decay: float = 0.01,
	warmup_ratio: float = 0.1,
	max_length: int = 128,
	test_size: float = 0.2,
	random_state: int = 42,
	output_model_path: Path | str = DEFAULT_MODEL_PATH,
	metrics_path: Path | str = DEFAULT_METRICS_PATH,
	confusion_matrix_path: Path | str = DEFAULT_CONFUSION_MATRIX_PATH
) -> TrainingArtifacts:
	device = get_device()
	tokenizer, _ = load_model_artifacts(force_reload=True, device=device)

	train_frame, test_frame = prepare_splits(data_path, test_size=test_size, random_state=random_state)
	train_loader, test_loader = create_dataloaders(
		train_frame,
		test_frame,
		tokenizer,
		max_length=max_length,
		batch_size=batch_size
	)

	model = AutoModelForSequenceClassification.from_pretrained(NLP_MODEL_NAME, num_labels=NUM_LABELS)
	model.to(device)

	optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=weight_decay)
	total_steps = len(train_loader) * epochs
	warmup_steps = int(total_steps * warmup_ratio)
	scheduler = get_linear_schedule_with_warmup(
		optimizer,
		num_warmup_steps=max(0, warmup_steps),
		num_training_steps=total_steps
	)

	for epoch in range(epochs):
		model.train()
		epoch_losses: list[float] = []
		for batch in train_loader:
			batch = {key: value.to(device) for key, value in batch.items()}
			outputs = model(
				input_ids=batch["input_ids"],
				attention_mask=batch["attention_mask"],
				labels=batch["labels"]
			)
			loss = outputs.loss
			loss.backward()
			torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
			optimizer.step()
			scheduler.step()
			optimizer.zero_grad()
			epoch_losses.append(loss.item())

		avg_loss = float(np.mean(epoch_losses)) if epoch_losses else 0.0
		print(f"Epoch {epoch + 1}/{epochs} — training loss: {avg_loss:.4f}")

	metrics = evaluate_model(model, test_loader, device=device)

	output_model_path = Path(output_model_path)
	output_model_path.parent.mkdir(parents=True, exist_ok=True)
	torch.save(model.state_dict(), output_model_path)

	metrics_path = Path(metrics_path)
	metrics_path.parent.mkdir(parents=True, exist_ok=True)
	save_metrics(metrics["report"], metrics["accuracy"], metrics_path)

	confusion_matrix_path = Path(confusion_matrix_path)
	confusion_matrix_path.parent.mkdir(parents=True, exist_ok=True)
	plot_confusion_matrix(metrics["confusion_matrix"], ["human", "generated"], confusion_matrix_path)
	load_model_artifacts(force_reload=True, device=device)

	return TrainingArtifacts(
		model_path=output_model_path,
		metrics_path=metrics_path,
		confusion_matrix_path=confusion_matrix_path
	)
