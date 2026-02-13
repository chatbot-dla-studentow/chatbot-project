# Architektura Systemu Multi-Agent

## Przegląd Architektury

System chatbota dla studentów oparty jest na architekturze multi-agent, gdzie **Agent1 Student** pełni rolę centralnego agenta wiedzy, a pozostałe agenty (Agent2-5) mogą z niego korzystać dla specyficznych zadań.

```
┌─────────────────────────────────────────────────────────────┐
│                      Node-RED Orchestrator                   │
│                    (Routing & Workflow)                      │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─────────────┐
               │             │
               ▼             ▼
    ┌──────────────────────────────────┐
    │   Agent1 Student (CORE)          │
    │   - RAG (Qdrant + Ollama)        │
    │   - Knowledge Base (215 docs)    │
    │   - Query Logging                │
    │   - Source Attribution           │
    └──────────────┬───────────────────┘
                   │
         ┌─────────┼─────────┬─────────┐
         │         │         │         │
         ▼         ▼         ▼         ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Agent 2 │ │Agent 3 │ │Agent 4 │ │Agent 5 │
    │Ticket  │ │Analytics│ │  BOS   │ │Security│
    │        │ │         │ │        │ │        │
    └────────┘ └────────┘ └────────┘ └────────┘
         │         │         │         │
         └─────────┴─────────┴─────────┘
                   │
                   ▼
          [Komunikują się z Agent1]
```

## Komponenty Systemu

### 1. Agent1 Student (Core Knowledge Agent)

**Rola**: Centralny agent wiedzy z pełnym RAG i bazą danych.

**Funkcjonalności**:
- **RAG (Retrieval-Augmented Generation)**
  - Vector database: Qdrant
  - Embeddings: nomic-embed-text (768 wymiarów)
  - Search threshold: 0.25
  - Limit wyników: 2 dokumenty

- **Baza Wiedzy**
  - 215 dokumentów w kategorii studenckich
  - 5 kategorii: dane_osobowe, egzaminy, rekrutacja, stypendia, urlopy_zwolnienia
  - Format: JSON z metadanymi

- **Logowanie**
  - Query logs: agent1_query_logs (zapytania użytkowników)
  - QA logs: agent1_qa_logs (pary pytanie-odpowiedź)
  - Auto-detekcja kategorii

- **Źródła Odpowiedzi**
  - Response zawiera `sources` object:
    ```json
    {
      "sources": {
        "documents": ["stypendia/stypendium_rektora.txt", "..."],
        "score": 0.856,
        "category": "stypendia"
      }
    }
    ```

**Endpoints**:
- `POST /api/chat` - Główny endpoint RAG (kompatybilny z Ollama)
- `GET /health` - Status aplikacji
- `GET /admin/logs/queries` - Historia zapytań
- `GET /admin/logs/qa-pairs` - Historia odpowiedzi

**Technologie**:
- FastAPI
- LangChain (OllamaEmbeddings, ChatOllama)
- Qdrant Client
- httpx

**Port**: 8001

### 2. Agent2 Ticket (Ticket Classification)

**Rola**: Klasyfikacja zgłoszeń studenckich.

**Funkcjonalność**:
- Bazowa klasyfikacja zgłoszeń
- **Komunikacja z Agent1**: Jeśli zgłoszenie dotyczy procedur studenckich (keywords: stypendium, egzamin, urlop)
- Zwraca klasyfikację + wiedzę z Agent1

**Endpoint**:
- `POST /run` - Klasyfikuje zgłoszenie
  ```json
  {
    "input": "Jak ubiegać się o stypendium rektora?",
    "user_id": "student123"
  }
  ```

**Response**:
```json
{
  "ticket_classification": {
    "category": "akademickie",
    "priority": "medium",
    "knowledge_from_agent1": "Stypendium rektora...",
    "sources": {...}
  }
}
```

**Komunikacja z Agent1**:
```python
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{AGENT1_URL}/api/chat",
        json={
            "messages": [{"role": "user", "content": query}],
            "model": "mistral:7b"
        }
    )
```

**Port**: 8002

### 3. Agent3 Analytics (Data Analysis)

**Rola**: Analityka danych studenckich.

**Funkcjonalność**:
- Generowanie insightów
- **Komunikacja z Agent1**: Dla statystyk związanych ze studentami
- Zwraca analizę + dane z Agent1

**Endpoint**:
- `POST /run` - Analizuje dane

**Response**:
```json
{
  "insights": {
    "summary": "Analiza stypendiów...",
    "data_from_agent1": "Statystyki...",
    "sources": {...}
  }
}
```

**Port**: 8003

### 4. Agent4 BOS (Biuro Obsługi Studenta)

**Rola**: Wsparcie procedur BOS.

**Funkcjonalność**:
- **Zawsze komunikuje się z Agent1** - pełny proxy
- Generuje odpowiedzi/drafty na podstawie wiedzy Agent1

**Endpoint**:
- `POST /run` - Przetwarza zapytanie BOS

**Response**:
```json
{
  "draft": "Odpowiedź z Agent1...",
  "sources": {
    "documents": [...],
    "score": 0.95
  }
}
```

**Port**: 8004

### 5. Agent5 Security (Bezpieczeństwo i RODO)

**Rola**: Walidacja zgodności z RODO i politykami bezpieczeństwa.

**Funkcjonalność**:
- Sprawdzanie compliance
- **Komunikacja z Agent1**: Dla polityk RODO i danych osobowych
- Zwraca audit + polityki z Agent1

**Endpoint**:
- `POST /run` - Sprawdza zgodność

**Response**:
```json
{
  "audit": {
    "status": "checked",
    "compliance": "verified",
    "policy_from_agent1": "Polityka RODO...",
    "sources": {...}
  }
}
```

**Port**: 8005

### 6. Node-RED Orchestrator

**Rola**: Orkiestracja workflow i routing zapytań.

**Funkcjonalności**:
- Routing zapytań do odpowiednich agentów
- Workflow management (BPMN conversion)
- Monitoring i logging flow

**Endpoints**:
- `POST /agent1_student` - Endpoint dla Agent1
- HTTP flows dla pozostałych agentów

**Port**: 1880

### 7. Qdrant Vector Database

**Rola**: Przechowywanie embeddingów i dokumentów.

**Kolekcje**:
- `agent1_student` - 215 dokumentów (główna baza wiedzy)
- `agent1_query_logs` - Logi zapytań
- `agent1_qa_logs` - Logi odpowiedzi

**Konfiguracja**:
- Vector size: 768 (nomic-embed-text)
- Distance: COSINE
- Index: HNSW (default)

**Port**: 6333

### 8. Ollama LLM Server

**Rola**: Serwer modeli AI.

**Modele**:
- `mistral:7b` - Główny model LLM
- `nomic-embed-text` - Model embeddings (~274MB)

**Port**: 11434

### 9. Open WebUI

**Rola**: Frontend dla użytkowników.

**Funkcjonalność**:
- Interfejs czatu
- Komunikacja z Agent1 przez `/api/chat`
- Wyświetlanie sources (jeśli dostępne)

**Port**: 3000

## 🔄 Przepływ Danych

### Scenariusz 1: Zapytanie Bezpośrednie (Open WebUI → Agent1)

```
1. User: "Jak ubiegać się o stypendium rektora?"
   │
   ▼
2. Open WebUI → POST /api/chat (Agent1:8001)
   │
   ▼
3. Agent1:
   a. Query Logger: log_query() → agent1_query_logs
   b. RAG: embed query (nomic-embed-text)
   c. Qdrant: search (collection: agent1_student, limit=2)
   d. Context: 2 dokumenty (score > 0.25)
   e. LLM: mistral:7b + context → answer
   f. Query Logger: log_qa_pair() → agent1_qa_logs
   │
   ▼
4. Response:
   {
     "message": {"content": "Stypendium rektora..."},
     "sources": {
       "documents": ["stypendia/stypendium_rektora.txt"],
       "score": 0.856,
       "category": "stypendia"
     }
   }
   │
   ▼
5. Open WebUI: Wyświetla odpowiedź + źródła
```

### Scenariusz 2: Zapytanie przez Agent BOS (Agent4 → Agent1)

```
1. Request: POST /run (Agent4:8004)
   {
     "input": "Jak złożyć podanie o urlop dziekański?"
   }
   │
   ▼
2. Agent4:
   - Wykrywa że dotyczy procedur
   - Forward do Agent1
   │
   ▼
3. httpx → POST /api/chat (Agent1:8001)
   │
   ▼
4. Agent1: [pełny workflow RAG jak w sc. 1]
   │
   ▼
5. Agent4: Otrzymuje response z Agent1
   │
   ▼
6. Response:
   {
     "draft": "Aby złożyć podanie...",
     "sources": {...},
     "agent": "agent4_bos"
   }
```

### Scenariusz 3: Klasyfikacja Zgłoszenia (Agent2 + Agent1)

```
1. Request: POST /run (Agent2:8002)
   {
     "input": "Problem z logowaniem do systemu stypendiów"
   }
   │
   ▼
2. Agent2:
   - Keyword match: "stypendi" → zapytaj Agent1
   │
   ▼
3. httpx → POST /api/chat (Agent1:8001)
   │
   ▼
4. Agent1: RAG search + response
   │
   ▼
5. Agent2: Klasyfikacja + wiedza z Agent1
   │
   ▼
6. Response:
   {
     "ticket_classification": {
       "category": "akademickie",
       "priority": "medium",
       "knowledge_from_agent1": "System stypendiów...",
       "sources": {...}
     }
   }
```

## 🌐 Networking

### Docker Network: ai_network

Wszystkie kontenery są w sieci `ai_network (172.18.0.0/16)`.

**Rozwiązywanie nazw (DNS)**:
- `agent1_student` → Agent1 (8001)
- `agent2_ticket` → Agent2 (8002)
- `agent3_analytics` → Agent3 (8003)
- `agent4_bos` → Agent4 (8004)
- `agent5_security` → Agent5 (8005)
- `qdrant` → Qdrant (6333)
- `ollama` → Ollama (11434)
- `node-red` → Node-RED (1880)

### Zmienne Środowiskowe (docker-compose.yml)

**Agent1**:
```yaml
environment:
  - QDRANT_HOST=qdrant
  - QDRANT_PORT=6333
  - OLLAMA_URL=http://ollama:11434
  - COLLECTION=agent1_student
```

**Agent2-5**:
```yaml
environment:
  - AGENT1_URL=http://agent1_student:8001
```

## Monitoring i Logging

### Agent1 Logs

**Query Logs** (`agent1_query_logs`):
```python
{
  "log_id": "uuid",
  "query": "Jak zmienić dane osobowe?",
  "category": "dane_osobowe",  # auto-detected
  "timestamp": "2026-02-10T22:00:00Z",
  "user_id": "anonymous"
}
```

**QA Logs** (`agent1_qa_logs`):
```python
{
  "log_id": "uuid",
  "query": "Jak zmienić dane osobowe?",
  "answer": "Aby zmienić dane...",
  "category": "dane_osobowe",
  "sources": ["dane_osobowe/zmiana_danych.txt"],
  "score": 0.89,
  "timestamp": "2026-02-10T22:00:05Z"
}
```

### Admin Endpoints (Agent1)

**GET /admin/logs/queries/stats**:
```json
{
  "success": true,
  "data": {
    "total_queries": 156,
    "categories": {
      "stypendia": 45,
      "egzaminy": 38,
      "dane_osobowe": 28
    }
  }
}
```

**GET /admin/logs/queries?limit=10**:
Lista ostatnich zapytań.

**GET /admin/logs/qa-pairs?limit=10**:
Lista ostatnich odpowiedzi z sources.

## Security

### CORS
- Agent1: Konfigurowalny CORS dla Open WebUI
- Agent2-5: Internal only (ai_network)

### Rate Limiting
- TODO: Implementacja rate limiting na /api/chat

### Data Privacy
- Query Logging: user_id anonimizowane
- RODO compliance: Agent5 do walidacji
- Sources: Transparentność źródeł odpowiedzi

## Deployment

### Development

```bash
# 1. Start Qdrant
cd qdrant && docker compose up -d

# 2. Start Ollama
cd ollama && docker compose up -d

# 3. Załaduj bazę wiedzy (Agent1)
cd agents/agent1_student
docker compose up -d
docker exec agent1_student python helpers/load_knowledge_base.py

# 4. Start pozostałych agentów
cd agents/agent2_ticket && docker compose up -d
cd agents/agent3_analytics && docker compose up -d
cd agents/agent4_bos && docker compose up -d
cd agents/agent5_security && docker compose up -d

# 5. Start Node-RED
cd nodered && docker compose up -d

# 6. Start Open WebUI
cd Open_WebUI && docker compose up -d
```

### Production

- TODO: Kubernetes deployment
- TODO: Load balancing dla Agent1
- TODO: Backup strategy dla Qdrant
- TODO: Model versioning dla Ollama

## 📈 Skalowanie

### Vertical Scaling (Agent1)

Agent1 jest najbardziej obciążony - można zwiększyć zasoby:
```yaml
resources:
  limits:
    cpus: '2.0'
    memory: 4G
  reservations:
    cpus: '1.0'
    memory: 2G
```

### Horizontal Scaling

Multiple replicas Agent1 z load balancerem:
```yaml
deploy:
  replicas: 3
  update_config:
    parallelism: 1
```

### Caching

Dodać Redis dla cache'owania:
- Częste zapytania
- Embeddingi (wymiar: 768)
- Search results z Qdrant

## Integracja z Innymi Grupami

**Agent2-5 - Punkty Integracji**:

1. **Komunikacja HTTP**:
   - URL: `http://agent1_student:8001/api/chat`
   - Method: POST
   - Headers: `Content-Type: application/json`

2. **Request Format**:
   ```json
   {
     "messages": [
       {"role": "user", "content": "Pytanie"}
     ],
     "model": "mistral:7b",
     "stream": false
   }
   ```

3. **Response Format**:
   ```json
   {
     "message": {
       "role": "assistant",
       "content": "Odpowiedź..."
     },
     "sources": {
       "documents": ["path/file.txt"],
       "score": 0.95,
       "category": "kategoria"
     }
   }
   ```

4. **Error Handling**:
   - Timeout: 30s
   - Retry: 3 attempts
   - Fallback: Basic response bez RAG

## 📝 Best Practices

### Dla Agent1

1. **RAG Tuning**:
   - Score threshold: 0.25-0.3 (balans precision/recall)
   - Limit documents: 2 (kontekst nie za duży)
   - Context length: 600 znaków per doc

2. **Logging**:
   - Zawsze loguj query (dla statystyk)
   - Loguj QA tylko dla successful responses
   - Auto-detect category (fallback: "unknown")

3. **Performance**:
   - Ollama timeout: 120s
   - Qdrant timeout: 10s
   - Async wszystkie I/O

### Dla Agent2-5

1. **Komunikacja**:
   - Używaj async httpx
   - Timeout 30s
   - Handle errors gracefully

2. **Keywords**:
   - Definiuj jasne keywords dla routing
   - Przykład: Agent2 → ["stypendium", "egzamin", "urlop"]

3. **Response**:
   - Przekaż sources z Agent1
   - Dodaj własne metadane (agent, category)

## Troubleshooting

### Problem: Agent2-5 nie mogą połączyć się z Agent1

**Diagnoza**:
```bash
docker exec agent2_ticket curl http://agent1_student:8001/health
```

**Rozwiązanie**:
1. Sprawdź czy Agent1 działa: `docker ps | grep agent1`
2. Sprawdź network: `docker network inspect ai_network`
3. Sprawdź AGENT1_URL w docker-compose.yml

### Problem: Brak sources w odpowiedzi

**Diagnoza**:
- Sprawdź score: GET /admin/logs/qa-pairs
- Jeśli score < 0.25 → brak sources

**Rozwiązanie**:
1. Obniż threshold w search_knowledge_base()
2. Dodaj więcej dokumentów do bazy
3. Sprawdź jakość embeddingów

### Problem: Powolne odpowiedzi Agent1

**Diagnoza**:
```bash
docker logs agent1_student | grep "RAG:"
```

**Rozwiązanie**:
1. Zmniejsz limit documents (2 → 1)
2. Zmniejsz context length (600 → 400)
3. Optymalizuj Ollama options (num_ctx, temperature)

## 📅 Roadmap

- [ ] Agent1: Implementacja cache (Redis)
- [ ] Agent1: Streaming responses z sources
- [ ] Agent2-5: Rozbudowa logiki specific per agent
- [ ] Node-RED: Full BPMN workflow support
- [ ] Monitoring: Grafana dashboards
- [ ] Testing: Integration tests dla komunikacji między agentami
- [ ] Deployment: Kubernetes configurations

---

**Autor**: Agent1 Student Team  
**Data**: 10 lutego 2026  
**Wersja**: 1.0

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Mikołaj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Paweł Ponikowski (pponikowski)
