# Status (23.11.2025)

## Założenie 
Głównym pomysłem jest zaimplementowania dynamiczniejszej mechaniki w `chunking.py`, tak aby model mógl bardziej logiczniej i sensowniej predyktować przy pełnych zdaniach, zamiast uciętych losowo fragmentów. Do tego planowane jest stworzenie niezależnej mechaniki odczytywania tekstu z plików - dorobienie nowego API, umożliwiające predykcje z pliku.

## Realizacje 

Stara mechanika dzielenie na segmenty została w zasadzie całkowicie zmodyfikowana we fragmentach. Zamiast sztywnego cięcia tekstu co określoną liczbę słów, wprowadzono mechanizm poszukiwania granic zdań. Algorytm iteruje po słowach i w zdefiniowanym oknie poszukiwań (wokół docelowej długości fragmentu) stara się znaleźć znak kończący zdanie (`.!?`). Dzięki temu segmenty są bardziej spójne semantycznie i rzadziej ucinane w połowie myśli.

Dorobiono nowy moduł `text_extractor.py` odpowiadający za wczytanie tekstu z pliku z formatów: `.pdf`, `.docx`, `.txt`, `.csv`, `.json`, `.log`, `.md`, `.xml`. Do tego przerobiono mechaniki w `routes/nlp.py` - dodano dwa helpery (`helper_to_predict`, `helper_to_save_into_db`) porządkujące logikę predykcji i zapisu do bazy, oraz nowy routing (`predict_file`) do odbierania pliku, ekstrakcji jego treści i wykonania na niej predykcji.

## Wnioski

Sam model sensowniej dzieli fragmenty, stara się jak najbardziej aby segment kończył się wraz z końcem zdania. Extrakcja tekstu z plików działa, co jednak znaczniej wydłuża czas predykcji w porównaniu do zwykłego wysłania jej tekstem. 