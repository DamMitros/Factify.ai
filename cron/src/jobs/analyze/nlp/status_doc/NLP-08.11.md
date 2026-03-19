# Status modelu (08.11.2025)

## Problematyka

Aby poprawić jakość odpowiedzi, zaplanowane zostało zaimplementowanie Monte Carlo Dropout. Ma on na cele lepiej zdeterminować wiarygodność decyzyjną modelu i większe zaakcentować elementów, w których model rzeczywiście nie ma przekonania. Zaimplementowanie metody musi być odwracalne aby dalej móc badać stare modele. 

### Monte Carlo Dropout (MCD)

"The Monte Carlo Dropout technique, as introduced by Gal and Ghahramani in 2016, involves estimation of uncertainty in predictions made by models. By applying dropout at test time and running multiple forward passes with different dropout masks, the model produces a distribution of predictions rather than a single point estimate. This distribution provides insights into the model's uncertainty about its predictions, effectively regularizing the network." 
~ (źródło: https://www.geeksforgeeks.org/deep-learning/what-is-monte-carlo-mc-dropout/)

Z tego wynika, że Monte Carlo Dropout jest techniką, która używa dla tego samego przykładu kilka różnych masek z których fragment sieci neuronowej jest "wycięty". Następnie tworzy anm to zbiór wielu predykcji, pozwalających stwierdzić na ile rzeczywiście model jest zdeterminowany o poprawności wyniku swojej analizy.

## Implementacja 

Przede wszystkim rozbudowaną ewaluację modelu, która odbywa się już po wytrenowaniu modelu. `evaluation.py` przerobiono tak, aby zachować starą logikę pojedynczego przepuszczenia danych przez model (kiedy MC Dropout jest wyłączone), a jednocześnie umożliwiać wielokrotne obliczanie predykcji z MC Dropout, gdzie losowo „wycinane” są neurony w sieci. W obu trybach zwracana jest ta sama struktura wyników. Temperature scaling pozostaje bez zmian. 

Do tego wprowadzone drobne zmiany techniczne tzn. dodanie nowych zmiennych w config.py, przepuszczenie ich przez `training.py` do `evaluation.py` oraz dodanie metody umożliwiającej działanie MCD w `model_utils.py`.

Aby wyniki były czytelniejsze dodano nowe parametry do nowych raportów z treningów i rozbudowano informację zwracane przez API.

## Wnioski 

Dla nowej implementacji przetestowano podwójnie model:
- `mc_dropout_train` (label smoothing 0.2), który wykazał się wyjątkowo dobrym wynikiem testowym (błędnie sklasyfikowane 9 błędnych odpowiedzi na 5829), ale dalej powielał pewność siebie przy błędnych odpowiedziach (chociaż było już widać zmiane)
- `mc_dropout_train2` (label smoothing 0.1), który miał minimalnie gorszą klasyfikację błędnych odpowiedzi (13 na 5829) to w końcu w `fails.csv` zobaczyliśmy dużo większą dywersfikację sklasyfikowania modelu. Pokazało nam to też efekt, że model wykazują jawniej swoją niepewność.

## Cele

Obecny dłuższy czas problem pewności siebie modelu można uznać za znacznie zmniejszony. Trzeba przyjrzeć się teraz na ile rzeczywiście wytrenowany model poradzi sobie z nową pulą danych. Warto byłoby zwefikować działanie modelów oraz zbadać czy model rzeczywiście osiągą akceptowalne wyniki. 