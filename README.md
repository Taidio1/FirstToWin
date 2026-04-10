# NDR (Network Detection and Response) - Projekt Zespołowy

## 📖 O projekcie
Projekt realizowany w ramach przedmiotu "Projekt zespołowy". 
Celem projektu jest zaprojektowanie i implementacja systemu NDR, którego zadaniem jest monitorowanie ruchu sieciowego, wykrywanie anomalii i potencjalnych zagrożeń bezpieczeństwa oraz umożliwienie reakcji na zidentyfikowane incydenty.

System rozwiązuje problem braku przejrzystości w sieciach lokalnych oraz opóźnień w detekcji ataków (takich jak skanowanie portów, ataki DDoS, czy nieautoryzowany ruch). Użytkownikami docelowymi systemu są administratorzy sieci oraz analitycy SOC (Security Operations Center).

## 👥 Zespół i podział prac

Nasz zespół składa się z 6 osób. Każdy członek zespołu ma przypisaną konkretną rolę, aby zapewnić płynną realizację projektu:
* **Kacper (Project Manager & Backend Developer)** - Koordynacja prac zespołu w systemie do zarządzania zadaniami, projektowanie architektury backendowej, API oraz logiki biznesowej.
* **Kuba (Head of IT Security)** - Opracowywanie reguł detekcji, projektowanie mechanizmów bezpieczeństwa oraz weryfikacja systemu pod kątem odporności na ataki.
* **Jonasz (Head of IT Security)** - Analiza wektorów ataków, tworzenie scenariuszy testowych (Red/Blue teaming) oraz wsparcie w logice detekcji zagrożeń.
* **Bartek (Frontend Developer)** - Projektowanie i implementacja interfejsu użytkownika (dashboardów, tabel z alertami) z naciskiem na UX/UI.
* **Oskar (Data Analyst)** - Przetwarzanie logów sieciowych, wykrywanie anomalii statystycznych i tworzenie modeli/skryptów do kategoryzacji ruchu.
* **Łukasz (Technical Writer, Integrator & Presenter)** - Tworzenie i utrzymanie dokumentacji projektu, integracja modułów (sklejanie backendu z frontendem/analityką), przygotowanie ostatecznej prezentacji oraz instrukcji wdrożeniowych.

## ⚙️ Główne funkcjonalności (MVP)

1.  **Zarządzanie sensorami sieciowymi:** System umożliwia rejestrację, autoryzację (np. za pomocą kluczy API) monitorowanie statusu "sensorów" (skryptów nasłuchujących/urządzeń), które przesyłają logi do głównego serwera.
2.  **Dashboard (Interfejs Użytkownika):** Przejrzysty panel wyświetlający statystyki sieciowe i krytyczne alerty w czasie rzeczywistym.
3.  **Operacje CRUD:** Możliwość dodawania, edytowania i usuwania reguł detekcji (np. blokowanie konkretnych adresów IP).
4.  **Przechowywanie danych:** Zapisywanie logów sieciowych i historii alertów w bazie danych.
5.  **Walidacja danych:** Sprawdzanie poprawności formatów (np. adresów IP, masek podsieci) przy wprowadzaniu nowych reguł.
6.  **Integracja z Threat Intelligence** (OSINT) Gdy sensor przesyła logi z nieznanym adresem IP z zewnątrz, Nasz backend odpytuje darmowe API (np. AbuseIPDB, VirusTotal lub AlienVault OTX), aby sprawdzić, czy ten adres IP nie znajduje się na globalnych czarnych listach
7.  **Interaktywna Wizualizacja Grafowa (Network Graph)** Wizualizacja topologii sieci w formie interaktywnego grafu

## 🏗️ Architektura i technologie
*(Tu uzupełnijcie technologie, na które się zdecydujecie)*

* **Backend:** np. Python (FastAPI / Django) lub Node.js
* **Frontend:** np. React / Vue.js
* **Baza danych:** np. PostgreSQL / MongoDB / Elasticsearch (do logów)
* **Analiza Danych:** np. Pandas, narzędzia do analizy PCAP
* **Zarządzanie projektem:** np. Jira / GitHub

## 🚀 Instrukcja uruchomienia (Lokalnie)
