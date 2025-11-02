# NLP

## 1. Struktura
```
backend/src/nlp/
├── __init__.py            # Wejście CLI (train / evaluate / predict)
├── artifacts/             # Modele, raporty, metryki z treningów
│   ├── models/
│   └── reports/
├── data/                  # Dane treningowe / walidacyjne (CSV)
└── detector/
    ├── analysis.py        # Statystyki datasetu i bucketów długości
    ├── calibration.py     # Kalibracja modelu poprzez temperature scaling
    ├── cli.py             # Implementacja komend CLI
    ├── config.py          # Konfiguracja treningu i ścieżki artefaktów
    ├── data.py            # Ładowanie i podział danych
    ├── evaluation.py      # Metryki oraz raporty walidacyjne
    ├── model_utils.py     # Ładowanie / zapisywanie modeli RoBERTa
    ├── reporting.py       # Generowanie raportów JSON / CSV
    └── training.py        # Pętla treningowa i logika optymalizacji
```

## 2. Wymagania środowiskowe
- Python 3.10+
- `pip install -r backend/src/nlp/detector/requirements.txt`

## 3. Podstawowe komendy CLI
Wszystkie polecenia uruchamiamy z katalogu `backend/src/nlp`:

```bash
python3 __init__.py train --epochs 1 --batch-size 4 --max-length 128
```
- Trening zapisze model w `artifacts/models/` i wygeneruje raporty w `artifacts/reports/`.

```bash
python3 __init__.py evaluate --dataset-path data/validation.csv
```
- Wyświetli metryki walidacyjne i zaktualizuje raporty (accuracy, F1, bucket length).

```bash
python3 __init__.py predict --text "Przykładowy tekst do klasyfikacji"
```
- Zwróci JSON z prawdopodobieństwami klas `ai` / `human`.

## 4. Konfiguracja i artefakty
- Globalne ustawienia (ścieżki, nazwy plików) znajdują się w `detector/config.py`.
- Pliki raportów (np. `metrics.json`, `length_bucket_metrics.json`, `misclassified.csv`) są nadpisywane przy kolejnych uruchomieniach.
- Modele są wersjonowane poprzez nazwę pliku (np. `roberta_finetuned.pt`)