# Status modelu (14.11.2025)

## Idea i cel 

Pomysłem na dalszy rozwój modelu jest wymuszenie na nim zwracanie podzielonego na fragmentu inputu, który model zdeterminuje osobno na ile uważa wykorzystanie, użycia AI. Wszystkie podzielone elementy wspólnie powinny przez średnią ważoną zdeterminować wynik ogólny. Model więc zarówno przez CLI i API będzie zwracać wyniki `Overall` i `segments: index`. Jednym z powodów takiej implementacji jest szkolenie modelu na max-length=128 tokenów, która powoduje, że model pierwotnie i tak uczył się i dokonywał predykcji tylko na pierwszych 128 tokenów tekstu.

## Realizacja 

- Dodano nowy moduł `dector/chunking.py` odpowiadający za odpowiednie wyważenie proporcji i segmentów, tak aby były one równomierne.
- Znacznie rozbudowano moduł `detector/evaluation.py`, który implementuje przede wszystkim nowy rodzaj predykcji, z podzielonymi sekcjami i zwracaną średnią ważoną z wyników tych sekcji jako wynik ogólny.Dodatkowo zachowana została orginalna pojedyńcza mechanika.
- Endpoint CLI (`python3 __init__.py predict`) ma teraz flagę `--detailed` oraz parametry segmentacji i potrafi zwracać szczegółową strukturę segmentów lub jeden ogólny klasyczny wynik.
- Endpoint `/predict` w API domyślnie zwraca strukturę segmentową (`detailed` domyślnie `true`). Aby wymusić tryb klasyczny, JSON powinien przyjąć formę:
```json
{
  "text": "{tekst}",
  "detailed": false
}
```
- Nowe parametry uwzględniono w `detector/config.py`.

## Detale techniczne 

- `detector/evaluation.py` przyszłościowo w zależności od rozwoju aplikacji będzie możliwe wzięcie pod uwagę rozdzielenie tego pliku na 2/3 lub usunięcie części mechanik. Aktualnie kod jest już zbyt długi, co nie tylko utrudnia w modyfikowaniu kodu co również w wykrywaniu i naprawianiu błędów.
- Aktualnie docelowym celem przy dzieleniu na sekcje tekstu jest około ~50 wyrazów. Aktualnie możliwe jest wzięcie pod uwagę mniejszego/większego limitu, który jednak nie może przekroczyć limitu 128 tokenów. 
 
## Efekt końcowy 

Model przy testowaniu za pomocą `python3 __init__.py predict --text "{tekst}" --detailed` wykazał się  oczekiwanym rezultatem. Nie było konieczne usuwanie poprzednio zaimplementowanych elementów a same wyniki zwracany z funkcji są optymistyczne i wyglądają sensownie. 

## Przyszłościowe cele 

Aktualnie można uwzględnić stworzenie zautomatyzowanych testów jakościowych modelu, które mogą uwiarygodność wyniki zwracane przez model. Stworzy nam to odgórne ramy, które model realizuje i zapewni nas, o tym, że model idzie w dobrym kierunku rozwoju. 

Warto też zastanowić się nad stopniowym "odchudzeniem" mechanik lub wydzielenia dla nich osobnych plików.