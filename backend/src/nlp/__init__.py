import sys
from pathlib import Path

if __package__ in (None, ""):
  sys.path.append(str(Path(__file__).resolve().parents[1]))

from nlp.detector.cli import build_parser as _build_parser
from nlp.detector.cli import dispatch_cli as _dispatch_cli
from nlp.detector.cli import main
from nlp.detector.config import (
    DEFAULT_DATA_PATH,
    DEFAULT_MODEL_PATH,
    NLP_MODEL_NAME
)
from nlp.detector.data import EssayDataset, create_dataloaders as _create_dataloaders, prepare_splits as _prepare_splits
from nlp.detector.evaluation import evaluate_model, evaluate_saved_model
from nlp.detector.inference import predict_proba, predict_segmented_text
from nlp.detector.model_utils import get_device as _device, load_model_artifacts
from nlp.detector.reporting import plot_confusion_matrix as _plot_confusion_matrix, save_metrics as _save_metrics
from nlp.detector.training import TrainingArtifacts, train_model

__all__ = [
  "DEFAULT_DATA_PATH",
  "DEFAULT_MODEL_PATH",
  "EssayDataset",
  "TrainingArtifacts",
  "evaluate_model",
  "evaluate_saved_model",
  "load_model_artifacts",
  "main",
  "predict_proba",
  "predict_segmented_text",
  "train_model"
]

if __name__ == "__main__":
  main()
