from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from torch import nn

import numpy as np, torch
from transformers import AutoModelForSequenceClassification, get_linear_schedule_with_warmup

from .config import (
	DEFAULT_DATA_PATH,
	NLP_MODEL_NAME,
	NUM_LABELS
)
from .data import create_dataloaders, prepare_splits
from .evaluation import evaluate_model
from .model_utils import get_device, load_model_artifacts
from .artifacts import RunArtifactPaths, build_run_artifact_paths, generate_run_name
from .calibration import fit_temperature_scaling
from .analysis import (
	compute_dataset_stats,
	compute_length_bucket_metrics,
)
from .reporting import (
	plot_confusion_matrix,
	save_dataset_stats,
	save_fails,
	save_length_metrics,
	save_metrics,
	save_params,
	save_calibration_metadata,
)

@dataclass
class TrainingArtifacts:
	run_name: str
	model_path: Path
	metrics_path: Path
	confusion_matrix_path: Path
	params_path: Path
	dataset_stats_path: Path
	length_metrics_path: Path
	report_dir: Path
	fails_path: Optional[Path]
	calibration_path: Path
	calibration_metrics_path: Path
	temperature: float

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
	calibration_size: float = 0.1,
	random_state: int = 42,
	output_model_path: Path | str | None = None,
	metrics_path: Path | str | None = None,
	confusion_matrix_path: Path | str | None = None,
	run_name: str | None = None
) -> TrainingArtifacts:
	device = get_device()
	tokenizer, _ = load_model_artifacts(force_reload=True, device=device)

	resolved_run_name = run_name or generate_run_name()
	run_paths = build_run_artifact_paths(resolved_run_name)

	model_output_path = Path(output_model_path) if output_model_path is not None else run_paths.model_path
	metrics_output_path = Path(metrics_path) if metrics_path is not None else run_paths.metrics_path
	confusion_output_path = Path(confusion_matrix_path) if confusion_matrix_path is not None else run_paths.confusion_matrix_path

	for parent in {model_output_path.parent, metrics_output_path.parent, confusion_output_path.parent}:
		parent.mkdir(parents=True, exist_ok=True)

	train_frame, calibration_frame, test_frame = prepare_splits(
		data_path,
		test_size=test_size,
		calibration_size=calibration_size,
		random_state=random_state
	)
	train_loader, calibration_loader, test_loader = create_dataloaders(
		train_frame,
		calibration_frame,
		test_frame,
		tokenizer,
		max_length=max_length,
		batch_size=batch_size
	)
	dataset_stats = compute_dataset_stats(train_frame, test_frame)

	model = AutoModelForSequenceClassification.from_pretrained(NLP_MODEL_NAME, num_labels=NUM_LABELS)
	model.to(device)

	label_smoothing_factor=0.2
	loss_fn = nn.CrossEntropyLoss(label_smoothing=label_smoothing_factor)

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
				# labels=batch["labels"]
			)
			logits = outputs.logits
			loss = loss_fn(logits, batch["labels"])

			loss.backward()
			torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
			optimizer.step()
			scheduler.step()
			optimizer.zero_grad()
			epoch_losses.append(loss.item())

		avg_loss = float(np.mean(epoch_losses)) if epoch_losses else 0.0
		print(f"Epoch {epoch + 1}/{epochs} — training loss: {avg_loss:.4f}")

	calibration_outcome = fit_temperature_scaling(model, calibration_loader, device=device)
	temperature = calibration_outcome.temperature
	setattr(model, "_factify_temperature", temperature)
	metrics = evaluate_model(model, test_loader, device=device, temperature=temperature)
	torch.save({
		"model_state_dict": model.state_dict(),
		"temperature": temperature
	}, model_output_path)
	save_metrics(metrics["report"], metrics["accuracy"], metrics_output_path)
	plot_confusion_matrix(metrics["confusion_matrix"], ["human", "generated"], confusion_output_path)
	save_dataset_stats(dataset_stats, run_paths.dataset_stats_path)
	length_metrics = compute_length_bucket_metrics(metrics.get("records", []))
	save_length_metrics(length_metrics, run_paths.length_metrics_path)
	save_calibration_metadata({"temperature": temperature}, run_paths.calibration_path)
	save_calibration_metadata(calibration_outcome.report, run_paths.calibration_metrics_path)
	params_payload = {
		"run_name": resolved_run_name,
		"model_name": NLP_MODEL_NAME,
		"num_labels": NUM_LABELS,
		"hyperparameters": {
			"epochs": epochs,
			"batch_size": batch_size,
			"learning_rate": learning_rate,
			"weight_decay": weight_decay,
			"warmup_ratio": warmup_ratio,
			"max_length": max_length,
			"calibration_size": calibration_size,
		},
		"data": {
			"path": str(Path(data_path)),
			"test_size": test_size,
			"random_state": random_state,
		},
	}
	save_params(params_payload, run_paths.params_path)
	fails_records = [record for record in metrics.get("records", []) if record.get("true_label") != record.get("pred_label")]
	fails_path: Optional[Path] = None
	if fails_records:
		save_fails(fails_records, run_paths.fails_path)
		fails_path = run_paths.fails_path

	load_model_artifacts(model_path=model_output_path, force_reload=True, device=device)

	return TrainingArtifacts(
		run_name=resolved_run_name,
		model_path=model_output_path,
		metrics_path=metrics_output_path,
		confusion_matrix_path=confusion_output_path,
		params_path=run_paths.params_path,
		dataset_stats_path=run_paths.dataset_stats_path,
		length_metrics_path=run_paths.length_metrics_path,
		report_dir=run_paths.report_dir,
		fails_path=fails_path,
		calibration_path=run_paths.calibration_path,
		calibration_metrics_path=run_paths.calibration_metrics_path,
		temperature=temperature
	)
