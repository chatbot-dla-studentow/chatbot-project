# Dokumentacja Agent1 Student

Dokumentacja agenta chatbotowego odpowiadającego na pytania studenckie (stypendia, BOS, harmonogramy, obrony prac).

## Spis Dokumentów

### 1. [README.md](README.md)
**Główna dokumentacja techniczna Agent1**
- Architektura RAG (Retrieval-Augmented Generation)
- Stack technologiczny (FastAPI, Ollama, Qdrant)
- Instalacja i deployment
- API endpoints
- Konfiguracja Docker
- Zarządzanie bazą wiedzy

**Dla kogo:** Developerzy, administratorzy systemu

---

### 2. [QUICK_START.md](User guide/QUICK_START.md)
**Szybki start - pierwsze uruchomienie**
- Minimalna konfiguracja
- Podstawowe komendy
- Testowanie API
- Rozwiązywanie podstawowych problemów

**Dla kogo:** Nowi członkowie zespołu, testowanie lokalne

---

### 3. [LOGGING_EXAMPLES.md](LOGGING_EXAMPLES.md)
**Przykłady użycia systemu logowania**
- Jak korzystać z endpointów logowania
- Statystyki zapytań (queries_log)
- Statystyki par Q&A (qa_pairs_log)
- Wyszukiwanie podobnych zapytań
- Analiza kategorii
- Skrypty maintenance

**Dla kogo:** Developerzy, testowanie funkcji logowania

---

### 4. [LOGGING_TEST_REPORT.md](Test reports/LOGGING_TEST_REPORT.md)
**Raport testowy - system logowania**
- Wyniki testów funkcjonalnych
- Walidacja endpointów logowania
- Metryki wydajnościowe
- Lista znanych bugów (jeśli są)
- Podsumowanie zgodności z wymaganiami

**Dla kogo:** Testerzy, code review, dokumentacja QA

---

### 5. [AGENT1_IMPLEMENTATION_REPORT.md](Test reports/AGENT1_IMPLEMENTATION_REPORT.md)
**Raport implementacji - zgodność z wymaganiami Prof. Orłowskiego**
- Wymagania funkcjonalne i niefunkcjonalne
- Podsumowanie wykonania (checklist)
- Architektura rozwiązania
- Endpointy administracyjne
- Metryki wydajności
- Wnioski i rekomendacje

**Dla kogo:** Promotor, obrona pracy, stakeholderzy

---

### 6. [TEST_REPORT.md](Test reports/TEST_REPORT.md)
**Raport testowy - testy ogólne Agent1**
- Testy jednostkowe
- Testy integracyjne
- Testy wydajnościowe
- Pokrycie testami
- Wykryte błędy i ich naprawa

**Dla kogo:** Testerzy, code review, dokumentacja QA

---

### 7. [user_guide.md](User guide/user_guide.md)
**Instrukcja użytkownika - jak korzystać z chatbota**
- Logowanie i nawigacja
- Zadawanie pytań
- Zrzuty ekranu interfejsu
- Najczęstsze przypadki użycia

**Dla kogo:** Użytkownicy końcowi, dokumentacja użytkownika

---

### 8. [mobile_tests.md](Test reports/mobile_tests.md)
**Raport testów mobilnych**
- Testy na urządzeniach mobilnych
- Responsywność interfejsu
- Zrzuty ekranu testów
- Wykryte problemy i rozwiązania

**Dla kogo:** Testerzy, dokumentacja QA, mobile testing

---

## Powiązane Zasoby

**Kod źródłowy:**
- `agents/agent1_student/app.py` - główna aplikacja FastAPI
- `agents/agent1_student/query_logger.py` - logika logowania
- `agents/agent1_student/load_knowledge_base.py` - ładowanie dokumentów
- `agents/agent1_student/docker-compose.yml` - konfiguracja Docker

**Baza wiedzy:**
- `agents/agent1_student/chatbot-baza-wiedzy-nowa/` - źródłowe dokumenty TXT
- `agents/agent1_student/knowledge/` - przetworzone JSON-y

**Deployment:**
- `/opt/chatbot-project/` - lokalizacja na serwerze produkcyjnym
- Port: 8001 (http://10.0.0.1:8001 przez VPN)

---

## 📖 Jak Korzystać z Dokumentacji

### Jestem nowy w projekcie
1. Przeczytaj [README.md](README.md) - zrozumiesz architekturę
2. Uruchom według [QUICK_START.md](User guide/QUICK_START.md)
3. Przetestuj API według [LOGGING_EXAMPLES.md](LOGGING_EXAMPLES.md)
4. Zobacz [user_guide.md](User guide/user_guide.md) - instrukcja dla użytkownika

### Pracuję nad funkcjonalnością
1. [README.md](README.md) - sprawdź istniejące API
2. [LOGGING_EXAMPLES.md](LOGGING_EXAMPLES.md) - przykłady użycia
3. Kod w `agents/agent1_student/app.py`

### Testuję system
1. [TEST_REPORT.md](Test reports/TEST_REPORT.md) - jakie testy już są
2. [LOGGING_TEST_REPORT.md](Test reports/LOGGING_TEST_REPORT.md) - testy logowania
3. [mobile_tests.md](Test reports/mobile_tests.md) - testy mobilne
4. [LOGGING_EXAMPLES.md](LOGGING_EXAMPLES.md) - jak testować ręcznie

### Przygotowuję dokumentację do obrony
1. [AGENT1_IMPLEMENTATION_REPORT.md](Test reports/AGENT1_IMPLEMENTATION_REPORT.md) - główny raport
2. [README.md](README.md) - architektura techniczna
3. [TEST_REPORT.md](Test reports/TEST_REPORT.md) + [LOGGING_TEST_REPORT.md](Test reports/LOGGING_TEST_REPORT.md) + [mobile_tests.md](Test reports/mobile_tests.md) - wyniki testów
4. [user_guide.md](User guide/user_guide.md) - instrukcja użytkownika

---

## Quick Links

- **Główny README projektu:** [../README.md](../README.md)
- **Deployment:** [../DEPLOYMENT.md](../DEPLOYMENT.md)
- **Repozytorium:** https://github.com/chatbot-dla-studentow/chatbot-project
- **Serwer produkcyjny:** vps-5f2a574b.vps.ovh.net (57.128.212.194)

---

**Ostatnia aktualizacja:** 10 lutego 2026  
**Maintainers:** Adam Siehen (@asiehen), Paweł Ponikowski (@pponikowski)

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Paweł Ponikowski (pponikowski)
