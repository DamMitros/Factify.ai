import argparse, json, time
from pathlib import Path

from .evaluation import evaluate_saved_model, predict_proba
from .training import train_model
from .config import (
	DEFAULT_CONFUSION_MATRIX_PATH,
	DEFAULT_DATA_PATH,
	DEFAULT_METRICS_PATH,
	DEFAULT_MODEL_PATH
)

def _cli_train(args: argparse.Namespace) -> None:
	start_time = time.time()
	artifacts = train_model(
		data_path=args.data_path,
		epochs=args.epochs,
		batch_size=args.batch_size,
		learning_rate=args.learning_rate,
		weight_decay=args.weight_decay,
		warmup_ratio=args.warmup_ratio,
		max_length=args.max_length,
		test_size=args.test_size,
		random_state=args.random_state,
		output_model_path=args.output_model_path,
		metrics_path=args.metrics_path,
		confusion_matrix_path=args.confusion_matrix_path
	)
	training_duration = time.time() - start_time
	print(f"Training finished after {training_duration:.2f} seconds. Artifacts saved to:")
	print(f"  - model: {artifacts.model_path}")
	print(f"  - metrics: {artifacts.metrics_path}")
	print(f"  - confusion matrix: {artifacts.confusion_matrix_path}")

def _cli_evaluate(args: argparse.Namespace) -> None:
	metrics = evaluate_saved_model(
		data_path=args.data_path,
		model_path=args.model_path,
		batch_size=args.batch_size,
		max_length=args.max_length,
		sample_size=args.sample_size,
		random_state=args.random_state
	)

	print(json.dumps(
	{
		"loss": metrics["loss"],
		"accuracy": metrics["accuracy"],
		"report": metrics["report"],
		"confusion_matrix": metrics["confusion_matrix"].tolist(),
	}, indent=2))

def _cli_predict(args: argparse.Namespace) -> None:
	probability = predict_proba(args.text, model_path=args.model_path)
	print(json.dumps({
		"text": args.text,
		"ai_probability": probability,
		"human_probability": 1 - probability,
	}, indent=2))

def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="NLP pipeline utilities")
	parser.add_argument("command", choices=["train", "evaluate", "predict"], help="Operation to perform")
	parser.add_argument("--data-path", default=DEFAULT_DATA_PATH, type=Path, help="Ścieżka do zbioru danych")
	parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH, type=Path, help="Ścieżka do modelu")
	parser.add_argument("--output-model-path", default=DEFAULT_MODEL_PATH, type=Path, help="Ścieżka zapisu nowego modelu (tylko train)")
	parser.add_argument("--metrics-path", default=DEFAULT_METRICS_PATH, type=Path, help="Ścieżka do metryk")
	parser.add_argument("--confusion-matrix-path", default=DEFAULT_CONFUSION_MATRIX_PATH, type=Path, help="Ścieżka do wykresu macierzy pomyłek")
	parser.add_argument("--epochs", type=int, default=3, help="Liczba epok treningowych")
	parser.add_argument("--batch-size", type=int, default=16, help="Rozmiar batcha")
	parser.add_argument("--learning-rate", type=float, default=2e-5, help="Współczynnik uczenia")
	parser.add_argument("--weight-decay", type=float, default=0.01, help="Weight decay")
	parser.add_argument("--warmup-ratio", type=float, default=0.1, help="Odsetek kroków przeznaczony na warmup")
	parser.add_argument("--max-length", type=int, default=512, help="Maksymalna długość sekwencji")
	parser.add_argument("--test-size", type=float, default=0.2, help="Proporcja zbioru testowego podczas treningu")
	parser.add_argument("--random-state", type=int, default=42, help="Seed podziału danych")
	parser.add_argument("--sample-size", type=float, default=None, help="Proporcja danych używanych do ewaluacji (tylko evaluate)")
	parser.add_argument("--text", type=str, help="Tekst do predykcji (tylko predict)")
	return parser

def dispatch_cli(args: argparse.Namespace) -> None:
	command = args.command
	if command == "train":
		_cli_train(args)
	elif command == "evaluate":
		_cli_evaluate(args)
	elif command == "predict":
		if not args.text:
			raise ValueError("Provide --text for predict command")
		_cli_predict(args)
	else:
		raise ValueError(f"Unknown command: {command}")

def main(argv: list[str] | None = None) -> None:
	parser = build_parser()
	args = parser.parse_args(argv)
	dispatch_cli(args)
