from pathlib import Path
from typing import Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from .config import DEFAULT_MODEL_PATH, NLP_MODEL_NAME, NUM_LABELS

_tokenizer_cache: AutoTokenizer | None = None
_model_cache: AutoModelForSequenceClassification | None = None

def get_device() -> torch.device:
	if torch.cuda.is_available():
		return torch.device("cuda")
	return torch.device("cpu")

def load_model_artifacts(model_path: Path | str = DEFAULT_MODEL_PATH, *,
												force_reload: bool = False, device: torch.device | None = None
												) -> Tuple[AutoTokenizer, AutoModelForSequenceClassification]:
	global _tokenizer_cache, _model_cache

	resolved_model_path = Path(model_path)
	if device is None:
		device = get_device()

	if force_reload:
		_tokenizer_cache = None
		_model_cache = None

	if _tokenizer_cache is None:
		_tokenizer_cache = AutoTokenizer.from_pretrained(NLP_MODEL_NAME)

	if _model_cache is None:
		model = AutoModelForSequenceClassification.from_pretrained(
			NLP_MODEL_NAME, num_labels=NUM_LABELS
		)
		if resolved_model_path.exists():
			state_dict = torch.load(resolved_model_path, map_location=device)
			model.load_state_dict(state_dict)
		_model_cache = model.to(device)
		_model_cache.eval()

	return _tokenizer_cache, _model_cache
