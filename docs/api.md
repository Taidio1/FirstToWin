# Dokumentacja API - System NDR (Network Detection and Response)

Niniejszy dokument zawiera listę endpointów API wymaganych przez interfejs użytkownika (Frontend) do pełnej funkcjonalności systemu.

## Informacje ogólne
- **Base URL:** `/api`
- **Autoryzacja:** Nagłówek `Authorization: Bearer <token>`
- **Format danych:** JSON

---

## 1. Autoryzacja i Użytkownicy (`/auth`)

### Logowanie
- **Endpoint:** `POST /auth/login`
- **Body:**
  ```json
  {
    "email": "string",
    "password": "string"
  }
  ```
- **Odpowiedź (200 OK):**
  ```json
  {
    "access_token": "string",
    "token_type": "bearer",
    "user": {
      "id": "number",
      "email": "string",
      "username": "string",
      "role": "admin | analyst | viewer",
      "created_at": "ISO8601 String"
    }
  }
  ```

### Rejestracja
- **Endpoint:** `POST /auth/register`
- **Body:** `{ "email": "string", "username": "string", "password": "string" }`
- **Odpowiedź:** Obiekt `User`

---

## 2. Alerty i Detekcja (`/alerts`)

### Lista alertów
- **Endpoint:** `GET /alerts`
- **Query Params:**
  - `page`: numer strony (domyślnie 1)
  - `page_size`: liczba elementów (domyślnie 10/20)
  - `severity`: `critical | high | medium | low | info`
  - `status`: `open | acknowledged | resolved`
  - `q`: fraza wyszukiwania (IP, nazwa reguły)
- **Odpowiedź:** `Paginated<AlertItem>`

### Szczegóły alertu
- **Endpoint:** `GET /alerts/{id}`

### Aktualizacja statusu
- **Endpoint:** `PATCH /alerts/{id}`
- **Body:** `{ "status": "open | acknowledged | resolved" }`

### Threat Intelligence (OSINT)
- **Endpoint:** `GET /alerts/{id}/osint`
- **Opis:** Zwraca dane o złośliwości adresu IP z zewnętrznych baz (AbuseIPDB, VirusTotal itp.).

---

## 3. Dashboard i Statystyki (`/dashboard`)

### Statystyki ogólne
- **Endpoint:** `GET /dashboard/stats`
- **Zwraca dane dla:**
  - Liczników (Alerty 24h, Otwarte krytyczne, Sensory online)
  - Wykresu Severity (kołowy)
  - Wykresu Timeline (liniowy - aktywność w czasie)
  - Listy Top Sources (najczęstsze źródła ataków)

---

## 4. Logi Sieciowe (`/logs`)

### Przeglądarka logów
- **Endpoint:** `GET /logs`
- **Query Params:** `page`, `page_size`, `q`
- **Opis:** Surowe dane o ruchu sieciowym przesłane przez sensory.

---

## 5. Reguły Detekcji (`/rules`)

### Operacje CRUD
- `GET /rules` – Pobranie wszystkich reguł.
- `POST /rules` – Dodanie nowej reguły.
- `PUT /rules/{id}` – Aktualizacja reguły.
- `DELETE /rules/{id}` – Usunięcie reguły.

### Struktura obiektu Rule:
```json
{
  "name": "string",
  "type": "blacklist_ip | connection_threshold | port_scan | protocol_filter",
  "enabled": "boolean",
  "severity": "Severity",
  "match": {
    "src_ip": "string?",
    "dst_ip": "string?",
    "dst_port": "number?",
    "protocol": "TCP | UDP | ICMP | OTHER?",
    "threshold": "number?",
    "window_seconds": "number?"
  },
  "description": "string"
}
```

---

## 6. Sensory (`/sensors`)

### Zarządzanie sensorami
- `GET /sensors` – Lista sensorów i ich status (`online | offline | degraded`).
- `POST /sensors` – Rejestracja nowego sensora (Body: `{ "name": "string", "location": "string" }`).
  - **Ważne:** Zwraca `api_key`, który musi zostać zapisany przez użytkownika.
- `DELETE /sensors/{id}` – Usunięcie sensora.

---

## Modele danych (Typy)

### AlertItem
```typescript
{
  id: number;
  rule_id: number;
  rule_name: string;
  severity: Severity;
  status: AlertStatus;
  src_ip: string;
  dst_ip: string;
  protocol: Protocol;
  sensor_id: string;
  details: string;
  created_at: string;
}
```

### NetworkLog
```typescript
{
  id: number;
  sensor_id: string;
  timestamp: string;
  src_ip: string;
  dst_ip: string;
  src_port: number;
  dst_port: number;
  protocol: Protocol;
  flags: string;
  payload_size: number;
}
```
# Konfiguracja API
Do odpalenia backendu potrzebne są dane środowiskowe w pliku .env:
- DB_URL
- SERVER_HOST
- SERVER_PORT

## Migracje
Aplikowanie migracji (backend project root):
```bash
alembic upgrade head
```

## Aktualne dodatki MVP demo

### Healthcheck

- **Endpoint:** `GET /api/health`
- **Autoryzacja:** brak
- **Odpowiedz:**
  ```json
  {
    "status": "ok",
    "database": "ok",
    "version": "0.0.1-dev"
  }
  ```

### Ingest logow

- **Endpoint:** `POST /api/ingest/logs`
- **Wymagany nagłówek:** `X-Sensor-Key: <klucz-sensora>`
- **Body:**
  ```json
  {
    "sensor_name": "string",
    "src_ip": "string",
    "dst_ip": "string",
    "src_port": "number",
    "dst_port": "number",
    "protocol": "TCP | UDP | ICMP | OTHER",
    "flags": "string",
    "payload_size": "number"
  }
  ```
- **Odpowiedź `201 Created`:** zapisany log i lista alertów utworzonych lub zaktualizowanych dla tego logu.
- **Odpowiedź `401 Unauthorized`:** brak lub niepoprawny klucz sensora.

---

## 8. Attack Lab (`/attack-lab`)

Dostępny tylko w środowisku demo. Umożliwia wyzwalanie scenariuszy ataku bezpośrednio przez API.

### Status

- **Endpoint:** `GET /attack-lab/status`
- **Autoryzacja:** Bearer token
- **Odpowiedź:**
  ```json
  {
    "running": false,
    "interval_seconds": 30,
    "seconds_remaining": null,
    "last_scenario": "port-scan",
    "last_result": {
      "scenario": "port-scan",
      "payloads_sent": 5,
      "alerts_created": 1
    }
  }
  ```

### Uruchomienie scenariusza

- **Endpoint:** `POST /attack-lab/run`
- **Body:** `{ "scenario": "port-scan | ssh-bruteforce | blacklist | normal | mixed" }`
- **Odpowiedź:** `{ "scenario": "string", "payloads_sent": number, "alerts_created": number }`

### Auto-attack

- **Endpoint:** `POST /attack-lab/auto/start` — Body: `{ "interval_seconds": number }`
- **Endpoint:** `POST /attack-lab/auto/stop`
