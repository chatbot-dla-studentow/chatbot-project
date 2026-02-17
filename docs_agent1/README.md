# ChatBot dla Studentów – RAG (Agent1 Student)

## Projekt inżynierski w ramach kierunku Informatyka na Uniwersytecie WSB Merito w Gdańsku

Chatbot oparty na technologii RAG (Retrieval‑Augmented Generation) dla studentów. Odpowiada na pytania dotyczące obrony pracy, rekrutacji, stypendiów, urlopów/zwolnień oraz danych osobowych na podstawie lokalnej bazy wiedzy.

## Skład zespołu:
* Adam Sieheń – Project Manager (architektura systemu, implementacja MVP, integracja zespołu)
* Patryk Boguski – Tech Ops (backend, integracja LLM)
* Mikołaj Sykucki – Tester (testy automatyczne i walidacja systemu)
* Oskar Jurgielaniec – Frontend (interfejs użytkownika aplikacji czatowej)
* Paweł Ponikowski – Public Domain (procedury, dane publiczne, przygotowanie zasobów pod serwer MCP)

## Promotor:
Prof. dr hab. inż. Cezary Orłowski

## Cel projektu
Celem projektu jest utworzenie chatbota wspierającego studentów w zakresie:
* procedury obrony pracy dyplomowej
* procedur rekrutacyjnych i zmian w toku studiów
* informacji o stypendiach
* urlopów dziekańskich i zwolnień
* zmian danych osobowych i ochrony danych

## Linki do narzędzi projektowych:
### Link do dokumentacji na OneDrive:
https://m365ht-my.sharepoint.com/:f:/g/personal/gdx131362_student_gdansk_merito_pl/IgCQRszyJgUJS40VSaVd4mDjAT1TAcorcdLnRoKL6SvMw2g?e=dneRN0
### Link do Trello:
https://trello.com/b/h5pYK4my/chatbot-obs%C5%82ugujacy-studentow
### Link do Moodle:
https://moodle2.e-wsb.pl/course/view.php?id=208534

**Status:** MVP – stabilnie indeksuje dokumenty TXT/DOCX/PDF po konwersji do JSON; bardzo duże PDF-y mogą wymagać ponownej indeksacji.

## Główne cechy

**Lokalna baza wiedzy** – dokumenty źródłowe w `chatbot-baza-wiedzy-nowa/` i przetworzone JSON-y w `knowledge/`  
**RAG** – embeddingi Ollama + wyszukiwanie w Qdrant  
**Batch embeddings** – optymalizacja przetwarzania (20 chunks/batch)  
**Smart chunking** – automatyczne dzielenie dokumentów na fragmenty  
**Kategorie wiedzy** – dane_osobowe, egzaminy, rekrutacja, stypendia, urlopy_zwolnienia  
**QA pairs** – przykładowe pytania i odpowiedzi w każdej kategorii  
**API kompatybilne z Ollama** – endpointy /api/chat i /api/generate  
**Docker Compose** – szybkie uruchomienie całej usługi  
**Query Logging** – automatyczne logowanie zapytań i odpowiedzi w Qdrant  
**Category Detection** – automatyczne wykrywanie kategorii zapytań

## Zrzuty ekranu

Ekran chatu (Open WebUI):
![alt text](img/user_guide/chat.png)

Qdrant Dashboard:
![alt text](img/user_guide/home.png)

## Wymagania

- **Linux/macOS/Windows**
- **Docker** oraz **Docker Compose**
- **Ollama** działająca na `http://localhost:11434`
  - Modele: `mistral:7b`, `nomic-embed-text`

## Instalacja i uruchomienie

### 1. Przygotowanie Ollama

```bash
ollama pull mistral:7b
ollama pull nomic-embed-text
```

### 2. Uruchomienie usługi

```bash
cd agents/agent1_student

docker compose up -d --build
```

### 3. Dostęp do aplikacji

```
Agent1 Student API:  http://localhost:8001
Open WebUI:          http://localhost:3000
Qdrant UI:           http://localhost:6333/dashboard
Node-RED:            http://localhost:1880
```

## Indeksacja dokumentów

### Aktualna ścieżka danych

- Źródła: `chatbot-baza-wiedzy-nowa/`
- Przetworzone JSON-y: `knowledge/`
- Plik zbiorczy: `knowledge/all_documents.json`

### Szybka reindeksacja (CLI)

**Pierwsza instalacja (pełny load)**:
```bash
# 1) Przetworzenie plików źródłowych do JSON
python helpers/parse_knowledge_base.py

# 2) Dodanie QA pairs
python helpers/add_qa_pairs.py

# 3) Wczytanie do Qdrant (pełne)
python helpers/load_knowledge_base.py
```

**Regularna aktualizacja (tylko nowe dokumenty)**:
```bash
# 1) Przetworzenie nowych plików do JSON
python helpers/parse_knowledge_base.py

# 2) Aktualizacja Qdrant (inkrementalna)
python helpers/update_knowledge.py
```

### Czyszczenie kolekcji Qdrant

```bash
python helpers/delete_qdrant_collection.py
```

## Dodawanie dokumentów do bazy wiedzy

**Pierwsza instalacja**:
1. Dodaj pliki do `chatbot-baza-wiedzy-nowa/<kategoria>/`
2. Obsługiwane formaty: `.pdf`, `.docx`, `.doc`, `.txt`
3. Uruchom `helpers/parse_knowledge_base.py`
4. (Opcjonalnie) uzupełnij QA pairs w `helpers/add_qa_pairs.py` i uruchom skrypt
5. Wczytaj dane do Qdrant: `helpers/load_knowledge_base.py` (pełny load)

**Regularna aktualizacja**:
1. Dodaj nowe pliki do `chatbot-baza-wiedzy-nowa/<kategoria>/`
2. Uruchom `helpers/parse_knowledge_base.py`
3. Uruchom `helpers/update_knowledge.py` (dodaje tylko nowe dokumenty)

**Różnica**: `update_knowledge.py` jest bezpieczniejsze i szybsze niż `load_knowledge_base.py`

## Struktura projektu

```
agents/agent1_student/
├── app.py                       # FastAPI + RAG
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── knowledge_manager.py         # CLI do zarządzania bazą wiedzy
├── agent1_flow.json             # Workflow Node-RED
├── chatbot-baza-wiedzy-nowa/    # Źródła dokumentów
├── knowledge/                   # Przetworzone JSON-y do Qdrant
├── helpers/                     # Skrypty zarządzania
│   ├── parse_knowledge_base.py      # Parser plików
│   ├── load_knowledge_base.py       # Pełny load do Qdrant
│   ├── update_knowledge.py          # Inkrementalna aktualizacja
│   ├── verify_knowledge_base.py     # Walidacja bazy
│   ├── check_knowledge_quality.py   # Analiza jakości
│   ├── add_qa_pairs.py              # QA pairs
│   ├── delete_qdrant_collection.py  # Czyszczenie kolekcji
│   ├── init_log_collections.py      # Inicjalizacja kolekcji logów
│   └── query_logger.py              # Logowanie zapytań i QA
├── LOGGING_EXAMPLES.md          # Przykłady użycia logów
├── img/                         # Obrazy i zrzuty ekranu
│   ├── user_guide/              # Obrazy do instrukcji użytkownika
│   │   └── chat.png, home.png, login.png, menu.png
│   └── mobile_tests/            # Screenshoty testów mobilnych
│       └── IMG_*.PNG
├── Test reports/
│   ├── AGENT1_IMPLEMENTATION_REPORT.md # Raport dla promotora
│   ├── TEST_REPORT.md           # Raport testów
│   ├── LOGGING_TEST_REPORT.md   # Raport testów logowania
│   └── mobile_tests.md          # Testy mobilne
├── User guide/
│   ├── user_guide.md            # Instrukcja użytkownika
│   └── QUICK_START.md           # Szybki start
└── README.md                    # Ten plik
```

## Dokumentacja API (skrót)

### Kompatybilność z Ollama
```
POST /api/chat
POST /api/generate
GET  /api/tags
GET  /api/version
GET  /api/ps
```

### Endpointy dodatkowe
```
POST /run
POST /publish-workflow
GET  /admin/logs/queries/stats
GET  /admin/logs/qa/stats
GET  /admin/logs/queries/search
GET  /admin/logs/categories
```

## System Logowania i Kategoryzacji

Agent1 Student automatycznie loguje wszystkie zapytania użytkowników i odpowiedzi do bazy Qdrant. System wykrywa kategorię zapytania na podstawie słów kluczowych.

### Kategorie

System rozpoznaje 5 kategorii:
- **dane_osobowe** – zmiana danych, adresu, email, RODO
- **egzaminy** – egzaminy, obrona pracy dyplomowej, sesja, oceny
- **rekrutacja** – rekrutacja, zmiana kierunku, rezygnacja, wznowienie
- **stypendia** – stypendium socjalne, rektora, dla niepełnosprawnych, Erasmus
- **urlopy_zwolnienia** – urlopy dziekańskie, zwolnienia z WF

### Kolekcje Qdrant

- **agent1_student** – główna baza wiedzy (dokumenty + QA pairs)
- **agent1_query_logs** – logi zapytań użytkowników
- **agent1_qa_logs** – logi par pytanie-odpowiedź z RAG scores

### Struktura kolekcji i przykładowe dane

#### agent1_student (baza wiedzy)
Przechowuje dokumenty i QA pairs jako punkty z wektorem embeddingu oraz metadanymi.

Przykładowy payload dokumentu:
```json
{
  "id": "uuid",
  "text": "Treść dokumentu lub fragmentu...",
  "metadata": {
    "category": "stypendia",
    "source_file": "FAQ - Najczęściej zadawane pytania dotyczące stypendiów.md",
    "file_type": "md",
    "chunk_index": 2
  }
}
```

Przykładowy payload QA pair:
```json
{
  "id": "uuid",
  "text": "Pytanie: Jak mogę uzyskać stypendium socjalne?\nOdpowiedź: Aby uzyskać stypendium socjalne...",
  "metadata": {
    "type": "qa",
    "category": "stypendia",
    "question": "Jak mogę uzyskać stypendium socjalne?",
    "answer": "Aby uzyskać stypendium socjalne..."
  }
}
```

#### agent1_query_logs (logi zapytań)
Każde zapytanie użytkownika jest logowane z embeddingiem zapytania.

Przykładowy payload:
```json
{
  "query": "Jak mogę uzyskać stypendium socjalne?",
  "category": "stypendia",
  "timestamp": "2026-02-06T16:59:12.826175",
  "user_id": "anonymous",
  "log_id": "uuid",
  "model": "mistral:7b"
}
```

#### agent1_qa_logs (logi pytanie‑odpowiedź)
Każda para pytanie‑odpowiedź jest logowana z embeddingiem całego kontekstu Q+A oraz źródłami RAG.

Przykładowy payload:
```json
{
  "query": "Jak mogę uzyskać stypendium socjalne?",
  "answer": "Aby uzyskać stypendium socjalne...",
  "category": "stypendia",
  "timestamp": "2026-02-06T16:59:13.123456",
  "user_id": "anonymous",
  "log_id": "uuid",
  "sources": [
    {"file": "stypendia/FAQ - Najczęściej zadawane pytania dotyczące stypendiów.md", "chunk": 1}
  ],
  "rag_score": 0.854,
  "model": "mistral:7b"
}
```

### Endpointy administracyjne

#### Statystyki zapytań
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

#### Statystyki QA
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

#### Wyszukiwanie podobnych zapytań
```bash
curl "http://localhost:8001/admin/logs/queries/search?query=stypendium&limit=5"
```
Zwraca listę historycznych zapytań podobnych do podanego wraz z RAG score.

#### Lista kategorii
```bash
curl http://localhost:8001/admin/logs/categories
```
Zwraca wszystkie kategorie ze słowami kluczowymi.

### Inicjalizacja kolekcji logów

Przy pierwszym uruchomieniu systemu należy zainicjalizować kolekcje logów:
```bash
python init_log_collections.py
```

## Troubleshooting

### Ollama nie odpowiada
**Objaw:** Brak odpowiedzi z `http://localhost:11434`

**Rozwiązanie:**
1. Uruchom Ollama
2. Pobierz modele: `ollama pull mistral:7b`, `ollama pull nomic-embed-text`

### Qdrant nie startuje
**Objaw:** Brak połączenia z Qdrant

**Rozwiązanie:**
1. Sprawdź Docker
2. `docker compose down && docker compose up -d --build`
3. Logi: `docker logs qdrant`

### Brak wyników w odpowiedziach
**Objaw:** Chatbot odpowiada „Nie mam tej informacji w bazie wiedzy”

**Rozwiązanie:**
1. Sprawdź czy kolekcja `agent1_student` istnieje w Qdrant
2. Uruchom `load_knowledge_base.py`
3. Zweryfikuj `knowledge/all_documents.json`

## Performance tips

- **LLM**: `mistral:7b` – dobry balans szybkości i jakości
- **Embeddings**: `nomic-embed-text` (768D)
- **Batch size**: 20
- **Top-K**: 2 (domyślnie)
- **Limit odpowiedzi**: `num_predict=80`

## Wsparcie

Dokumentacja API (FastAPI): http://localhost:8001/docs

## Maintainers
- Adam Siehen (adamsiehen)
