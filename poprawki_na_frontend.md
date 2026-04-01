**/community**
Podłączenie predykcji na `/community` nie działa - endpoint rozdzielony na 2, i tak było to do przebudowy 
Trzeba tam uwzględnić Obrazy, Tekst AI, Manipulacja, Źródła.

**/Admin**
`/admin/overview` - panel trzeba dorobić 2 sloty zrobić go bardziej może gridem w układzie 3x2 (bo w sumie jest 6 statusów)

`/admin/users` - historia usera nie działa/w zasadzie ten sam case co w community

`/text AI` | `/image AI` -- one nie działają -- na razie nie ma endpointów musze je najpierw ogarnąć

`/text history` - endpoint działa ale on jest na chama wrzucony zamiast innego endpointu, przez co wyskakuje błąd

`/image history` - endpoint działa ale on jest na chama wrzucony zamiast innego endpointu, przez co wyskakuje błąd

Cała reszta elementów działa, zmieniłem kilka pierdół logiki

Ogólnie cały admin page to troche ultra mega smelly code