from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .config import MODEL_DIR, REPORT_DIR

@dataclass(slots=True)
class RunArtifactPaths:
	run_name: str
	model_path: Path
	report_dir: Path
	metrics_path: Path
	confusion_matrix_path: Path
	params_path: Path
	fails_path: Path
	dataset_stats_path: Path
	length_metrics_path: Path
	calibration_path: Path
	calibration_metrics_path: Path

	def ensure_directories(self) -> None:
		self.report_dir.mkdir(parents=True, exist_ok=True)
		self.model_path.parent.mkdir(parents=True, exist_ok=True)

def generate_run_name(prefix: str = "roberta_finetuned", timestamp: datetime | None = None) -> str:
	timestamp = timestamp or datetime.now()
	return f"{prefix}_{timestamp.strftime('%Y%m%d')}"

def build_run_artifact_paths(run_name: str, *, ensure_dirs: bool = True) -> RunArtifactPaths:
	report_dir = REPORT_DIR / run_name
	paths = RunArtifactPaths(
		run_name=run_name,
		model_path=MODEL_DIR / f"{run_name}.pt",
		report_dir=report_dir,
		metrics_path=report_dir / "metrics.json",
		confusion_matrix_path=report_dir / "confusion_matrix.png",
		params_path=report_dir / "params.json",
		fails_path=report_dir / "fails.csv",
		dataset_stats_path=report_dir / "dataset_stats.json",
		length_metrics_path=report_dir / "length_bucket_metrics.json",
		calibration_path=report_dir / "calibration.json",
		calibration_metrics_path=report_dir / "calibration_metrics.json"
	)

	if ensure_dirs:
		paths.ensure_directories()

	return paths
