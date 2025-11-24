import argparse, json, time
from pathlib import Path

from .evaluation import evaluate_saved_model
from .inference import predict_proba, predict_segmented_text
from .training import train_model
from .config import (
	DEFAULT_DATA_PATH,
	DEFAULT_MODEL_PATH,
	SEGMENT_AI_THRESHOLD,
	SEGMENT_HUMAN_THRESHOLD,
	SEGMENT_MIN_WORDS,
	SEGMENT_STRIDE_WORDS,
	SEGMENT_WORD_TARGET,
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
		calibration_size=args.calibration_size,
		random_state=args.random_state,
		output_model_path=args.output_model_path,
		metrics_path=args.metrics_path,
		confusion_matrix_path=args.confusion_matrix_path,
		run_name=args.run_name
	)
	training_duration = time.time() - start_time
	print(f"Training finished after {training_duration:.2f} seconds. Artifacts saved to:")
	print(f"  - run: {artifacts.run_name}")
	print(f"  - model: {artifacts.model_path}")
	print(f"  - metrics: {artifacts.metrics_path}")
	print(f"  - confusion matrix: {artifacts.confusion_matrix_path}")
	print(f"  - params: {artifacts.params_path}")
	print(f"  - dataset stats: {artifacts.dataset_stats_path}")
	print(f"  - length metrics: {artifacts.length_metrics_path}")
	if artifacts.fails_path:
		print(f"  - fails: {artifacts.fails_path}")
	print(f"  - calibration params: {artifacts.calibration_path}")
	print(f"  - calibration metrics: {artifacts.calibration_metrics_path}")
	print(f"  - fitted temperature: {artifacts.temperature:.4f}")
	print(f"  - report dir: {artifacts.report_dir}")
     
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
	if args.detailed:
		stride_value = args.segment_stride_words
		if stride_value is not None:
			stride_value = int(stride_value)
		result = predict_segmented_text(
			args.text,
			model_path=args.model_path,
			words_per_chunk=args.segment_words_per_chunk,
			stride_words=stride_value,
			min_words=args.segment_min_words,
			max_length=args.segment_max_length,
			ai_threshold=args.segment_ai_threshold,
			human_threshold=args.segment_human_threshold,
		)
		print(json.dumps(result, indent=2, ensure_ascii=False))
		return

	scores = predict_proba(args.text, model_path=args.model_path, return_details=True)
	response = {
		"text": args.text,
		"ai_probability": scores["prob_generated"],
		"human_probability": scores["prob_human"],
		"details": {
			"prob_generated": scores["prob_generated"],
			"prob_generated_std": scores["prob_generated_std"],
			"prob_human": scores["prob_human"],
			"prob_human_std": scores["prob_human_std"],
			"prob_generated_raw": scores["prob_generated_raw"],
			"prob_human_raw": scores["prob_human_raw"],
			"prob_entropy": scores["prob_entropy"],
			"prob_variation_ratio": scores["prob_variation_ratio"],
			"mc_dropout_passes": scores["mc_dropout_passes"],
			"temperature": scores["temperature"],
		},
	}
	print(json.dumps(response, indent=2, ensure_ascii=False))

def build_parser() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(description="NLP pipeline utilities")
	parser.add_argument("command", choices=["train", "evaluate", "predict"], help="Operation to perform")
	parser.add_argument("--data-path", default=DEFAULT_DATA_PATH, type=Path, help="Ścieżka do zbioru danych")
	parser.add_argument("--model-path", default=DEFAULT_MODEL_PATH, type=Path, help="Ścieżka do modelu")
	parser.add_argument("--output-model-path", default=None, type=Path, help="Ścieżka zapisu nowego modelu (tylko train)")
	parser.add_argument("--metrics-path", default=None, type=Path, help="Ścieżka do metryk")
	parser.add_argument("--confusion-matrix-path", default=None, type=Path, help="Ścieżka do wykresu macierzy pomyłek")
	parser.add_argument("--epochs", type=int, default=3, help="Liczba epok treningowych")
	parser.add_argument("--batch-size", type=int, default=16, help="Rozmiar batcha")
	parser.add_argument("--learning-rate", type=float, default=2e-5, help="Współczynnik uczenia")
	parser.add_argument("--weight-decay", type=float, default=0.01, help="Weight decay")
	parser.add_argument("--warmup-ratio", type=float, default=0.1, help="Odsetek kroków przeznaczony na warmup")
	parser.add_argument("--max-length", type=int, default=512, help="Maksymalna długość sekwencji")
	parser.add_argument("--test-size", type=float, default=0.2, help="Proporcja zbioru testowego podczas treningu")
	parser.add_argument("--calibration-size", type=float, default=0.1, help="Proporcja zbioru treningowego wydzielona na kalibrację temperatury")
	parser.add_argument("--random-state", type=int, default=42, help="Seed podziału danych")
	parser.add_argument("--sample-size", type=float, default=None, help="Proporcja danych używanych do ewaluacji (tylko evaluate)")
	parser.add_argument("--text", type=str, help="Tekst do predykcji (tylko predict)")
	parser.add_argument("--run-name", type=str, default=None, help="Prefiks runu. Jeśli brak wygeneruje się dzisiejsza data.")
	parser.add_argument("--detailed", action="store_true", help="Zwróć szczegółowe segmenty podczas predykcji")
	parser.add_argument("--segment-words-per-chunk", type=int, default=SEGMENT_WORD_TARGET, help="Liczba słów w segmencie (predict --detailed)")
	parser.add_argument("--segment-stride-words", type=int, default=SEGMENT_STRIDE_WORDS, help="Krok przesuwny między segmentami (predict --detailed)")
	parser.add_argument("--segment-min-words", type=int, default=SEGMENT_MIN_WORDS, help="Minimalna liczba słów w segmencie (predict --detailed)")
	parser.add_argument("--segment-max-length", type=int, default=128, help="Maksymalna długość tokenów na segment (predict --detailed)")
	parser.add_argument("--segment-ai-threshold", type=float, default=SEGMENT_AI_THRESHOLD, help="Próg uznania segmentu za AI (predict --detailed)")
	parser.add_argument("--segment-human-threshold", type=float, default=SEGMENT_HUMAN_THRESHOLD, help="Próg uznania segmentu za human (predict --detailed)")

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
