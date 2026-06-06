# Scenariusz prezentacji NDR

Czas: 10–15 minut. Poniżej opisany jest pełny przebieg demo — co pokazać na ekranie i co powiedzieć przy każdym kroku.

## Przygotowanie (przed prezentacją)

```powershell
# 1. Uruchom stack
docker compose up --build -d

# 2. Sprawdź, czy wszystko działa
python scripts/smoke_demo.py
```

Smoke test powinien zakończyć się komunikatem `All checks passed`. Jeśli nie — sprawdź sekcję "Częste problemy" w `docs/instrukcja_uruchomienia.md`.

Otwórz przeglądarkę: **http://localhost:3000**

---

## Krok 1 — Logowanie (1 min)

**Ekran:** strona logowania

Pokaż formularz, wpisz:
- Email: `demo@example.local`
- Hasło: `demo1234`

**Co powiedzieć:**  
"System wymaga uwierzytelnienia. Mamy trzy role: admin, analyst i viewer. Demo działa na roli analityka SOC."

---

## Krok 2 — Dashboard w spokojnym stanie (2 min)

**Ekran:** `/` — Dashboard

Zwróć uwagę na:
- Liczniki: *Open critical alerts*, *Alerts 24h*, *Sensors online*, *Packets analyzed*
- Wykres *Alerts over time* — aktualnie spokojnie
- Wykres kołowy *By severity*
- *Top noisy sources* — brak znaczących źródeł

**Co powiedzieć:**  
"To jest widok przed atakiem. Jeden sensor online, zero alertów krytycznych. System monitoruje ruch i wyświetla dane w czasie rzeczywistym — dashboard odświeża się co 5 sekund bez przeładowania strony."

---

## Krok 3 — Reguły detekcji (2 min)

**Ekran:** `/rules` — Detection rules

Pokaż tabelę reguł:
- `Port Scan` — typ `port_scan`, severity `high`
- `SSH Brute Force` — typ `connection_threshold`, severity `critical`
- `Blacklist IP` — typ `blacklist_ip`, severity `critical`

Pokaż kolumnę *Hits* — na początku zera.

**Co powiedzieć:**  
"Reguły detekcji są konfigurowalne. Każda ma typ, severity i warunki dopasowania: próg połączeń, okno czasowe, port docelowy lub konkretny adres IP. Można je włączać, edytować i usuwać z poziomu UI."

Opcjonalnie: utwórz nową regułę przez *New rule* i anuluj.

---

## Krok 4 — Symulacja ataku (2 min)

**Terminal (trzymaj go przygotowanego obok):**

```powershell
python scripts/simulate_attack.py --type full-demo
```

Skrypt wykona kolejno:
1. Normalny ruch sieciowy (tło)
2. Port scan z `10.10.10.99`
3. SSH brute force z `10.10.10.100`
4. Ruch z zablokowanego IP `203.0.113.66`

**Co powiedzieć:**  
"Uruchamiamy symulator, który wysyła logi do backendu przez uwierzytelniony endpoint ingest. Klucz sensora w nagłówku `X-Sensor-Key` jest wymagany — bez niego backend zwraca 401. Teraz backend przetwarza logi przez silnik detekcji."

Wróć do przeglądarki — alerty pojawią się po chwili automatycznie.

---

## Krok 5 — Przegląd alertów (3 min)

**Ekran:** `/alerts` — Alerts

Pokaż:
- Alerty z severity `critical` i `high`
- Filtrowanie po severity: wybierz `critical`
- Filtrowanie po statusie: `open`

Kliknij alert `SSH Brute Force` lub `Port Scan`:

**Ekran:** Modal alertu (AlertDetail)

Pokaż pola:
- Severity + Status badges
- Nazwa reguły i szczegóły
- Source IP → Destination IP, Sensor, czas
- Sekcja **OSINT enrichment** — AbuseIPDB odpytane automatycznie

**Co powiedzieć:**  
"Po kliknięciu alertu analityk widzi pełen kontekst: skąd przyszedł ruch, do czego się połączył, która reguła to wykryła i ile razy ten wzorzec był obserwowany. System automatycznie odpytuje AbuseIPDB, żeby sprawdzić reputację adresu IP."

Pokaż deduplikację: jeśli ten sam src_ip wygenerował wiele logów, jest jeden alert z zaktualizowanym polem *Last seen* — nie lawina duplikatów.

---

## Krok 6 — Reakcja analityka (2 min)

Na otwartym modalu alertu:

1. Kliknij **Acknowledge** — status zmienia się na `acknowledged`
2. Kliknij **Add to blacklist** na IP źródłowym → tworzy się nowa reguła `blacklist_ip`
3. Wróć do `/rules` — pokaż nową regułę na liście

**Co powiedzieć:**  
"To jest flow reakcji SOC: zauważ → zbadaj → zablokuj. Jeden klik tworzy regułę, która od tej chwili będzie flagować ruch z tego samego IP jako krytyczny."

Opcjonalnie: oznacz alert jako `resolved`.

---

## Krok 7 — Attack Lab (1 min)

**Ekran:** `/attack-lab` — Attack Simulator

Pokaż:
- Auto-attack (ustaw interval 15s, kliknij *Start Auto-attack*)
- Karty scenariuszy manualnych
- Wróć do dashboardu — alerty pojawiają się automatycznie

**Co powiedzieć:**  
"Attack Lab służy do demonstracji i testowania reguł bez potrzeby wychodzenia do terminala. Przydatne przy tworzeniu nowych reguł — można od razu zobaczyć, czy detekcja reaguje poprawnie."

Zatrzymaj auto-attack (*Stop Auto-attack*) przed zakończeniem.

---

## Krok 8 — Architektura i podsumowanie (2 min)

Wróć do dashboardu, pokaż liczniki po ataku (vs. stan przed).

**Co powiedzieć:**  
"Podsumowując: system składa się z czterech warstw. Sensor lub symulator wysyła surowe logi sieciowe przez uwierzytelniony endpoint HTTP. Backend przetwarza je silnikiem detekcji — reguły konfigurowane są w bazie danych, nie na sztywno w kodzie. Alerty są deduplikowane, żeby lista pozostała czytelna. Frontend odświeża dane w czasie rzeczywistym przez polling co 5 sekund."

"Ograniczenia MVP: sensor to symulator HTTP, nie prawdziwy tap sieciowy. OSINT korzysta z darmowego API, które ma limit zapytań. W produkcji zamiast pollingu użylibyśmy WebSocketów."

---

## Możliwe pytania od prowadzącego

**"Jak działa autoryzacja sensora?"**  
Każdy sensor ma unikalny klucz API przechowywany jako hash w bazie. Endpoint `POST /api/ingest/logs` wymaga nagłówka `X-Sensor-Key`. Brak lub błędny klucz → 401.

**"Jak działa deduplikacja alertów?"**  
Silnik detekcji przed utworzeniem alertu sprawdza, czy istnieje już otwarty alert o tym samym `rule_id`, `src_ip`, `dst_ip` i protokole. Jeśli tak — aktualizuje pole `details` z nowym timestampem zamiast tworzyć duplikat.

**"Dlaczego polling a nie WebSocket?"**  
MVP — polling co 5s jest wystarczający do demonstracji i prostszy do utrzymania. WebSocket byłby następnym krokiem.

**"Czy Zeek/Suricata jest zintegrowany?"**  
Konfiguracje są w katalogach `zeek/` i `suricata/`. Integracja z prawdziwym ruchem sieciowym przez ten sam przeplyw ingest jest zaplanowana jako rozszerzenie — w MVP używamy symulatora, żeby demo było stabilne i odtwarzalne.

---

## Checklist przed wejściem na salę

- [ ] `docker compose up --build -d` — stack działa
- [ ] `python scripts/smoke_demo.py` — wszystkie checks zielone
- [ ] Przeglądarka otwarta na http://localhost:3000
- [ ] Terminal z przygotowaną komendą `simulate_attack.py --type full-demo`
- [ ] Wylogowany z frontendu (żeby pokazać login na żywo)
