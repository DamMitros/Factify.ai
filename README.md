# Factify.ai

## Table of Contents

- [Rozkład plików](#rozkład-plików)
- [Konfiguracja (.env)](#konfiguracja-env)
- [Uruchamianie i czyszczenie](#uruchamianie-i-czyszczenie)
- [Serwisy](#serwisy)
- [Nawigacja po bazie kodu](#nawigacja-po-bazie-kodu)
- [Zasady prowadzenia repozytorium](#zasady-prowadzenia-repozytorium)

## Rozkład plików

- `backend/`
  - `Dockerfile` - obraz backend'u
  - `src/`
    - `main.py` - punkt startowy aplikacji Flask
    - `config.py` - czyta zmienne środowiskowe i zapisuje je w zmiennych globalnych
    - `routes/` - folder z blueprint'ami (grupami ścieżek)
    - `requirements.txt` - zależności backend'u
- `cron/`
  - `Dockerfile` - obraz cron'a
  - `src/`
    - `main.py`
    - `requirements.txt` - zależności cron'a
- `frontend/`
  - `Dockerfile` - obraz frontend'u
  - `src/`
    - **Projekt Next.js**
- `docker-compose.yaml` - definicje serwisów
- `.env.dist` - szablon do konfiguracji środowiska

> [!IMPORTANT]
> **Stwórz kopię pliku i nazwij ją `.env` (usuwając końcówkę `.dist`).**
> 
> Aplikacja ignoruje plik `.env.dist` i szuka tylko `.env`, które znajduje się w `.gitignore`, 
> aby różnice w konfiguracji nie powodowały konfliktów.

## Konfiguracja (`.env`)

Opisy opcji znajdują się w pliku `.env.dist`. **Większości wartości nie trzeba zmieniać**.


## Uruchamianie i czyszczenie

1. **Uruchomienie z przebudowaniem obrazów:**
    - Wymagane, jeśli zajdą zmiany w plikach `Dockerfile` lub zależnościach (np. po instalowaniu bibliotek).
    ```bash
    docker compose up --build
    ```

2. **Uruchomienie zwykłe:**
    ```bash
    docker compose up
    ```

3. **Wyczyszczenie kontenerów:**
    ```bash
    docker-compose down
    ```

4. **Wyczyszczenie kontenerów i danych w wolumenach (m.in. bazę danych):**
    ```bash
    docker-compose down -v
    ```

## Serwisy:
- `backend`
  - URL: http://localhost:8080
  - **Wspiera _Hot Reload_**, więc małe zmiany nie wymagają restartu kontenera.
- `frontend`
  - URL: http://localhost:8081
  - **Wspiera _Hot Reload_** przez serwer deweloperski Next.js, więc małe zmiany nie wymagają restartu kontenera.
- `cron`
  - Nie jest dostępny z zewnątrz.
  - Odpowiada za wykonywanie dłuższych czynności, aby nie zawieszały backendu.
- `mongodb`:
  - Dostępny pod `localhost:27017` z ustawionym użytkownikiem (domyślnie `factify_ai`) i hasłem


## Nawigacja po bazie kodu

### Backend

- `backend/src/main.py`
  - **Tu aplikacja się uruchamia.**
  - Idealne miejsce na dodawanie nowych/usuwanie niepotrzebnych blueprint'ów.
- `backend/src/config.py`
  - **Tu aplikacja "przepisuje" wartości z .env do łatwo dostępnych zmiennych**.
  - Idealne miejsce na dodawanie nowych zmiennych środowiskowych.
- `backend/src/routes`
  - **Tu znajdują się definicje grup ścieżek.**
  - Idealne miejsce na dodawanie nowych funkcjonalności do backendu.

#### Dodawanie nowego blueprint'u (grupy ścieżek):
1. Utwórz plik w `backend/src/routes`, np. `users.py`:
    ```python
    from flask import Blueprint, jsonify
    
    users_bp = Blueprint("users", __name__)
    
    @users_bp.route("/list", methods=["GET"])
    def list_users():
       return jsonify([{"id": 1, "name": "Alice"}])
    ```

2. Zarejestruj blueprint w `main.py` za pomocą `register_route()`:
    ```python
    from routes.users import users_bp
    
    # ...
    
    register_route("/users", users_bp)
    ```

Teraz `list_users()` jest dostępne przez `<prefix>/users/list` (np. `/api/users/list`).


## Zasady prowadzenia repozytorium

Na gałęzi `master` zawsze powinien znajdować się działający kod.

Wszystkie zmiany powinny być rozpoczynane na nowych gałęziach:
- Nowe funkcjonalności powinny być pisane na gałęziach z prefiksem `feature/` (np. `feature/image-recognition`)
- Wyizolowane poprawki błędów powinny być pisane na gałęziach z prefiksem `fix/` (np. `fix/upload-bug`)

Po zakończeniu pracy na swojej gałęzi należy:
- Wykonać ostatniego commit'a i push'a (`git commit` i `git push`)
- Zebrać zmiany z głównej gałęzi (`git fetch origin master`)
- Wykonać merge z głównej gałęzi do swojej (`git merge origin/master`)
  - Jeżeli pojawią się konflikty, to znaczy, że w trakcie naszej pracy, ktoś inny wprowadził zmiany w tych samych miejscach co my. **Należy je naprawić, usuwając nieaktualne wersje kodu i zostawiając tylko te ostateczne.**
- _(Jeżeli trzeba było rozwiązać konflikty):_ Wykonać push'a, który wrzuci poprawki do repozytorium. (`git push`)

Teraz można stworzyć Pull Request na GitHub'ie, który złączy zmiany z naszej gałęzi do głównej.

Jeżeli po sprawdzeniu wszystkiego po raz ostatni, wprowadzone zmiany działają zgodnie z oczekiwaniami, 
to nie czekamy na potwierdzenie i potwierdzamy Pull Request'a samemu.

### Nie usuwamy gałęzi z Pull Request'a, po wykonaniu merge'a.
