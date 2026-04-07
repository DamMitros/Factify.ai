# Dokumentacja Endpointów API (Backend)

Poniżej znajduję się zestawienie głównych endpointów komunikacyjnych w aplikacji. 

---

## Analiza tekstu AI (`/analysis/ai`)

**`POST`** `/analysis/ai`
  * **Opis:** Tworzy nowe zadanie analizy tekstu pod kątem wygenerowania przez AI i dodaje je do kolejki w cronie.
  * **Zwraca:** `taskId` 

**`GET`** `/analysis/ai/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania analizy z cronu na podstawie jego ID.

**`GET`** `/analysis/ai/predictions`
  * **Opis:** Pobiera pełną historię analiz tekstu AI dla aktualnie zalogowanego użytkownika.

**ADMIN REQUIRED** -> endpointy tylko dla admina

**`GET`** `/analysis/ai/predictions/<user_id>` 
  * **Opis:** Odczytuje pełną historię analiz tekstu AI dla wybranego użytkownika.

**`GET`** `/analysis/ai/predictions/all_users`
  * **Opis:** Odczytuje pełną historie dostępnych analiz tekstu AI w bazie danych

---

## Analiza obrazu AI (`/image`)

**`POST`** `/image/detect`
  * **Opis:** Przyjmuje plik ze zdjęciem, koduje go do base64 i tworzy zadanie analizy obrazu AI w cronie. 
  * **Zwraca:** `taskId`

**`GET`** `/image/detect/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania analizy obrazu z cronu.

**`GET`** `/image/predictions`
  * **Opis:** Pobiera pełną historię analiz obrazów AI dla aktualnie zalogowanego użytkownika.

**ADMIN REQUIRED** -> endpointy tylko dla admina

**`GET`** `/image/predictions/<user_id>` 
  * **Opis:** Odczytuje pełną historię analiz obrazów AI dla wybranego użytkownika.

**`GET`** `/image/predictions/all_users`
  * **Opis:** Odczytuje pełną historie dostępnych analiz obrazów AI w bazie danych

---

## Analiza manipulacji (`/analysis/manipulation`)

**`POST`** `/analysis/manipulation`
  * **Opis:** Tworzy zadanie sprawdzające tekst pod kątem manipulacji w cronie.
  * **Zwraca:** `taskId`.

**`GET`** `/analysis/manipulation/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania analizy manipulacji z cronu.

**`GET`** `/analysis/manipulation/predictions`
  * **Opis:** Pobiera pełną historię analiz manipulacji dla aktualnie zalogowanego użytkownika.

**ADMIN REQUIRED** -> endpointy tylko dla admina

**`GET`** `/analysis/manipulation/predictions/<user_id>` 
  * **Opis:** Odczytuje pełną historię analiz manipulacji dla wybranego użytkownika.

**`GET`** `/analysis/manipulation/predictions/all_users`
  * **Opis:** Odczytuje pełną historie dostępnych analiz manipulacji w bazie danych

---

## Wyszukiwanie źródeł (`/analysis/find_sources`)

**`POST`** `/analysis/find_sources`
  * **Opis:** Tworzy zadanie wyszukujące w sieci źródła.
  * **Zwraca:** `taskId`.

**`GET`** `/analysis/find_sources/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania wyszukiwania źródeł z cronu.

**`GET`** `/analysis/find_sources/predictions`
  * **Opis:** Pobiera pełną historię wyszukiwań źródeł dla aktualnie zalogowanego użytkownika.

**ADMIN REQUIRED** -> endpointy tylko dla admina

**`GET`** `/analysis/find_sources/predictions/<user_id>` 
  * **Opis:** Odczytuje pełną historię wyszukiwań źródeł dla wybranego użytkownika.

**`GET`** `/analysis/find_sources/predictions/all_users`
  * **Opis:** Odczytuje pełną historie dostępnych wyszukiwań źródeł w bazie danych

---
## Element społecznośniówki (`/social`)

**`POST`** `/social/feed`
  * **Opis:** Stworzenie postu, w którym można podpiąć analize

**`GET`** `/social/feed`
  * **Opis:** Pobranie z bazy danych posty posortowane po czasie stworzenia

**`DELETE`** `/social/feed/<post_id>`
  * **Opis:** Usunięcie posta [tylko twórca może usunąć post]

**`PUT`** `/social/feed/<post_id>`
  * **Opis:** Edycja posta [tylko twórca może edytować]

**`POST`** `/social/feed/<post_id>/like`
  * **Opis:** Dodanie/Usuniecię like'a (zależne od tego co jest w bazie)

**`POST`** `/social/feed/<post_id>/comment`
  * **Opis:** Dodanie komentarza

**`GET`** `/social/feed/<post_id>/comments`
  * **Opis:** Pobranie komnetarzy do podanego posta 

**`DELETE`** `/social/feed/comments/<comment_id>`
  * **Opis:** Usunięcie wybranego komentarza

**`PUT`** `/social/feed/comments/<comment_id>`
  * **Opis:** Edycja komentarza o podanym ID

**ADMIN REQUIRED** -> endpointy tylko dla admina

**`GET`** `/social/feed/<user_id>/posts`
  * **Opis:** Odczytuje wszystkie posty wybranego użytkownika.

**`GET`** `/social/feed/<user_id>/comments`
  * **Opis:** Odczytuje wszystkie komentarze wybranego użytkownika.

---

## Panel admina (`/admin`) -> wszystkie endpointy tutaj wymagają roli Admin

**`GET`** `/admin/stats` 
  * **Opis:** Odczytuje liczbę użytkowników, wszystkich analiz (każda sekcja osobno), status

**`GET`** `/admin/users`
  * **Opis:** Odczytuje dane użytkownika z bazy danych

**`PUT`** `/admin/users/<user_id>/block`
  * **Opis:** Zablokowanie użytkownika na Keycloaku i zapis w bazie danych

**`DELETE`** `/admin/users/<email>`
  * **Opis:** Usunięcie użytkownika z bazy danych i Keycloacka

**`GET`** `/admin/nlp/reports`
  * **Opis:** Pobiera listę dostępnych raportów szkolenia modelu do analiz tekstu AI

**`GET`** `/admin/nlp/reports/<report_id>`
  * **Opis:** Pobiera wszystkie dostępne dane z wybranego raportów szkolenia modelu do analiz tekstu AI

**`GET`** `/admin/image/reports`
  * **Opis:** Pobiera listę dostępnych raportów szkolenia modelu do analiz obrazu AI

**`GET`** `/admin/image/reports/<report_id>`
  * **Opis:** Pobiera wszystkie dostępne dane z wybranego raportu szkolenia modelu do analiz obrazu AI

--- 

## User skills (`/user`)

**`GET`** `/user/profile`
  * **Opis:** Zczytuje base dane o użytkowniku (username, name, dostępne role itd.)

**`PUT`** `/user/register`
  * **Opis:** Request odpowiadający za aktualizacje danych użytkownika w bazie (oraz jego pierwotne stworzenie)

---

Jeśli jakiekolwiek dane są tutaj błędnie zapisane, to no cóż... tak bywa :3 