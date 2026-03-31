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

---

## Analiza obrazu AI (`/image`)

**`POST`** `/image/detect`
  * **Opis:** Przyjmuje plik ze zdjęciem, koduje go do base64 i tworzy zadanie analizy obrazu AI w cronie. 
  * **Zwraca:** `taskId`

**`GET`** `/image/detect/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania analizy obrazu z cronu.

**`GET`** `/image/predictions`
  * **Opis:** Pobiera pełną historię analiz obrazów AI dla aktualnie zalogowanego użytkownika.

---

## Analiza manipulacji (`/analysis/manipulation`)

**`POST`** `/analysis/manipulation`
  * **Opis:** Tworzy zadanie sprawdzające tekst pod kątem manipulacji w cronie.
  * **Zwraca:** `taskId`.

**`GET`** `/analysis/manipulation/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania analizy manipulacji z cronu.

**`GET`** `/analysis/manipulation/predictions`
  * **Opis:** Pobiera pełną historię analiz manipulacji dla aktualnie zalogowanego użytkownika.

---

## Wyszukiwanie źródeł (`/analysis/find_sources`)

**`POST`** `/analysis/find_sources`
  * **Opis:** Tworzy zadanie wyszukujące w sieci źródła.
  * **Zwraca:** `taskId`.

**`GET`** `/analysis/find_sources/<task_id>`
  * **Opis:** Odczytuje status i wyniki zadania wyszukiwania źródeł z cronu.

**`GET`** `/analysis/find_sources/predictions`
  * **Opis:** Pobiera pełną historię wyszukiwań źródeł dla aktualnie zalogowanego użytkownika.

---

Tutaj kiedyś znajdzie się jeszcze **`/social`** i  **`/admin`** - nie chce mi sie a poza tym i tak jeszcze beda poprawki na adminie 

Endpointy z usera chyba nie ma sensu rozpisywac cnie:???