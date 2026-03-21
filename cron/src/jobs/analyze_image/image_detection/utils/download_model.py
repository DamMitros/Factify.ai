"""
Skrypt do pobierania wytrenowanego modelu z GitHub releases.

Użycie:
    python -m backend.src.image_detection.utils.download_model --url <RELEASE_URL>
"""

import urllib.request
import argparse
from pathlib import Path
import sys

# Dodaj parent do path żeby załadować config
sys.path.insert(0, str(Path(__file__).parent.parent))

from detector.config import MODELS_DIR, MODEL_NAME


def download_model(url: str = None):
    """
    Pobiera wytrenowany model z GitHub releases.
    
    Args:
        url: URL do pliku modelu na GitHub releases
    """
    model_path = MODELS_DIR / MODEL_NAME
    
    if model_path.exists():
        print(f"✓ Model już istnieje: {model_path}")
        overwrite = input("Czy chcesz nadpisać? (t/n): ").lower()
        if overwrite != 't':
            print("Anulowano.")
            return
    
    if not url:
        print("BŁĄD: Musisz podać URL do modelu.")
        print("Przykład:")
        print("  python -m backend.src.image_detection.utils.download_model \\")
        print("    --url https://github.com/USER/REPO/releases/download/v1.0.0/ai_vs_real_best.pth")
        return
    
    print(f"Pobieranie modelu z {url}...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        urllib.request.urlretrieve(url, model_path)
        print(f"✓ Model pobrany: {model_path}")
        print(f"  Rozmiar: {model_path.stat().st_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"✗ Błąd podczas pobierania: {e}")
        if model_path.exists():
            model_path.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pobierz model z GitHub releases")
    parser.add_argument(
        "--url",
        type=str,
        help="URL do pliku modelu na GitHub releases"
    )
    args = parser.parse_args()
    
    download_model(args.url)
