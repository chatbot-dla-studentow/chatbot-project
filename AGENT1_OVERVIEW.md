# Agent1 Student - Dokumentacja Techniczna

Chatbot studencki oparty na technologii RAG (Retrieval-Augmented Generation) odpowiadający na pytania dotyczące procedur uczelnianych.

## Spis treści

- [Opis projektu](#opis-projektu)
- [Stack technologiczny](#stack-technologiczny)
- [Architektura systemu](#architektura-systemu)
- [Wymagania](#wymagania)
- [Instalacja i uruchomienie](#instalacja-i-uruchomienie)
- [Struktura projektu](#struktura-projektu)
- [API Endpoints](#api-endpoints)
- [Baza wiedzy](#baza-wiedzy)
- [System logowania](#system-logowania)
- [Zarządzanie dokumentami](#zarządzanie-dokumentami)
- [Troubleshooting](#troubleshooting)
- [Konfiguracja](#konfiguracja)
- [Dokumentacja szczegółowa](#dokumentacja-szczegółowa)

---

## Opis projektu

**Agent1 Student** to inteligentny chatbot wspierający studentów Uniwersytetu WSB Merito w Gdańsku. System wykorzystuje RAG do udzielania odpowiedzi na podstawie lokalnej bazy wiedzy zawierającej dokumenty uczelni.

**Obszary wsparcia:**
- Procedury obrony pracy dyplomowej
- Rekrutacja i zmiany w toku studiów
- Stypendia (socjalne, rektora, dla niepełnosprawnych, Erasmus)
- Urlopy dziekańskie i zwolnienia
- Zmiana danych osobowych i RODO

**Status:** MVP - stabilnie działający system z pełną bazą wiedzy (220 dokumentów, 5 kategorii).

**Zespół projektowy:**
- Adam Siehen - Project Manager
- Patryk Boguski - Tech Ops, Backend ML
- Mikołaj Sykucki - Tester
- Oskar Jurgielaniec - Frontend
- Paweł Ponikowski - Baza wiedzy, dokumentacja

**Promotor:** Prof. dr hab. inż. Cezary Orłowski

---

## Stack technologiczny

**Backend:**
- Python 3.11
- FastAPI (API framework)
- LangChain (orchestration)
- httpx (async HTTP client)

**LLM i Embeddings:**
- Ollama (silnik LLM)
- mistral:7b (7.2B parametrów, Q4_K_M)
- nomic-embed-text (embeddings 768D)

**Baza wektorowa:**
- Qdrant (vector database)
- 3 kolekcje: agent1_student, agent1_query_logs, agent1_qa_logs

**Infrastruktura:**
- Docker + Docker Compose
- Open WebUI (interfejs użytkownika)
- Node-RED (orkiestracja workflow)

---

## Architektura systemu

```
┌─────────────┐
│ Open WebUI  │ (port 3000) - interfejs użytkownika
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Agent1     │ (port 8001) - FastAPI + RAG
│  Student    │
└──────┬──────┘
       │
       ├──────────────┐
       ▼              ▼
┌──────────┐   ┌──────────┐
│  Ollama  │   │  Qdrant  │ (port 6333)
│ mistral  │   │  Vector  │
│   :7b    │   │    DB    │
└──────────┘   └──────────┘
```

**Przepływ danych:**
1. Użytkownik zadaje pytanie (Open WebUI)
2. Agent1 generuje embedding zapytania (nomic-embed-text)
3. Wyszukiwanie w Qdrant (Top-K=2)
4. Kontekst + pytanie → Ollama mistral:7b
5. Odpowiedź + logowanie do Qdrant
6. Zwrot odpowiedzi użytkownikowi

---

## Wymagania

**Niezbędne:**
- Docker 20.10+
- Docker Compose 2.0+
- Ollama zainstalowana i działająca na http://localhost:11434
- Modele: mistral:7b, nomic-embed-text

**Opcjonalne:**
- Python 3.11+ (do zarządzania bazą wiedzy)
- curl lub httpie (testowanie API)

**Zasoby systemowe:**
- RAM: minimum 8GB (zalecane 16GB)
- Dysk: 10GB wolnego miejsca
- CPU: 4 rdzenie (zalecane)

---

## Instalacja i uruchomienie

### 1. Przygotowanie Ollama

```bash
# Zainstaluj Ollama (jeśli nie masz)
# https://ollama.ai/

# Pobierz modele
ollama pull mistral:7b
ollama pull nomic-embed-text

# Weryfikacja
ollama list
```

### 2. Uruchomienie usługi

```bash
# Przejdź do katalogu Agent1
cd agents/agent1_student

# Uruchom wszystkie kontenery
docker compose up -d --build

# Sprawdź status
docker ps
```

### 3. Inicjalizacja kolekcji logów (jednorazowo)

```bash
# W katalogu agents/agent1_student
python helpers/init_log_collections.py
```

### 4. Wczytanie bazy wiedzy do Qdrant (jednorazowo)

```bash
python helpers/load_knowledge_base.py
```

### 5. Dostęp do aplikacji

**Agent1 Student API:**
- URL: http://localhost:8001
- Dokumentacja: http://localhost:8001/docs

**Open WebUI:**
- URL: http://localhost:3000

**Qdrant Dashboard:**
- URL: http://localhost:6333/dashboard

**Node-RED (Orkiestracja Workflow):**
- URL: http://localhost:1880
- Edytor flow: http://localhost:1880 (GUI w przeglądarce)
- Funkcje:
  - Wizualna orkiestracja przepływu danych między agentami
  - Routing zapytań do odpowiednich agentów
  - Automatyzacja procesów
- Integracja z Agent1:
  - Endpoint publikacji: POST /publish-workflow
  - Plik flow: agent1_flow.json
  - URL Node-RED: http://node-red:1880

### 6. Testowanie

```bash
# Test podstawowy
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [{"role": "user", "content": "Jak uzyskać stypendium?"}],
    "stream": false
  }'

# Test wersji
curl http://localhost:8001/api/version

# Statystyki zapytań
curl http://localhost:8001/admin/logs/queries/stats
```

---

## Struktura projektu

```
agents/agent1_student/
├── app.py                              # Główna aplikacja FastAPI + RAG
├── Dockerfile                          # Obraz kontenera
├── requirements.txt                    # Zależności Python
├── knowledge_manager.py                # CLI do zarządzania bazą wiedzy
├── agent1_flow.json                    # Workflow Node-RED
| 
| 📌 Uwaga: docker-compose.yml usunięty (v2.0)
|    → Użyj głównego /docker-compose.yml lub /deployment/setup.sh
│
├── chatbot-baza-wiedzy-nowa/           # Źródłowe pliki (TXT, DOCX, PDF)
│   ├── dane_osobowe/
│   ├── egzaminy/
│   ├── rekrutacja/
│   ├── stypendia/
│   └── urlopy_zwolnienia/
│
├── knowledge/                          # Przetworzone JSON dla Qdrant
│   ├── all_documents.json              # Zbiorczy plik (220 dokumentów)
│   ├── dane_osobowe/
│   │   ├── dane_osobowe_documents.json    (77 chunks)
│   │   └── dane_osobowe_qa_pairs.json     (3 QA)
│   ├── egzaminy/
│   │   ├── egzaminy_documents.json        (16 chunks)
│   │   └── egzaminy_qa_pairs.json         (4 QA)
│   ├── rekrutacja/
│   │   ├── rekrutacja_documents.json      (56 chunks)
│   │   └── rekrutacja_qa_pairs.json       (4 QA)
│   ├── stypendia/
│   │   ├── stypendia_documents.json       (56 chunks)
│   │   └── stypendia_qa_pairs.json        (4 QA)
│   └── urlopy_zwolnienia/
│       ├── urlopy_zwolnienia_documents.json   (15 chunks)
│       └── urlopy_zwolnienia_qa_pairs.json    (2 QA)
│
├── helpers/                             # Skrypty zarządzania
│   ├── parse_knowledge_base.py          # Parser plików źródłowych
│   ├── add_qa_pairs.py                  # Dodawanie przykładowych QA
│   ├── verify_knowledge_base.py         # Walidacja struktury bazy
│   ├── load_knowledge_base.py           # Wczytanie do Qdrant
│   ├── update_knowledge.py              # Aktualizacja inkrementalna
│   ├── delete_qdrant_collection.py      # Czyszczenie kolekcji
│   ├── init_log_collections.py          # Inicjalizacja kolekcji logów
│   └── query_logger.py                  # Logowanie zapytań i QA
```

---

## API Endpoints

### Kompatybilne z Ollama

**POST /api/chat**
Konwersacja z RAG (główny endpoint).
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [{"role": "user", "content": "Twoje pytanie"}],
    "stream": false
  }'
```

**POST /api/generate**
Generowanie odpowiedzi (bez streamingu).
```bash
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "prompt": "Twoje pytanie",
    "stream": false
  }'
```

**GET /api/tags**
Lista dostępnych modeli.

**GET /api/version**
Wersja API.

**GET /api/ps**
Lista uruchomionych modeli.

**POST /api/pull**
Pobieranie modelu z Ollama.

**POST /api/push**
Wysyłanie modelu do Ollama.

**POST /api/delete**
Usuwanie modelu.

### Endpointy dodatkowe

**POST /run**
Uruchomienie zadania.

**POST /publish-workflow**
Publikacja workflow do Node-RED.
```bash
curl -X POST http://localhost:8001/publish-workflow \
  -H "Content-Type: application/json" \
  -d @agent1_flow.json
```
Wysyła workflow z pliku agent1_flow.json do Node-RED. Workflow definiuje przepływ danych między agentami i logikę orkiestracji.

### Endpointy administracyjne

**GET /admin/logs/queries/stats**
Statystyki zapytań użytkowników.
```bash
curl http://localhost:8001/admin/logs/queries/stats
```
Zwraca:
```json
{
  "success": true,
  "data": {
    "total_queries": 50,
    "categories": {
      "stypendia": 15,
      "egzaminy": 12,
      "dane_osobowe": 10,
      "rekrutacja": 8,
      "urlopy_zwolnienia": 3,
      "unknown": 2
    }
  }
}
```

**GET /admin/logs/qa/stats**
Statystyki par pytanie-odpowiedź.
```bash
curl http://localhost:8001/admin/logs/qa/stats
```
Zwraca:
```json
{
  "success": true,
  "data": {
    "total_qa_pairs": 50,
    "categories": {...},
    "average_rag_score": 0.742
  }
}
```

**GET /admin/logs/queries/search?query=TEXT&limit=N**
Wyszukiwanie podobnych zapytań w historii.
```bash
curl "http://localhost:8001/admin/logs/queries/search?query=stypendium&limit=5"
```

**GET /admin/logs/categories**
Lista kategorii ze słowami kluczowymi.
```bash
curl http://localhost:8001/admin/logs/categories
```

---

## Baza wiedzy

### Statystyki

- **Łącznie dokumentów:** 220 (203 chunki + 17 QA pairs)
- **Kategorie:** 5 (dane_osobowe, egzaminy, rekrutacja, stypendia, urlopy_zwolnienia)
- **Format:** JSON z UTF-8
- **Rozmiar:** 804KB
- **Embeddingi:** 768D (nomic-embed-text)

### Kategorie

**dane_osobowe (77 chunków + 3 QA)**
- Zmiana danych w systemie
- RODO i ochrona danych
- Aktualizacja kontaktu

**egzaminy (16 chunków + 4 QA)**
- Obrona pracy dyplomowej
- Harmonogramy
- Reklamacje ocen
- Przedłużenie sesji

**rekrutacja (56 chunków + 4 QA)**
- Warunki przyjęcia
- Zmiana kierunku
- Wznowienie studiów
- Rezygnacja

**stypendia (56 chunków + 4 QA)**
- Stypendium socjalne
- Stypendium rektora
- Stypendia dla niepełnosprawnych
- Erasmus+

**urlopy_zwolnienia (15 chunków + 2 QA)**
- Urlopy dziekańskie
- Zwolnienia z WF

### Przykładowe pytania

**Dane osobowe:**
- Jak zmienić swoje dane osobowe w systemie?
- Jakie są zasady ochrony danych osobowych dla studentów?
- Gdzie zgłosić zmianę numeru telefonu lub maila?

**Egzaminy:**
- Jak wygląda procedura obrony pracy dyplomowej?
- Kiedy odbywa się harmonogram obron prac dyplomowych?
- Jak złożyć reklamację na ocenę z egzaminu?

**Rekrutacja:**
- Jakie są warunki przyjęcia na studia?
- Czy mogę zmienić kierunek studiów?
- Jak wznowić naukę po przerwaniu studiów?

**Stypendia:**
- Jak ubiegać się o stypendium?
- Jaka jest wysokość stypendiów w bieżącym semestrze?
- Czy osoby niepełnosprawne mogą ubiegać się o wyższe stypendium?

**Urlopy/Zwolnienia:**
- Kiedy mogę wziąć urlop dziekański?
- Czy mogę być zwolniony z zajęć z wychowania fizycznego?

### Struktura dokumentu w Qdrant

**Payload dokumentu:**
```json
{
  "id": "uuid",
  "text": "Treść dokumentu lub fragmentu...",
  "metadata": {
    "category": "stypendia",
    "source_file": "FAQ - stypendia.md",
    "file_type": "md",
    "chunk_index": 2
  }
}
```

**Payload QA pair:**
```json
{
  "id": "uuid",
  "text": "Pytanie: Jak mogę uzyskać stypendium?\nOdpowiedź: Aby uzyskać...",
  "metadata": {
    "type": "qa",
    "category": "stypendia",
    "question": "Jak mogę uzyskać stypendium?",
    "answer": "Aby uzyskać..."
  }
}
```

---

## System logowania

Agent1 automatycznie loguje wszystkie zapytania i odpowiedzi do Qdrant. System wykrywa kategorię zapytania na podstawie słów kluczowych.

### Kolekcje Qdrant

**agent1_student**
Główna baza wiedzy (dokumenty + QA pairs).

**agent1_query_logs**
Logi zapytań użytkowników.
```json
{
  "query": "Jak mogę uzyskać stypendium?",
  "category": "stypendia",
  "timestamp": "2026-02-06T16:59:12.826175",
  "user_id": "anonymous",
  "log_id": "uuid",
  "model": "mistral:7b"
}
```

**agent1_qa_logs**
Logi par pytanie-odpowiedź z RAG scores.
```json
{
  "query": "Jak mogę uzyskać stypendium?",
  "answer": "Aby uzyskać stypendium...",
  "category": "stypendia",
  "timestamp": "2026-02-06T16:59:13.123456",
  "user_id": "anonymous",
  "log_id": "uuid",
  "sources": [
    {"file": "stypendia/FAQ.md", "chunk": 1}
  ],
  "rag_score": 0.854,
  "model": "mistral:7b"
}
```

### Kategorie zapytań

System rozpoznaje 5 kategorii na podstawie słów kluczowych:

- **dane_osobowe** - zmiana danych, adresu, email, RODO
- **egzaminy** - egzaminy, obrona pracy, sesja, oceny
- **rekrutacja** - rekrutacja, zmiana kierunku, rezygnacja, wznowienie
- **stypendia** - stypendium socjalne, rektora, niepełnosprawność, Erasmus
- **urlopy_zwolnienia** - urlopy dziekańskie, zwolnienia z WF

### Przykłady użycia

```bash
# Statystyki zapytań
curl http://localhost:8001/admin/logs/queries/stats | jq '.'

# Statystyki QA
curl http://localhost:8001/admin/logs/qa/stats | jq '.'

# Wyszukiwanie podobnych zapytań
curl "http://localhost:8001/admin/logs/queries/search?query=stypendium&limit=5" | jq '.'

# Lista kategorii
curl http://localhost:8001/admin/logs/categories | jq '.'
```

---

## Zarządzanie dokumentami

### Dodawanie nowych dokumentów

**Opcja A: Nowe pliki źródłowe**
```bash
# 1. Dodaj pliki do chatbot-baza-wiedzy-nowa/<kategoria>/
#    Obsługiwane formaty: .txt, .docx, .doc, .pdf

# 2. Przetwórz na JSON
cd agents/agent1_student
python helpers/parse_knowledge_base.py

# 3. (Opcjonalnie) Dodaj QA pairs
# Edytuj add_qa_pairs.py i uruchom:
python helpers/add_qa_pairs.py

# 4. Wczytaj do Qdrant
python helpers/load_knowledge_base.py
```

**Opcja B: Edycja bezpośrednia JSON**
```bash
# 1. Edytuj pliki w knowledge/<kategoria>/*.json

# 2. Wczytaj do Qdrant
cd agents/agent1_student
python helpers/load_knowledge_base.py
```

### Weryfikacja bazy wiedzy

```bash
cd agents/agent1_student
python helpers/verify_knowledge_base.py
```

Wyświetli:
- Liczbę dokumentów w każdej kategorii
- Liczbę QA pairs
- Całkowity rozmiar bazy
- Problemy ze strukturą (jeśli są)

### Czyszczenie kolekcji

```bash
cd agents/agent1_student
python helpers/delete_qdrant_collection.py
```

Kolekcja jest automatycznie usuwana i tworzona na nowo przy każdym uruchomieniu `helpers/load_knowledge_base.py`.

### Reindeksacja kompletna

```bash
cd agents/agent1_student

# 1. Przetwórz pliki źródłowe
python helpers/parse_knowledge_base.py

# 2. Dodaj QA pairs
python helpers/add_qa_pairs.py

# 3. Wczytaj do Qdrant (automatycznie czyści starą kolekcję)
python helpers/load_knowledge_base.py
```

---

## Troubleshooting

### Ollama nie odpowiada

**Objaw:** Brak odpowiedzi z http://localhost:11434

**Rozwiązanie:**
```bash
# Sprawdź czy Ollama działa
ollama list

# Pobierz modele jeśli brakuje
ollama pull mistral:7b
ollama pull nomic-embed-text

# Sprawdź czy Ollama serwer działa
curl http://localhost:11434/api/version
```

### Qdrant nie startuje

**Objaw:** Brak połączenia z Qdrant

**Rozwiązanie:**
```bash
# Sprawdź Docker
docker ps | grep qdrant

# Restart kontenerów
cd agents/agent1_student
docker compose down
docker compose up -d --build

# Logi Qdrant
docker logs qdrant
```

### Brak wyników w odpowiedziach

**Objaw:** Chatbot odpowiada "Nie mam tej informacji w bazie wiedzy"

**Rozwiązanie:**
```bash
# 1. Sprawdź czy kolekcja istnieje
# Otwórz http://localhost:6333/dashboard
# Powinny być kolekcje: agent1_student, agent1_query_logs, agent1_qa_logs

# 2. Wczytaj bazę wiedzy ponownie
cd agents/agent1_student
python helpers/load_knowledge_base.py

# 3. Weryfikuj plik źródłowy
ls -lh knowledge/all_documents.json
```

### Agent1 nie startuje

**Objaw:** Kontener agent1_student crashuje

**Rozwiązanie:**
```bash
# Logi kontenera
docker logs agent1_student

# Najczęstsze przyczyny:
# - Brak połączenia z Ollama (sprawdź http://localhost:11434)
# - Brak połączenia z Qdrant (sprawdź docker ps)
# - Błędy w requirements.txt (sprawdź logi build)

# Restart z rebuild
cd agents/agent1_student
docker compose down
docker compose up -d --build
```

### Inicjalizacja kolekcji logów

**Objaw:** Błędy przy zapisie logów

**Rozwiązanie:**
```bash
cd agents/agent1_student
python helpers/init_log_collections.py
```

---

## Konfiguracja

### Parametry RAG (app.py)

```python
# Liczba wyników z Qdrant
TOP_K = 2

# Limit tokenów odpowiedzi
NUM_PREDICT = 80

# Model LLM
MODEL_NAME = "mistral:7b"

# Model embeddingów
EMBEDDING_MODEL = "nomic-embed-text"
```

### Parametry load_knowledge_base.py

```python
# Ścieżka do bazy wiedzy
KNOWLEDGE_BASE_PATH = "./knowledge"

# Nazwa kolekcji
COLLECTION_NAME = "agent1_student"

# Model embeddingów
EMBEDDING_MODEL = "nomic-embed-text"

# Batch size
BATCH_SIZE = 20
```

### Docker Compose - Centralna konfiguracja

📌 **Od v2.0:** Stary `agents/agent1_student/docker-compose.yml` został usunięty.

Używaj **głównego `/docker-compose.yml`** w katalogu root:

```yaml
services:
  agent1_student:
    build: ./agents/agent1_student
    ports:
      - "8001:8000"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - QDRANT_URL=http://qdrant:6333
    networks:
      - ai_network
```

**Uruchamianie:**
```bash
# Automatycznie (recommended)
./deployment/setup.sh

# Lub ręcznie
docker-compose up -d
```

### Performance tips

- **LLM:** mistral:7b - dobry balans szybkości i jakości
- **Embeddings:** nomic-embed-text (768D) - szybkie i skuteczne
- **Batch size:** 20 - optymalne dla większości przypadków
- **Top-K:** 2 - wystarczające dla precyzji odpowiedzi
- **Chunking:** ~500 znaków - balans między kontekstem a precyzją

---

## Historia rozwoju i wykonane zadania

### Sprint 1-3 (Listopad 2025 - Luty 2026)

| Członek zespołu | Rola | Zadania (skrót) |
|---|---|---|
| Adam Siehen | Project Manager | Do uzupełnienia |
| Patryk Boguski | Tech Ops | Do uzupełnienia |
| Mikołaj Sykucki | Tester/Analityk | Do uzupełnienia |
| Oskar Jurgielaniec | Frontend | Do uzupełnienia |
| Paweł Ponikowski | Baza wiedzy i dokumentacja | FAQ, procedury, stypendia, regulaminy; skrypty: parse/load/update/verify/check/add_qa; dokumentacja: knowledge.md, ARCHITECTURE.md; testy helperów; merge beta -> main |

---

## Dokumentacja szczegółowa

Dokumentacja znajduje się w katalogu `docs_agent1/`:

**[docs_agent1/README.md](docs_agent1/README.md)**
Pełna dokumentacja techniczna z przykładami kodu.

**[docs_agent1/QUICK_START.md](docs_agent1/QUICK_START.md)**
Przewodnik szybkiego startu z przykładami.

**[docs_agent1/LOGGING_EXAMPLES.md](docs_agent1/LOGGING_EXAMPLES.md)**
Przykłady użycia systemu logowania.

**[docs_agent1/LOGGING_TEST_REPORT.md](docs_agent1/LOGGING_TEST_REPORT.md)**
Raport testowy systemu logowania.

**[docs_agent1/AGENT1_IMPLEMENTATION_REPORT.md](docs_agent1/AGENT1_IMPLEMENTATION_REPORT.md)**
Raport implementacji zgodny z wymaganiami promotora.

**[docs_agent1/TEST_REPORT.md](docs_agent1/TEST_REPORT.md)**
Raport testów ogólnych aplikacji.

**[docs_agent1/INDEX.md](docs_agent1/INDEX.md)**
Indeks całej dokumentacji.

---

## Linki i zasoby

**Projekt:**
- Repozytorium: https://github.com/chatbot-dla-studentow/chatbot-project
- Serwer produkcyjny: vps-5f2a574b.vps.ovh.net (57.128.212.194)
- Lokalizacja na serwerze: /opt/chatbot-project

**Narzędzia projektowe:**
- OneDrive: https://m365ht-my.sharepoint.com/:f:/g/personal/gdx131362_student_gdansk_merito_pl/IgCQRszyJgUJS40VSaVd4mDjAT1TAcorcdLnRoKL6SvMw2g?e=dneRN0
- Trello: https://trello.com/b/h5pYK4my/chatbot-obs%C5%82ugujacy-studentow
- Moodle: https://moodle2.e-wsb.pl/course/view.php?id=208534

**API Documentation:**
- FastAPI Swagger: http://localhost:8001/docs
- FastAPI ReDoc: http://localhost:8001/redoc

---

**Ostatnia aktualizacja:** 10 lutego 2026  
**Wersja:** 1.0 (MVP)  
**Maintainers:** Adam Siehen (@adamsiehen), Paweł Ponikowski (@pponikowski)

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
