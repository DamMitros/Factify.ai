# Status modelu NLP (02.11.2025)

## Postępy

Aby zrealizować cel z poprzedniego statusu - zdyfersyfikować pulę odpowiedzi dodałem dodatkową warstwę w treningu jaką jest kalibracja prawdopodobieństw. Do tego trzeba było:
- rozbudować podział danych o dodatkową część (validation), dzięki czemu dzielimy dataset na 3 trzy elementy train/validation/test,
- zaimplementowano moduł `calibration.py`, którzy korzystać z temperature scaling dopasowuje parametr na podstawie walidacji,
- zaktualizowano proces treningu tak, aby zapisywać wagi modelu razem z temperaturą i statystykami kalibracji.
- dostosowano ewaluację i predykcję (`evaluate_model`, `predict_proba`), aby raportowały skalibrowane prawdopobieństwa.

## Problemy 

Model przy zwiększonej liczbie epok i zaimplmentowanej nowej funkcji wykazał się jeszcze lepszą poprawnością odpowiedzi. Na 5801 poprawnie sklasyfikowanych przypadków tylko 28 było niepoprawnie jednak mimo kalibracji wyniki dalej są skrajnie mylne. 26 z nich zostało określonych jako "generated" kiedy powinny być "human writen", tylko 2 błędne przypadki było odwrotne. Zmiany nie przyniosły oczekiwanych efektów i model w dalszym przypadku określa:
- w 13 przypadkach wartość zdecydowaną (`0.99`),
- w 9 przypadkach wartość pewną (`0.90<x<0.99`),
- w 6 przypadkach wartość poniżej `0.9`.

## Cele 

Aktualna kalibracja poprzez temperature scalling przyniosła niezadowalające efekty. Potrzebne jest rozbudowanie obecnej kalibracji lub zaimplementowanie innej metody. Można wziąść pod uwagę rozwiązanie hybrydowe, tzn. zachować obecny moduł `calibration.py` i dodać dodatkowy element. 

Obecnie głównym celem nie jest pełna poprawność modelu a obniżenie jego pewności przy odpowiedziach. 
