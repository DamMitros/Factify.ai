# Image Detection Module

Moduł do wykrywania obrazów wygenerowanych przez AI przy użyciu EfficientNet-B0.

## Struktura

```
image_detection/
├── detector/
│   ├── config.py           # Konfiguracja (ścieżki, transformacje)
│   ├── model_utils.py      # Tworzenie/ładowanie modeli
│   └── inference.py        # Klasa ImageDetector do predykcji
├── artifacts/
│   ├── models/             # Wytrenowane modele .pth
│   └── reports/            # Metryki z treningów
├── data/                   # Dane treningowe (ai/, real/)
├── utils/
│   └── download_model.py   # Skrypt do pobierania modelu z releases
├── training.py             # Skrypt treningowy
└── config.py               # [PRZESTARZAŁY - użyj detector/config.py]
```

## Instalacja modelu

### Opcja 1: Pobieranie z GitHub releases

```bash
python -m backend.src.image_detection.utils.download_model \
  --url https://github.com/USER/REPO/releases/download/v1.0.0/ai_vs_real_best.pth
```

### Opcja 2: Manualne umieszczenie

Umieść plik `ai_vs_real_best.pth` w katalogu:
```
backend/src/image_detection/artifacts/models/
```

## Użycie API

### Endpoint: POST /api/image/detect

Wykrywa czy obraz został wygenerowany przez AI.

**Request:**
```bash
curl -X POST http://localhost:8080/api/image/detect \
  -F "file=@path/to/image.jpg"
```

**Response:**
```json
{
  "filename": "image.jpg",
  "predictions": {
    "ai": 0.8532,
    "real": 0.1468
  },
  "is_ai": true,
  "confidence": 0.8532
}
```

### Endpoint: GET /api/image/health

Sprawdza status modelu.

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

## Użycie w kodzie Python

```python
from image_detection.detector import ImageDetector
from PIL import Image

# Inicjalizacja detektora
detector = ImageDetector()

# Predykcja z pliku
result = detector.predict("path/to/image.jpg")
print(result)  # {'ai': 0.85, 'real': 0.15}

# Predykcja z PIL Image
img = Image.open("image.jpg")
result = detector.predict(img)

# Tylko nazwa klasy
predicted_class = detector.predict_class("image.jpg")
print(predicted_class)  # 'ai' lub 'real'
```

## Trening modelu

```bash
python backend/src/image_detection/training.py
```

Struktura danych treningowych:
```
data/
├── ai/          # Obrazy wygenerowane przez AI
└── real/        # Prawdziwe zdjęcia
```

## Konfiguracja

Edytuj `detector/config.py`:
- `MODEL_NAME`: Nazwa pliku modelu
- `BATCH_SIZE`: Rozmiar batcha
- `EPOCHS`: Liczba epok
- `LEARNING_RATE`: Learning rate
- `DEVICE`: 'cuda' lub 'cpu'

## Zależności

```
torch
torchvision
Pillow
flask
```
