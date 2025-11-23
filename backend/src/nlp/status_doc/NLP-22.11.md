# Status model (22.11.2025)

## Cel i plan 

Założeniem jest zoptymalizowanie pracy działania modelu, tak aby był stale odpalony na backendzie i był gotowy na przyjmowanie API z frontendu. Do tego zamysłem jest przyspieszenie jego ogólnego działania, wraz z uporządkowaniem jego kodu.

## Realizacja 

Model wczytuje się `backend/src/main.py`, dzięki czemu przy requescie `/predict` funkcja omija załadowanie modelu, a pobiera go z pamięci (_model_cache). W przypadku użycia CPU zastosowano dynamiczne kwantyzowanie (zamiast zapisy float(32)->int(8)) co powinno zaoszczędzić zużycie pamięci RAM i przyśpieszyć działanie na CPU. Usunięte została opcja wyłączenia MC Dropout oraz mniejsze stałe z `backed/src/nlp/detector/config.py`, które w praktyce nie były wykorzystywane. Podzielono moduł `evaluation.py` na dwa - `evaluation.py` i `inference.py`, nowy moduł zajmuje się predykcją. 

Dodano element pobierający bazowy model "RoBERTa", dzięki czemu można prowadzić testy całkowicie bez dostępu do internetu (po pobraniu modelu). 

## Wnioski  

Sam model przyspieszył, dzięki braku potrzeby każdorazowego uruchamiania go. Przy samym uporządkowaniu kodu, pojawił się jednak problem -  
Należy zastanowić się o idei pozostawienie dwóch osobnych funkcji w `inference.py` - predict_proba(...) i predict_segmented_text(...), sam podział wynika z możliwej opcji wyłączenia trybu szczegółowego w API. Jeśli docelowo na frontendzie pozostanie opcja szczegółowa nie będzie potrzeby istnienia dla funkcji predict_proba(...) a będzie wystarczyło przerobić lekko pozostałą funkcję.

## Przyszłościowe cele 

Podjęcie decyzji w sprawie funkcji predict_proba(...) i predict_segmented_text(...) oraz wprowadzenie bardziej dynamicznego zastosowania chunkowania tekstu w przypadku szczegółowych wyników - model aktualnie dzieli je w środkach zdań, co jest nienaturalne przy analizie pełnych tekstów.  

