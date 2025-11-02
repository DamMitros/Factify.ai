from pathlib import Path
from typing import Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from .config import DEFAULT_MODEL_PATH, NLP_MODEL_NAME, NUM_LABELS

_tokenizer_cache: AutoTokenizer | None = None
_model_cache: AutoModelForSequenceClassification | None = None
_temperature_cache: float | None = None

def get_device() -> torch.device:
	if torch.cuda.is_available():
		return torch.device("cuda")
	return torch.device("cpu")

def load_model_artifacts(
	model_path: Path | str = DEFAULT_MODEL_PATH,
	*,
	force_reload: bool = False,
	device: torch.device | None = None
	) -> Tuple[AutoTokenizer, AutoModelForSequenceClassification]:
	global _tokenizer_cache, _model_cache, _temperature_cache

	resolved_model_path = Path(model_path)
	if device is None:
		device = get_device()

	if force_reload:
		_tokenizer_cache = None
		_model_cache = None
		_temperature_cache = None

	if _tokenizer_cache is None:
		_tokenizer_cache = AutoTokenizer.from_pretrained(NLP_MODEL_NAME)

	if _model_cache is None:
		model = AutoModelForSequenceClassification.from_pretrained(
			NLP_MODEL_NAME, num_labels=NUM_LABELS
		)
		temperature = 1.0
		if resolved_model_path.exists():
			checkpoint = torch.load(resolved_model_path, map_location=device)
			if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
				state_dict = checkpoint["model_state_dict"]
				temperature = float(checkpoint.get("temperature", 1.0))
			else:
				state_dict = checkpoint
			model.load_state_dict(state_dict)
			temperature = max(float(temperature), 1e-3)
		_model_cache = model.to(device)
		_temperature_cache = temperature
		setattr(_model_cache, "_factify_temperature", temperature)
		_model_cache.eval()
	else:
		if _temperature_cache is not None:
			setattr(_model_cache, "_factify_temperature", _temperature_cache)
		else:
			setattr(_model_cache, "_factify_temperature", 1.0)

	return _tokenizer_cache, _model_cache
