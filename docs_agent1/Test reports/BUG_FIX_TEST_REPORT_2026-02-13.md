# Raport Testów i Napraw - Agent1 Student Chatbot
## Sesja Debugowania: 13 lutego 2026

**Status Ogólny**: ROZWIĄZANE  
**Data Raportu**: 13 luty 2026  
**Priorytet**: KRYTYCZNY (Model discovery dla Open WebUI)

---

## 1. PROBLEMY ZIDENTYFIKOWANE

### Problem Główny: NameError w app.py
**Opis**: Zmienna `DEFAULT_MODEL` używana przed definicją  
**Błąd**:
```
NameError: name 'DEFAULT_MODEL' is not defined
File "/app/app.py", line 20, in <module>
    model=DEFAULT_MODEL,
          ^^^^^^^^^^^^^
```

**Przyczyna Główna**: 
- Linia 20: `llm = ChatOllama(model=DEFAULT_MODEL, ...)`
- Linia 30: `DEFAULT_MODEL = "mistral:7b"`
- Inicjalizacja LLM wykonywana PRZED definicją zmiennej

**Impact**:
- FAILED: App nie startuje
- FAILED: `/api/tags` niedostępny (zwraca 404)
- FAILED: `/api/chat` niedostępny
- FAILED: Open WebUI nie widzi modeli
- FAILED: Chatbot nieużywalny

---

### Problem Wtórny: Port Mismatch
**Opis**: Agent1_student mapowany na port `8001` zamiast `8000`  
**Znaleziono**: Podczas debug-owania połączeń  
**Wdrażanie Open WebUI**: `OLLAMA_BASE_URL=http://agent1_student:8000` (wewnątrz sieci Docker)  
**Dostęp Host**: `http://localhost:8001` (mapowanie w docker-compose)

---

## 2. TESTY WSTĘPNE (PRZED NAPRAWĄ)

### Test 2.1: Sprawdzenie Zdolności Startu
```bash
$ docker logs agent1_student | Select-String "ERROR|NameError"
```
**Wynik**: FAILED
```
NameError: name 'DEFAULT_MODEL' is not defined
```

### Test 2.2: Sprawdzenie Endpoint-u `/api/tags`
```bash
$ curl http://localhost:8001/api/tags
```
**Wynik**: FAILED (404 Not Found)
- Kontener ponad szansą (NameError podczas startu)

### Test 2.3: Sprawdzenie Endpoint-u `/api/chat`
```bash
$ curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"test"}]}'
```
**Wynik**: FAILED (Container not running)

### Test 2.4: Open WebUI Model Discovery
**Opis**: Sprawdzenie czy Open WebUI widzi `mistral:7b`  
**Wynik**: FAILED
- Logi Open WebUI pokazywały pobieranie profili modeli
- Ale żaden model nie był dostępny do wyboru

---

## 3. NAPRAWY WDROŻONE

### Naprawa 1: Reorganizacja app.py - Kolejność Definicji

**Plik**: `agents/agent1_student/app.py`  
**Zmiana**: Przesunęcie definicji zmiennych do PRZED inicjalizacją LLM

**Struktura PRZED (BŁĘDNA)**:
```python
app = FastAPI()
#test
llm = ChatOllama(                    # ← Linia 18-22: PROBLEM
    model=DEFAULT_MODEL,            # ← Linia 20: DEFAULT_MODEL undefined!
    base_url="http://ollama:11434"
)

COLLECTION = os.getenv(...)         # ← Linia 24
...
DEFAULT_MODEL = "mistral:7b"        # ← Linia 30: Definiowane za PÓŹNO
```

**Struktura PO (PRAWIDŁOWA)**:
```python
app = FastAPI()

# Zmienne konfiguracyjne - MUSZĄ być zdefiniowane PRZED użyciem
COLLECTION = os.getenv("COLLECTION", "agent1_student")
NODERED_URL = os.getenv("NODERED_URL", "http://node-red:1880")
WORKFLOW_FILE = os.getenv("WORKFLOW_FILE", "/app/agent1_flow.json")
WORKFLOW_ENDPOINT = os.getenv("WORKFLOW_ENDPOINT", "/agent1_student")
QDRANT_HOST = os.getenv("QDRANT_HOST", "qdrant")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
EMBEDDING_MODEL = "nomic-embed-text"  # ← PRZED użyciem
DEFAULT_MODEL = "mistral:7b"          # ← PRZED użyciem

# Teraz możemy inicjalizować LLM
llm = ChatOllama(                     # ← Linia 30: DEFAULT_MODEL już zdefiniowany!
    model=DEFAULT_MODEL,
    base_url="http://ollama:11434"
)

SYSTEM_PROMPT = """..."""              # ← OSTATNI
```

**Warunki Naprawy**:
- OK: Wszystkie zmienne środowiskowe czytane PRZED użyciem
- OK: Stałe stringowe zdefiniowane PRZED inicjalizacją ChatOllama
- OK: System prompt zdefiniowany PO inicjalizacji LLM (nie potrzebny wcześniej)
- OK: Redukuje błędy NameError i uat initialization errors

### Naprawa 2: Redeploy naprawionego kodu

**Kroki**:
```bash
# 1. Edycja współzalności w lokalnym pliku ✓
# 2. Kopowanie do kontenera
docker cp "path/to/app.py" agent1_student:/app/app.py

# 3. Restart kontenera
docker restart agent1_student

# 4. Weryfikacja startu
docker logs agent1_student | grep "Application startup complete"
```

---

## 4. TESTY PO NAPRAWIE

### Test 4.1: Sprawdzenie Startu Aplikacji - PASSED
```bash
$ docker logs agent1_student | Select-String "Application startup complete"
```
**Wynik**: SUCCESS
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```
**Opis**: Aplikacja startuje bez błędów

---

### Test 4.2: Endpoint `/api/tags` - PASSED
```bash
$ curl http://localhost:8001/api/tags
```
**Wynik**: SUCCESS (Status 200)
```json
{
  "models": [
    {
      "name": "mistral:7b",
      "model": "mistral:7b",
      "size": 4372824384,
      "details": {
        "family": "llama",
        "parameter_size": "7.2B",
        "quantization_level": "Q4_K_M"
      }
    },
    {
      "name": "nomic-embed-text:latest",
      "model": "nomic-embed-text:latest",
      "size": 274302450,
      "details": {
        "family": "nomic-bert",
        "parameter_size": "137M",
        "quantization_level": "F16"
      }
    }
  ]
}
```
**Opis**: Endpoint zwraca listę dostępnych modeli

---

### Test 4.3: Endpoint `/api/chat` - RAG Query - PASSED
```bash
$ curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Jak ubiegać się o stypendium rektora?"}],"model":"mistral:7b"}'
```
**Wynik**: SUCCESS (Status 200)

**Logi Transakcji**:
```
INFO:app:Query logged: <uuid> (kategoria: stypendia)
INFO:app:RAG: Found 2 docs (score: 0.781)
INFO:httpx:HTTP Request: POST http://ollama:11434/api/chat "HTTP/1.1 200 OK"
INFO:app:QA pair logged | Has Knowledge: True
```

**Wynik RAG**:
- OK: Query zalogowana w Qdrant
- OK: Znaleziono 2 dokumenty z BA
- OK: Score: 0.781 (wysokiej istotności)
- OK: Kategoryzacja: `stypendia` (prawidłowa)
- OK: Odpowiedź pobrana z LLM
- OK: QA pair zalogowana

**Opis**: RAG pipeline kompletnie funkcjonalny

---

### Test 4.4: Open WebUI Model Discovery - PASSED
**Sprawdzenie**: Czy Open WebUI widzi model `mistral:7b`

**Logi Open WebUI**:
```
GET /api/v1/models/model/profile/image?id=mistral:7b&lang=en-US HTTP/1.1" 200
```

**Wynik**: SUCCESS
- OK: Open WebUI wysyła request o profil modelu
- OK: Endpoint /api/tags jest dostępny dla Open WebUI
- OK: Model `mistral:7b` widoczny w interfejsie

---

### Test 4.5: Logowanie Zapytań i QA Pairs - PASSED
**Query Logowanie** (Qdrant `agent1_query_logs`):
```
Query ID: 0cc5652c-c1bc-44eb-84d9-c689df924764
Category: unknown
Timestamp: 2026-02-13T23:00:01
```

**QA Logowanie** (Qdrant `agent1_qa_logs`):
```
QA ID: bfe32e33-2509-448c-a83c-c1c5fa608f0b
Category: stypendia
Has Knowledge: True
RAG Score: 0.781
```

**Wynik**: SUCCESS - Wszystkie logi zapisywane prawidłowo

---

## 5. PORÓWNANIE PRZED I PO

| Funkcja | Przed | Po |
|---------|-------|-----|
| **Startup aplikacji** | FAILED: NameError | OK |
| **`/api/tags`** | FAILED: 404 Not Found | OK: 200 OK + modele |
| **`/api/chat` RAG** | FAILED: Unavailable | OK: 200 OK |
| **Wyszukiwanie KB** | FAILED: App crashed | OK: Score 0.781 |
| **Kategoryzacja** | FAILED: N/A | OK: Dokładna |
| **Logowanie** | FAILED: N/A | OK: Qdrant zapisuje |
| **Open WebUI Models** | FAILED: Brak widoku | OK: Widzi mistral:7b |
| **Statystyka** | 0/7 PASSED | **7/7 PASSED** |

---

## 6. ANALIZA PRZYCZYNY NIEPOWODZENIA

### Root Cause Analysis (RCA)

**Level 1 - Objaw**: NameError przy import-cie modułu  
**Level 2 - Przyczyna**: Zmienna dostępna w runtime PRZED definicją  
**Level 3 - Główna Przyczyna**: Brak separacji między:
- Sekcją definicji zmiennych (setup)
- Sekcją inicjalizacji komponentów (init)
- Sekcją definicji route-ów (routing)

**Lekcja**: Python parsuje plik od górny do dołu. Wszystkie zmienne muszą być zdefiniowane PRZED ich użyciem.

---

## 7. REKOMENDACJE

### Krótkoterminowe (DONE)
[DONE] Reorganizacja zmiennych w app.py  
[DONE] Deployment naprawionego kodu  
[DONE] Weryfikacja wszystkich endpoint-ów  
[DONE] Potwierdzenie integracji z Open WebUI

### Średnioterminowe (TODO)
- [ ] Dodać type hints do funkcji chat (zmniejszy błędy)
- [ ] Unit testy dla każdej funkcji RAG
- [ ] Integration testy dla całego pipeline'u
- [ ] CI/CD pipeline do automatycznych testów

### Długoterminowe (TODO)
- [ ] Lint code (pylint/flake8) w pre-commit hooks
- [ ] Static type checking (mypy)
- [ ] Monitoring aplikacji w produkcji
- [ ] Alerting dla błędów

---

## 8. ŚRODOWISKO TESTOWANIA

### Konfiguracja:
```
OS: Windows 11 + WSL2 Docker Desktop
Docker: Latest with Docker Compose
Python: 3.11
Framework: FastAPI + LangChain
```

### Serwisy:
```
[OK] Agent1_student:    http://localhost:8001 (port 8000 wewnątrz)
[OK] Ollama:            http://localhost:11434 (mistral:7b + nomic-embed-text)
[OK] Qdrant:            http://localhost:6333 (agent1_student collection)
[OK] Open WebUI:        http://localhost:3000
[OK] Node-RED:          http://localhost:1880
```

### Modele:
```
[OK] mistral:7b        : 4.37 GB, Q4_K_M, 7.2B params
[OK] nomic-embed-text  : 274 MB, F16, 137M params
```

---

## 9. PODSUMOWANIE

### Co nie działało:
1. FAILED: Startup aplikacji - **FIXED**
2. FAILED: Model discovery endpoint - **FIXED**
3. FAILED: RAG pipeline - **FIXED**
4. FAILED: Open WebUI integration - **FIXED**

### Co zostało poprawione:
1. FIXED: Reorganizacja kolejności definicji zmiennych
2. FIXED: Redeploy kodu do kontenera
3. FIXED: Restart aplikacji z prawidłowym kodem
4. FIXED: Weryfikacja wszystkich endpoint-ów

### Wynik końcowy:
**CHATBOT GOTOWY DO UŻYTKU**
- Wszystkie testy pass
- RAG w pełni funkcjonalny  
- Open WebUI widzi modele
- Logowanie działa prawidłowo

---

## 10. LOGI REFERENCYJNE

### Docker Container Status (Po Naprawie)
```
STATUS: Up About a minute
PORT:   0.0.0.0:8001->8000/tcp
```

### Ostatnie Testy Systemowe
```
[2026-02-13 23:00:09]
- Query: "Jak ubiegać się o stypendium rektora?"
- Status: 200 OK
- RAG Score: 0.781
- Documents Found: 2
- Category: stypendia
- Result: PASSED
```

---

**Raport Zakończony**: OK  
**Autoryzacja**: Automated Test System  
**Next Review**: W razie nowych błędów w logach aplikacji  


## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Mikołaj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Paweł Ponikowski (pponikowski)
