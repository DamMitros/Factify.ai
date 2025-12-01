# Podejście do testów jakościowych i wydajnościowych (NLP-Tests-29.11)

Testy mają na celu wykazać **jak dobrze** model działa, czyli testowana jest jakość odpowiedzi modelu NLP w zautomatyzowany sposób - niezależnie od danych, na których był trenowany, walidowany i testowany w etapie szkolenie. Testy znajdują się w katalogu `backend/src/nlp/tests/quality_tests/`. Jest to rozbudowanie pierwotnych testów w katalogu `backend/src/nlp/test/`, które sprawdzały **czy** model działa.

## 1. Testy Dokładności i Metryki (Accuracy)
**Plik:** `test_accuracy.py`

Te testy wyliczają ilościowe miary jakości modelu na zbiorach walidacyjnych.

*   **Metryki:** Obliczanie `accuracy_score` oraz generowanie pełnego raportu klasyfikacji (`classification_report`).
*   **Entropia:** Analiza średniej entropii predykcji, co pozwala ocenić pewność modelu.
*   **Progi akceptacji:** Testy zawierają asercje sprawdzające, czy dokładność przekracza określony próg (np. > 0.8). Jeśli jakość modelu spadnie poniżej tego poziomu, test zakończy się niepowodzeniem.
*   **Zbiory danych:** Wykorzystują dedykowane zbiory testowe (np. `AI Generated Essays Dataset.csv` lub `your_dataset_5000.csv`).

## 2. Testy Spójności i Determinizmu (Consistency)
**Plik:** `test_consistency.py`

Weryfikacja, czy model zachowuje się w sposób przewidywalny i deterministyczny.

*   **Powtarzalność:** Uruchamianie predykcji wielokrotnie dla tego samego wejścia.
*   **Stabilność wyników:** Sprawdzenie, czy prawdopodobieństwa i entropia są identyczne (z dokładnością do błędu zmiennoprzecinkowego) w każdej iteracji. Zapobiega to sytuacjom, gdzie model zwraca losowe wyniki dla tego samego zapytania.

## 3. Testy Odporności (Robustness)
**Plik:** `test_robustness.py`

Sprawdzanie, jak model radzi sobie z zakłóceniami w danych wejściowych, które nie powinny zmieniać klasyfikacji.

*   **Niezmienniczość względem białych znaków:** Weryfikacja, czy dodanie dodatkowych spacji lub tabulatorów nie zmienia znacząco wyniku predykcji.
*   **Odporność na literówki:** Sprawdzenie, czy drobne błędy (np. literówki w słowach) nie powodują zmiany etykiety klasyfikacji (flip label). Gwarantuje to, że model nie jest nadmiernie wrażliwy na szum.

## 4. Zaawansowane Scenariusze i Treści Mieszane
**Plik:** `test_mixed_content.py`

Testowanie zdolności modelu do analizy tekstów hybrydowych, zawierających fragmenty napisane przez człowieka i wygenerowane przez AI.

*   **Segmentacja:** Testowanie funkcji `predict_segmented_text`, która dzieli tekst na fragmenty.
*   **Wykrywanie hybryd:** Konstruowanie sztucznych przykładów łączących tekst AI i Human.
*   **Weryfikacja lokalna:** Sprawdzenie, czy model potrafi poprawnie zidentyfikować segmenty o wysokim prawdopodobieństwie bycia AI oraz segmenty o niskim prawdopodobieństwie (Human) w ramach jednego dokumentu.

## Podsumowanie
Podejście "NLP-Tests-29.11" (Quality Tests) skupia się na **jakości merytorycznej i niezawodności**. Odpowiada na pytania: "Jak dokładny jest model?", "Czy jest odporny na błędy użytkownika?", "Czy radzi sobie z trudnymi przypadkami?". Jest to kluczowy etap walidacji przed wdrożeniem modelu na produkcję, zapewniający wysoki standard działania systemu.


## Wnioski 
Model reaguje w dwa różne sposoby w zależności od dobranego datasetu. W przypadku:
- `AI Generated Essays Dataset.csv` - tutaj wyniki mamy świetne model daje radę z każdym wyzwaniem zaprezentowanym w testach. 
- `your_dataset_5000.csv` - tutaj jeden test ma problem, dokładniej `test_accuracy.py` nie daje rady osiągnąć progu. Wynika to najprawdopodbniej z tego, że długość badanych tekstów jest bardzo krótka. Reszta testów realizowana jest bez problemów tak samo jak w `AI Generated Essays Dataset.csv`.
