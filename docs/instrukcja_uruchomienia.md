# Instrukcja uruchomienia MVP NDR

Ten MVP uruchamia backend FastAPI, frontend React/Vite, baze PostgreSQL oraz lokalny symulator ataku. Po symulacji alert powinien byc widoczny w Dashboardzie, Alertach i Logach.

## Wymagania

| Narzedzie | Minimalnie |
|-----------|------------|
| Python | 3.10+ |
| Node.js | 18+ |
| npm | 9+ |
| Docker Desktop | do startu przez `docker compose` |
| PostgreSQL | tylko przy starcie lokalnym bez Dockera |

## Szybki start przez Docker

Z katalogu glownego repo:

```powershell
docker compose up --build
```

Uslugi:

| Usluga | Adres |
|--------|-------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |

Backend wykonuje `alembic upgrade head` przy starcie kontenera. Dane demo sa tworzone automatycznie po starcie backendu:

| Typ | Wartosc |
|-----|---------|
| Uzytkownik | `demo@example.local` |
| Haslo | `demo1234` |
| Sensor | `local-demo-sensor` |
| Reguly | `Port Scan`, `SSH Brute Force`, `Blacklist IP` |

## Start lokalny bez Dockera

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python run.py
```

Plik `backend/.env` powinien zawierac:

```env
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DB_URL=postgresql+psycopg://postgres:haslo@localhost:5432/ndr
DEBUG=true
```

Przed migracjami utworz pusta baze `ndr`, jesli nie istnieje.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Plik `frontend/.env` dla pracy z backendem:

```env
VITE_USE_MOCK=false
VITE_API_BASE_URL=
```

Vite proxy przekazuje `/api/*` do `http://localhost:8000`.

## Symulacja lokalnego ataku

Po starcie backendu uruchom z katalogu glownego repo:

```powershell
python scripts/simulate_attack.py --type port-scan
python scripts/simulate_attack.py --type ssh-bruteforce
python scripts/simulate_attack.py --type blacklist
```

Skrypt wysyla logi tylko do lokalnego endpointu:

```text
http://localhost:8000/api/ingest/logs
```

Oczekiwany efekt:

1. `POST /api/ingest/logs` zapisuje rekord w `network_logs`.
2. `detection_engine.py` sprawdza aktywne reguly.
3. Pasujaca regula tworzy rekord w `alerts`.
4. Frontend pokazuje wyzsze liczniki dashboardu, nowy alert i nowe logi.

## Tryb mock frontendu

Do pracy tylko nad UI mozna ustawic:

```env
VITE_USE_MOCK=true
```

W trybie MVP i symulacji ataku ta flaga musi byc `false`, bo inaczej frontend pokazuje dane mockowe.

## Czeste problemy

### Backend nie laczy sie z baza

Sprawdz, czy PostgreSQL dziala i czy `DB_URL` wskazuje poprawny host:

| Tryb | Host w `DB_URL` |
|------|-----------------|
| lokalny backend | `localhost` |
| backend w Docker Compose | `postgres` |

### Frontend nie pokazuje alertu po symulacji

Sprawdz `frontend/.env`. Dla pelnego flow musi byc:

```env
VITE_USE_MOCK=false
```

Potem odswiez strone i zaloguj sie kontem `demo@example.local` / `demo1234`.
