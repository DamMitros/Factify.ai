# PRZESTARZAŁY PLIK - używaj detector/config.py
# Ten plik zostanie usunięty w przyszłości
from pathlib import Path
import warnings

warnings.warn(
    "backend/src/image_detection/config.py jest przestarzały. "
    "Używaj detector/config.py zamiast tego.",
    DeprecationWarning,
    stacklevel=2
)