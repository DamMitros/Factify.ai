# Status modelu (07.11.2025)

## Problematyka

Głównym założeniem jest ostateczne zbicie pewnoście siebie w modelu roBERTa. Zastosowane poprzednio temperature_scalling pozostanie, ale zostaną dodane nowe elementy. Na początku sprobowane zostanie dodanie Label smoothing. Jeśli to nie przyniesie skutków będe kolejno próbować regulacje parametrów modelu i upewnienie się, żeby model nie przeuczał się.

### Czym jest Label smoothing?

"Label smoothing is applied while training and focuses on increasing entropy of predicted values thereby reducing the over-confident events." 
~ (źródło: https://www.reddit.com/r/MachineLearning/comments/otop33/comment/h6yky1u/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button)

Oznacza to, że w trakcie treningu zostanie dodany nowy element modyfikujący sposób obliczania straty (loss), co powinno zmniejszyć pewność siebie modelu i zwiększyć entropię(miara niepewności rozkładu) jego przewidywań.

## Implementacja label smoothing

Był to niewielki element dodania kilku linijek w `training.py`, w których przede wszystkim zanim zwrócimy je w każdym batchu (mniejszym elemencie train setu) i zamiast zwracać wynik automatycznie do modelu -- obliczamy samodzielnie strate (loss).

## Wnioski

Co ciekawe drobny label smoothing poprawił wynik zwracany przez model, jednak zaczął on wykazywać bardziej niepewność nijeżeli pewność siebie, którą temperature scaling zaczął sztucznie zwiększać. Jest to niespodziewany ale pozytywyny efekt. Przy zwiększeniu label smoothing po raz drugi model zaczął być niepewny i niewłaściwie klasyfikować oznacza to, że pierwotna wartość 0.1 była bliższa właściwej wartości. Być może należy będzie przyszłościowo wziąść pod uwagę ważenie błędów w trakcie kalibracji, co jednak naturalnie zmniejszy wynik w poprawnych odpowiedziach.

## Możliwe rozwiązania

Pierwszym rozwiązaniem, które automatycznie przychodzi do głowy to drobne dostrojenie parametrów modelu. Co ma jednak bardzo dużą wade jaką jest każdorazowy czas treningu.

Drugim rozwiązaniem jest dostanie kilku prawdopodobieństw. Mogłoby być to zrealizowane przy pocięciu tekstu na konkretne fragmenty i następnie stworzenia średniej. Miałoby to jednak duży negatyw blokujący w dużym stopniu fragmentaryczną determinacje tekstu.

Trzecie rozwiązanie, które ujawniło mi się po poszukaniu problemu w internecie jest Monte Carlo Dropout. Da nam on dokładnie oczekiwany efekt kilku prawdopodobieństw zgodnie z pomysłem z drugiego rozwiązania, ale bez zaburzania przyszłego rozwoju modelu.

Z uwagi na brak czasu, najlepszym rozwiązaniem wydaje się MC Dropout.