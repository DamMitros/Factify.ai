# Status modelu NLP (01.11.2025)

## Postępy i problemy 

Dodano więcej danych i informacji w trakcie treningu danych. Pierwotnie zwracało:
  - wytrenowany model,
  - metryki,
  - macierz błędów.
  Aby umożliwić dalsze szkolenie modelu, dodano:
  - parametry trenowanego modelu,
  - mediany i ekstrema wprowadzanych danych,
  - statystyki wpływu długości tekstu do ilości błedu,
  - plik CSV z błędnie zdeterminowanymi tekstami (wraz ze szczegółami technicznymi).

## Wnioski z nowych danych 

Model wykazał się ponownie dobrą dokładnością, ale nowe dane umożliwiły pokazać znaczny problem. Model zwraca odpowiedzi praktycznie jednoznaczne, co jest szczególnie problematyczne przy błędnie zdeterminowanych odpowiedzi. 

Na ten moment bazując na danych z `length_bucket_metrics.json` zakładam, że nie ma znaczenia długość tekstu, który dostaje model. Pierwotnie zakładałem, że tutaj jest problem.

## Cele 
 
Model musi mieć bardziej zdyfersyfikoną pulę odpowiedzi - ma przestać przypominać system binarny. Przetestować na ile wpłynie to na jakość odpowiedzi. 

Jeśli jakość odpowiedzi się polepszy warto wrócić sprawdzić wiarygodność danych `length_bucket_metrics.json`, poprzez testowanie kilku tekstów bazując na stopniowo zwiększającym się limicie znaków.
