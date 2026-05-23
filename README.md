# NDR — Network Detection and Response

System do monitorowania ruchu sieciowego, wykrywania anomalii i reagowania na incydenty bezpieczeństwa. Projekt zespołowy realizowany w ramach przedmiotu "Projekt Zespołowy".

## Zespół — First To Win

| Osoba | Rola |
|-------|------|
| Kacper | Project Manager & Frontend Developer |
| Jonasz | Security Engineer (silnik detekcji, OSINT, parsowanie pakietów) |
| Kuba | Security Engineer (scenariusze ataku, red/blue teaming) |
| Bartek | Backend Developer |
| Oskar | Data Analyst (normalizacja logów, statystyki anomalii) |
| Łukasz | Technical Writer & QA |

## Architektura

```
Sensor / Symulator ──► POST /api/ingest/logs (X-Sensor-Key)
                              │
                    detection_engine.py
                              │
                    ┌─────────┴─────────┐
                 NetworkLogs         Alerts (deduplikacja)
                    └─────────┬─────────┘
                          FastAPI REST
                              │
                       React Dashboard
```

**Stack:**

| Warstwa | Technologia |
|---------|-------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy, Alembic |
| Baza danych | PostgreSQL 17 |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Sensor | Python, Scapy (opcjonalnie), symulator HTTP |
| Deployment | Docker Compose |

## Szybki start

```powershell
docker compose up --build -d
```

Usługi po uruchomieniu:

| Usługa | Adres |
|--------|-------|
| Frontend (dashboard) | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger / OpenAPI | http://localhost:8000/docs |
| Healthcheck | http://localhost:8000/api/health |

### Dane logowania demo

| Pole | Wartość |
|------|---------|
| Email | `demo@example.local` |
| Hasło | `demo1234` |
| Klucz sensora | `demo-sensor-key` |

Dane demo (użytkownik, sensor, reguły) są tworzone automatycznie przy starcie backendu.

## Symulacja ataku

Po uruchomieniu stacka wyślij scenariusz demo:

```powershell
# pojedyncze scenariusze
python scripts/simulate_attack.py --type port-scan
python scripts/simulate_attack.py --type ssh-bruteforce
python scripts/simulate_attack.py --type blacklist

# pełne demo end-to-end
python scripts/simulate_attack.py --type full-demo
```

Alerty pojawiają się w dashboardzie automatycznie (auto-refresh co 5 s).

## Tryb live demo

Kontener symulatora wysyła ruch cyklicznie bez ręcznej interwencji:

```powershell
docker compose --profile live up --build -d
```

## Attack Lab (UI)

Zakładka **Attack Lab** w interfejsie pozwala wyzwalać scenariusze bezpośrednio z przeglądarki — bez wychodzenia do terminala. Dostępny tryb automatyczny (co N sekund) i ręczne uruchamianie konkretnych scenariuszy.

## Sprawdzenie przed prezentacją

```powershell
python scripts/smoke_demo.py
```

Skrypt weryfikuje healthcheck, logowanie, dashboard i wzrost liczby alertów po symulacji.

## Testy backendu

```powershell
cd backend
python -m pytest -q
```

## Dokumentacja

| Dokument | Zawartość |
|----------|-----------|
| `docs/architektura.md` | Diagram przepływu, reguły detekcji, kontrakty API |
| `docs/instrukcja_uruchomienia.md` | Szczegółowa instrukcja startu i częste problemy |
| `docs/api.md` | Pełna lista endpointów i modeli danych |
| `docs/scenariusz_prezentacji.md` | Scenariusz 10–15 min demo z komendami |
