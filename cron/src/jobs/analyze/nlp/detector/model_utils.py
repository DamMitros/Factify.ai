import platform
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from .config import DEFAULT_MODEL_PATH, NLP_MODEL_NAME

_tokenizer_cache: AutoTokenizer | None = None
_model_cache: AutoModelForSequenceClassification | None = None
_temperature_cache: float | None = None

@contextmanager
def dropout_train_mode(model: torch.nn.Module) -> Iterator[None]:
    dropout_modules: list[torch.nn.Module] = []
    original_states: list[bool] = []
    for module in model.modules():
        if isinstance(module, (torch.nn.Dropout, torch.nn.Dropout1d, torch.nn.Dropout2d, torch.nn.Dropout3d)):
            dropout_modules.append(module)
            original_states.append(module.training)
    for module in dropout_modules:
        module.train(True)
    try:
        yield
    finally:
        for module, state in zip(dropout_modules, original_states):
            module.train(state)

def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
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
        model = AutoModelForSequenceClassification.from_pretrained(NLP_MODEL_NAME, num_labels=2)
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

        is_x86_64 = platform.machine().lower() in ("x86_64", "amd64")

        if device.type=='cpu' and is_x86_64:
            _model_cache = torch.quantization.quantize_dynamic(
                _model_cache,
                {torch.nn.Linear},
                dtype=torch.qint8
            )

        _temperature_cache = temperature
        setattr(_model_cache, "_factify_temperature", temperature)
        _model_cache.eval()
    else:
        if _temperature_cache is not None:
            setattr(_model_cache, "_factify_temperature", _temperature_cache)
        else:
            setattr(_model_cache, "_factify_temperature", 1.0)

    return _tokenizer_cache, _model_cache
