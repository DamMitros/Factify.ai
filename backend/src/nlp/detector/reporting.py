import json
from pathlib import Path
from typing import Dict, Iterable

import matplotlib.pyplot as plt
import numpy as np

def plot_confusion_matrix(cm: np.ndarray, labels: Iterable[str], output_path: Path) -> None:
	fig, ax = plt.subplots(figsize=(6, 6))
	image = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
	ax.figure.colorbar(image, ax=ax)
	tick_marks = np.arange(len(labels))
	ax.set_xticks(tick_marks, labels, rotation=45, ha="right")
	ax.set_yticks(tick_marks, labels)
	ax.set_ylabel("True label")
	ax.set_xlabel("Predicted label")
	ax.set_title("Confusion matrix")

	thresh = cm.max() / 2.0 if cm.size else 0
	for i in range(cm.shape[0]):
		for j in range(cm.shape[1]):
			ax.text(
				j,
				i,
				format(cm[i, j], "d"),
				ha="center",
				va="center",
				color="white" if cm[i, j] > thresh else "black"
			)

	fig.tight_layout()
	fig.savefig(output_path, dpi=200, bbox_inches="tight")
	plt.close(fig)

def save_metrics(report: Dict[str, Dict[str, float]], accuracy: float, output_path: Path) -> None:
	payload = {
		"accuracy": accuracy,
		"macro_avg": report.get("macro avg", {}),
		"weighted_avg": report.get("weighted avg", {}),
		"per_class": {k: v for k, v in report.items() if k not in {"accuracy", "macro avg", "weighted avg"}}
	}
	with output_path.open("w", encoding="utf-8") as handle:
		json.dump(payload, handle, indent=2)
