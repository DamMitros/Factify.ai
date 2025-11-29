# Podejście do testów funkcjonalnych i integracyjnych (NLP-Tests1)

Głównym celem tych testów jest zapewnienie, że model ładuje się poprawnie, spełnia kontrakt interfejsu oraz wykonuje podstawowe predykcje na referencyjnych zbiorach danych bez błędów krytycznych. Badają one podstawowe funkcjonalności oraz poprawności integracji modelu NLP w projekcie. Testy te znajdują się w katalogu `backend/src/nlp/tests/` (z wyłączeniem podkatalogu `quality_tests`).

## 1. Testy Infrastruktury i Ładowania Modelu
**Plik:** `test_model_loading.py`

Te testy weryfikują, czy środowisko jest poprawnie przygotowane do uruchomienia modelu. Sprawdzają fizyczną obecność plików i strukturę katalogów.

*   **Obecność pliku modelu:** Weryfikacja, czy plik modelu istnieje w oczekiwanej ścieżce.
*   **Poprawność formatu:** Sprawdzenie rozszerzenia pliku (oczekiwane `.pt`).
*   **Integralność pliku:** Upewnienie się, że plik nie jest pusty i ma sensowny rozmiar (np. > 100MB), co eliminuje błędy pobierania.
*   **Struktura artefaktów:** Weryfikacja istnienia wymaganych katalogów pomocniczych (`artifacts/models`, `artifacts/reports`).

## 2. Testy Interfejsu Modelu (Kontrakt)
**Plik:** `test_model_interference.py`

Te testy sprawdzają, czy załadowany model zachowuje się zgodnie z oczekiwanym kontraktem programistycznym. Nie oceniają jakości predykcji, ale ich formę techniczną.

*   **Kształt wyjścia (Shape):** Weryfikacja, czy model zwraca tensor o oczekiwanych wymiarach (np. `(1, 2)` dla klasyfikacji binarnej).
*   **Typ danych:** Sprawdzenie, czy zwracane logity są typu `torch.float32` i są tensorami PyTorch.
*   **Obsługa wejścia:** Pośrednio testuje, czy tokenizacja i przekazywanie danych do modelu nie powoduje wyjątków.

## 3. Smoke Testing i Poprawność Predykcji
**Pliki:** `test_model_predictions_human.py`, `test_model_predictions_mix.py`

Te testy służą jako "dymne testy" (smoke tests) poprawności działania modelu na rzeczywistych danych. Sprawdzają, czy model nie "wykłada się" na danych i czy jego predykcje nie są całkowicie losowe.

*   **Testy na danych ludzkich (`test_model_predictions_human.py`):**
    *   Wykorzystuje zbiór `Shuffled_Human.csv`.
    *   Losuje próbkę (np. 300 tekstów) i sprawdza, czy model klasyfikuje je jako klasę "Human" (0).
    *   Służy do szybkiego wykrycia regresji w rozpoznawaniu tekstów naturalnych.

*   **Testy na danych mieszanych (`test_model_predictions_mix.py`):**
    *   Wykorzystuje zbiór `AI_Human.csv`.
    *   Weryfikuje zgodność predykcji z etykietą (`generated`) dla wylosowanej próbki danych.
    *   Sprawdza ogólną zdolność modelu do rozróżniania klas na znanych próbkach.

## Podsumowanie
Podejście "NLP-Tests1" skupia się na **stabilności technicznej**. Odpowiada na pytania: "Czy model działa?", "Czy pliki są na miejscu?", "Czy interfejs jest zgodny?". Jest to pierwsza linia obrony przed wdrożeniem uszkodzonego systemu.
