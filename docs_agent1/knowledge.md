# Baza Wiedzy - Documentation

## Przegląd

Baza wiedzy Agent1 Student zawiera dokumenty z kategorii akademickich, zoptymalizowane pod kątem retrieval-augmented generation (RAG). System wykorzystuje Qdrant jako vector database oraz Ollama do generowania embeddingów.

## Struktura Bazy Wiedzy

### Katalogi

```
agents/agent1_student/
├── chatbot-baza-wiedzy-nowa/    # Pliki źródłowe (txt, docx, pdf)
│   ├── dane_osobowe/
│   ├── egzaminy/
│   ├── rekrutacja/
│   ├── stypendia/
│   └── urlopy_zwolnienia/
├── knowledge/                    # Sparsowane dokumenty JSON
│   ├── all_documents.json       # Wszystkie dokumenty (główny plik)
│   ├── dane_osobowe/
│   │   ├── dane_osobowe_documents.json
│   │   └── dane_osobowe_qa_pairs.json
│   ├── egzaminy/
│   ├── rekrutacja/
│   ├── stypendia/
│   └── urlopy_zwolnienia/
└── helpers/                      # Skrypty zarządzania
    ├── __init__.py
    ├── parse_knowledge_base.py
    ├── load_knowledge_base.py
    ├── update_knowledge.py
    ├── verify_knowledge_base.py
    ├── check_knowledge_quality.py
    ├── add_qa_pairs.py
    ├── init_log_collections.py
    ├── delete_qdrant_collection.py
    └── query_logger.py
```

### Kategorie Dokumentów

| Kategoria | Opis | Przykładowe Tematy |
|-----------|------|-------------------|
| **dane_osobowe** | Zarządzanie danymi osobowymi | Zmiana adresu, telefonu, RODO |
| **egzaminy** | Egzaminy i obrony | Sesja, obrona pracy, reklamacje |
| **rekrutacja** | Proces rekrutacyjny | Przyjęcie, zmiana kierunku, wznowienie |
| **stypendia** | Wsparcie finansowe | Stypendium rektora, socjalne, Erasmus |
| **urlopy_zwolnienia** | Nieobecności i zwolnienia | Urlop dziekański, zwolnienia z WF |

### Statystyki (stan aktualny)

- **Łącznie dokumentów**: 220
- **Kolekcje Qdrant**: 
  - `agent1_student` - 215 punktów (główna baza wiedzy)
  - `agent1_query_logs` - 0 punktów (logi zapytań)
  - `agent1_qa_logs` - 0 punktów (logi par Q&A)

## Format Dokumentu

### Struktura JSON

Każdy dokument w bazie wiedzy ma następującą strukturę:

```json
{
  "id": "uuid-v4",
  "source_file": "nazwa_pliku.txt",
  "category": "kategoria",
  "content": "Treść dokumentu...",
  "metadata": {
    "parsed_at": "2026-02-10T12:00:00",
    "file_type": "txt",
    "chunk_index": 0,
    "total_chunks": 1
  }
}
```

### Pola Dokumentu

| Pole | Typ | Opis |
|------|-----|------|
| `id` | string | Unikalny identyfikator (UUID v4) |
| `source_file` | string | Nazwa pliku źródłowego |
| `category` | string | Kategoria dokumentu |
| `content` | string | Treść dokumentu (pełna lub chunk) |
| `metadata` | object | Dodatkowe metadane |

### QA Pairs (Pytanie-Odpowiedź)

```json
{
  "qa_pairs": [
    {
      "question": "Jak zmienić dane osobowe?",
      "answer": "Należy złożyć podanie w dekanatcie...",
      "category": "dane_osobowe",
      "type": "procedure"
    }
  ]
}
```

## Skrypty Zarządzania

Wszystkie skrypty znajdują się w folderze `helpers/` i są dostępne przez interfejs `knowledge_manager.py`.

### 1. parse_knowledge_base.py

**Funkcja**: Parsuje pliki źródłowe i konwertuje do JSON.

**Wspierane formaty**:
- `.txt` - pliki tekstowe (UTF-8)
- `.docx` - dokumenty Word (wymaga python-docx)
- `.doc` - starsze dokumenty Word
- `.pdf` - pliki PDF (wymaga PyPDF2)

**Proces**:
1. Skanuje katalog `chatbot-baza-wiedzy-nowa/`
2. Wykrywa kategorię na podstawie ścieżki pliku
3. Ekstrahuje tekst z każdego pliku
4. Tworzy dokumenty JSON z metadanymi
5. Zapisuje do `knowledge/`

**Chunking**: Automatycznie dzieli długie dokumenty na fragmenty (chunks) aby zmieścić się w kontekście embeddingów.

**Uruchomienie**:
```bash
python helpers/parse_knowledge_base.py
# lub przez knowledge_manager.py (opcja 1)
```

### 2. load_knowledge_base.py

**Funkcja**: Ładuje dokumenty JSON do Qdrant z embeddingami.

**Proces**:
1. Wczytuje `knowledge/all_documents.json`
2. Sprawdza dostępność Ollama
3. Pull modelu `nomic-embed-text` (jeśli brak)
4. Generuje embedding dla każdego dokumentu
5. Tworzy/odtwarza kolekcję `agent1_student`
6. Upsertuje punkty do Qdrant

**Konfiguracja**:
```python
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = "nomic-embed-text"  # ~274MB, idealny dla 16GB RAM
```

**Model Embeddings**:
- **nomic-embed-text**: Lekki model (~274MB)
- Rozmiar wektora: 768 wymiarów
- Distance: COSINE

**Uruchomienie**:
```bash
docker exec agent1_student python helpers/load_knowledge_base.py
# lub przez knowledge_manager.py (opcja 2)
```

**UWAGA**: Ten skrypt usuwa istniejącą kolekcję i tworzy nową. Dla bezpieczniejszej aktualizacji użyj `update_knowledge.py`.

### 3. update_knowledge.py

**Funkcja**: Inkrementalna aktualizacja bazy wiedzy - dodaje tylko nowe dokumenty.

**Proces**:
1. Wczytuje dokumenty JSON z `knowledge/all_documents.json`
2. Pobiera wszystkie istniejące dokumenty z Qdrant
3. Oblicza MD5 hash dla każdego dokumentu (content + path)
4. Porównuje nowe dokumenty z istniejącymi
5. Dodaje TYLKO nowe dokumenty (bez usuwania starych)
6. Generuje raport z liczbą dodanych dokumentów

**Zalety**:
- **Bezpieczne**: Nie usuwa istniejących dokumentów
- **Szybkie**: Przetwarza tylko nowe dokumenty
- **Wydajne**: Idealne do regularnych aktualizacji
- **Automatyczne**: Wykrywa duplikaty na podstawie hash

**Różnica vs load_knowledge_base.py**:
| Aspekt | load_knowledge_base.py | update_knowledge.py |
|--------|------------------------|---------------------|
| Operacja | Pełny reload (usuwa kolekcję) | Inkrementalna aktualizacja |
| Bezpieczeństwo | Usuwa wszystkie dane | Zachowuje istniejące |
| Szybkość | Wolniejszy (wszystkie docs) | Szybszy (tylko nowe) |
| Użycie | Pierwsza instalacja | Regularne aktualizacje |

**Przykładowy output**:
```
======================================================================
Inkrementalna Aktualizacja Bazy Wiedzy
Dodaje tylko nowe dokumenty bez usuwania istniejących
======================================================================

1. Wczytywanie dokumentów JSON z ./knowledge...
  Wczytano 220 dokumentów z all_documents.json
  RAZEM: 220 dokumentów do sprawdzenia

2. Sprawdzanie Ollama (http://localhost:11434)...
   ✓ Model nomic-embed-text gotowy (wymiar: 768)

3. Łączenie z Qdrant (localhost:6333)...
   ✓ Połączono z kolekcją 'agent1_student'

4. Pobieranie istniejących dokumentów...
  Pobrano: 215 dokumentów...
  Znaleziono 215 unikalnych dokumentów w Qdrant

5. Filtrowanie nowych dokumentów...
   Znaleziono 0 nowych dokumentów
  Pominięto 215 istniejących dokumentów

Baza wiedzy jest aktualna - brak nowych dokumentów do dodania!
```

**Uruchomienie**:
```bash
docker exec agent1_student python helpers/update_knowledge.py
# lub przez knowledge_manager.py (opcja 3)
```

**Kiedy używać**:
- Dodajesz nowe pliki do chatbot-baza-wiedzy-nowa/
- Regularne aktualizacje bazy wiedzy
- Chcesz zachować istniejące dokumenty
- Pierwsza instalacja (użyj load_knowledge_base.py)
- Chcesz przebudować całą kolekcję

### 4. verify_knowledge_base.py

**Funkcja**: Weryfikuje strukturę i kompletność bazy wiedzy.

**Sprawdza**:
- Istnienie `all_documents.json`
- Strukturę JSON (pola: id, content, category)
- Pliki per-kategoria (documents.json, qa_pairs.json)
- Kompletność metadanych

**Raport**:
```
RAPORT WERYFIKACJI BAZY WIEDZY
==============================
STATYSTYKI OGÓLNE:
  Łączna liczba dokumentów: 220
  Łączna liczba QA pair: 17
   Liczba kategorii: 5

KATEGORII ZNALEZIONE: dane_osobowe, egzaminy, rekrutacja, stypendia, urlopy_zwolnienia

SZCZEGÓŁY PO KATEGORII:
   DANE_OSOBOWE
   ├─ Dokumenty: 43 chunks
   ├─ QA pairs: 8
   └─ Pliki: [documents.json, qa_pairs.json]
   ...
```

**Uruchomienie**:
```bash
python helpers/verify_knowledge_base.py
# lub przez knowledge_manager.py (opcja 4)
```

### 5. check_knowledge_quality.py

**Funkcja**: Sprawdza jakość danych w Qdrant.

**Analiza**:
- **Duplikaty**: Wykrywa identyczne dokumenty (MD5 hash)
- **Kategoryzacja**: Sprawdza rozkład kategorii
- **Statystyki**: Liczba punktów, rozmiar kolekcji

**Przykładowy output**:
```
ANALIZA BAZY WIEDZY W QDRANT
==============================
Kolekcja: agent1_student
   Liczba punktów: 215
   Status: green

Pobrano 215 dokumentów z Qdrant

KATEGORIE:
   dane_osobowe: 43 dokumenty (20.0%)
   egzaminy: 52 dokumenty (24.2%)
   rekrutacja: 38 dokumenty (17.7%)
   stypendia: 55 dokumenty (25.6%)
   urlopy_zwolnienia: 27 dokumenty (12.5%)

DUPLIKATY:
   Znaleziono 0 duplikatów
```

**Uruchomienie**:
```bash
docker exec agent1_student python helpers/check_knowledge_quality.py
# lub przez knowledge_manager.py (opcja 5)
```

### 6. add_qa_pairs.py

**Funkcja**: Dodaje przykładowe pary pytanie-odpowiedź do bazy wiedzy.

**QA Pairs**:
- Predefiniowane pytania i odpowiedzi dla każdej kategorii
- Typ: `procedure` (procedury) lub `information` (informacje)
- Wzbogacają kontekst dla RAG

**Przykład**:
```python
{
    "question": "Jak zmienić swoje dane osobowe w systemie?",
    "answer": "Aby zmienić dane osobowe...",
    "category": "dane_osobowe",
    "type": "procedure"
}
```

**Uruchomienie**:
```bash
python helpers/add_qa_pairs.py
# lub przez knowledge_manager.py (opcja 6)
```

### 7. init_log_collections.py

**Funkcja**: Inicjalizuje kolekcje logów w Qdrant.

**Tworzy kolekcje**:
- `agent1_query_logs` - Logi zapytań użytkowników
- `agent1_qa_logs` - Logi par pytanie-odpowiedź

**Konfiguracja**:
- Rozmiar wektora: 768 (jak nomic-embed-text)
- Distance: COSINE
- Wymaga działającego Ollama (do testowego embeddingu)

**Uruchomienie**:
```bash
docker exec agent1_student python helpers/init_log_collections.py
# lub przez knowledge_manager.py (opcja 7)
```

### 8. delete_qdrant_collection.py

**Funkcja**: Usuwa kolekcję z Qdrant.

**UWAGA**: Operacja nieodwracalna!

**Uruchomienie**:
```bash
docker exec agent1_student python helpers/delete_qdrant_collection.py
# lub przez knowledge_manager.py (opcja 8 - wymaga potwierdzenia)
```

### 9. query_logger.py

**Funkcja**: Moduł do logowania zapytań i odpowiedzi w Qdrant.

**Klasa QueryLogger**:
```python
from helpers.query_logger import QueryLogger

logger = QueryLogger(qdrant_client, embedding_func)

# Loguj zapytanie
log_id = logger.log_query(
    query="Jak zmienić dane osobowe?",
    category="dane_osobowe",  # opcjonalne, auto-detect
    user_id="user123",
    metadata={"source": "web"}
)

# Loguj parę Q&A
qa_id = logger.log_qa_pair(
    query="Jak zmienić dane?",
    answer="Złóż podanie...",
    category="dane_osobowe",
    sources=[{"doc_id": "...", "score": 0.95}]
)
```

**Automatyczna detekcja kategorii**:
Jeśli nie podano kategorii, QueryLogger wykrywa ją na podstawie słów kluczowych:

```python
CATEGORIES = {
    "dane_osobowe": ["dane", "osobowe", "zmiana", "adres", "telefon"],
    "egzaminy": ["egzamin", "obrona", "praca", "sesja"],
    "rekrutacja": ["rekrutacja", "przyjęcie", "zmiana kierunek"],
    "stypendia": ["stypendium", "socjalne", "rektora"],
    "urlopy_zwolnienia": ["urlop", "zwolnienie", "WF"]
}
```

## 🖥️ Knowledge Manager CLI

**Uruchomienie**:
```bash
python knowledge_manager.py
```

**Menu**:
```
======================================================================
KNOWLEDGE MANAGER - Agent1 Student
======================================================================

ZARZĄDZANIE BAZĄ WIEDZY:
  1. Parse  - Parsuj pliki źródłowe (txt, docx, pdf) → JSON
  2. Load   - Załaduj dokumenty JSON do Qdrant + embeddingi (pełne)
  3. Update - Aktualizuj bazę (dodaj tylko nowe dokumenty)
  4. Verify - Weryfikuj strukturę i zawartość bazy wiedzy
  5. Check  - Sprawdź jakość danych w Qdrant (duplikaty)
  6. Add QA - Dodaj pary pytanie-odpowiedź

ZARZĄDZANIE KOLEKCJAMI:
  7. Init Logs - Inicjalizuj kolekcje logów (query_logs, qa_logs)
  8. Delete - Usuń kolekcję z Qdrant

INFORMACJE:
  9. Status - Pokaż status wszystkich kolekcji
  h. Help - Pokaż szczegółową pomoc
  0. Exit - Wyjdź
```

**Funkcje**:
- **Status** (opcja 9): Wyświetla wszystkie kolekcje w Qdrant z liczbą punktów
- **Help** (opcja h): Szczegółowa pomoc z workflow i przykładami

## 🔄 Workflow Zarządzania Bazą Wiedzy

### Inicjalne Ładowanie (Pierwsza Instalacja)

```bash
# 1. Parsuj pliki źródłowe
python knowledge_manager.py  # opcja 1

# 2. Weryfikuj strukturę
python knowledge_manager.py  # opcja 4

# 3. Załaduj do Qdrant (pełny load)
docker exec agent1_student python knowledge_manager.py  # opcja 2

# 4. Sprawdź jakość
docker exec agent1_student python knowledge_manager.py  # opcja 5
```

### Regularna Aktualizacja (Nowe Dokumenty)

```bash
# 1. Dodaj nowe pliki do chatbot-baza-wiedzy-nowa/

# 2. Parsuj nowe pliki
python knowledge_manager.py  # opcja 1

# 3. Aktualizuj bazę (tylko nowe dokumenty)
docker exec agent1_student python knowledge_manager.py  # opcja 3

# 4. Sprawdź kompletność
docker exec agent1_student python knowledge_manager.py  # opcja 5

# 5. Inicjalizuj logi (opcjonalnie)
docker exec agent1_student python knowledge_manager.py  # opcja 6
```

### Aktualizacja Bazy Wiedzy

**Dodanie nowych dokumentów (ZALECANE)**:
1. Dodaj pliki do odpowiedniego katalogu w `chatbot-baza-wiedzy-nowa/`
2. Uruchom `parse_knowledge_base.py` (opcja 1)
3. Uruchom `verify_knowledge_base.py` (opcja 4) - sprawdź błędy
4. Uruchom `update_knowledge.py` (opcja 3) - dodaje tylko nowe dokumenty

**Pełna przebudowa bazy (gdy potrzebne)**:
1. Dodaj/edytuj pliki w `chatbot-baza-wiedzy-nowa/`
2. Uruchom `parse_knowledge_base.py` (opcja 1)
3. Uruchom `load_knowledge_base.py` (opcja 2) - usuwa całą kolekcję

**Modyfikacja istniejących dokumentów**:
1. Edytuj plik w `chatbot-baza-wiedzy-nowa/`
2. Re-parsuj: `parse_knowledge_base.py` (opcja 1)
3. Usuń starą wersję dokumentu (jeśli potrzeba)
4. Dodaj nową: `update_knowledge.py` (opcja 3)

**RÓŻNICA update_knowledge.py vs load_knowledge.py**:
- `update_knowledge.py` - Bezpieczne, szybkie, zachowuje dane (zalecane)
- `load_knowledge_base.py` - Usuwa całą kolekcję, wolniejsze (tylko gdy konieczne)

### Monitorowanie i Analiza

```bash
# Sprawdź status kolekcji
python knowledge_manager.py  # opcja 9

# Analiza jakości
docker exec agent1_student python knowledge_manager.py  # opcja 5

# Przeglądanie logów zapytań (przez API lub Qdrant UI)
curl http://10.0.0.1:6333/collections/agent1_query_logs
```

## 🔌 Integracja z RAG

### Podstawowe Query

```python
from qdrant_client import QdrantClient
import requests

# Klient Qdrant
client = QdrantClient(host="qdrant", port=6333)

# Funkcja embeddingu
def get_embedding(text: str):
    response = requests.post(
        "http://ollama:11434/api/embeddings",
        json={"model": "nomic-embed-text", "prompt": text}
    )
    return response.json()["embedding"]

# Wyszukiwanie podobnych dokumentów
query = "Jak zmienić dane osobowe?"
query_vector = get_embedding(query)

results = client.search(
    collection_name="agent1_student",
    query_vector=query_vector,
    limit=5,
    score_threshold=0.7
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Category: {result.payload['category']}")
    print(f"Content: {result.payload['content'][:200]}...")
    print()
```

### RAG z Logowaniem

```python
from helpers.query_logger import QueryLogger

# Inicjalizacja loggera
logger = QueryLogger(client, get_embedding)

# 1. Loguj zapytanie
query = "Jak ubiegać się o stypendium?"
log_id = logger.log_query(query, user_id="user123")

# 2. Wyszukaj w bazie wiedzy
query_vector = get_embedding(query)
results = client.search(
    collection_name="agent1_student",
    query_vector=query_vector,
    limit=5
)

# 3. Generuj odpowiedź (Ollama/ChatGPT)
context = "\n".join([r.payload['content'] for r in results])
answer = generate_answer(query, context)

# 4. Loguj parę Q&A
sources = [{"doc_id": r.id, "score": r.score} for r in results]
qa_id = logger.log_qa_pair(query, answer, sources=sources)
```

### Podawanie Źródeł Odpowiedzi

```python
def format_sources(results):
    """Formatuje źródła do wyświetlenia użytkownikowi"""
    sources = []
    for i, result in enumerate(results, 1):
        sources.append({
            "index": i,
            "category": result.payload['category'],
            "file": result.payload.get('source_file', 'unknown'),
            "score": round(result.score, 3),
            "snippet": result.payload['content'][:150] + "..."
        })
    return sources

# Przykład odpowiedzi z źródłami
response = {
    "answer": "Aby ubiegać się o stypendium...",
    "sources": format_sources(results),
    "confidence": results[0].score if results else 0
}
```

## Zmienne Środowiskowe

| Zmienna | Default | Opis |
|---------|---------|------|
| `QDRANT_HOST` | localhost | Host Qdrant |
| `QDRANT_PORT` | 6333 | Port Qdrant |
| `OLLAMA_URL` | http://localhost:11434 | URL Ollama API |
| `COLLECTION_NAME` | agent1_student | Nazwa głównej kolekcji |

**W kontenerze Docker** (.env lub docker-compose.yml):
```yaml
environment:
  - QDRANT_HOST=qdrant
  - QDRANT_PORT=6333
  - OLLAMA_URL=http://ollama:11434
```

## 🚨 Troubleshooting

### Problem: "Cannot connect to Ollama"

**Rozwiązanie**:
```bash
# Sprawdź czy Ollama działa
curl http://ollama:11434/api/tags

# Sprawdź czy model jest pobrany
docker exec ollama ollama list

# Pull modelu jeśli brak
docker exec ollama ollama pull nomic-embed-text
```

### Problem: "Cannot connect to Qdrant"

**Rozwiązanie**:
```bash
# Sprawdź status kontenera
docker ps | grep qdrant

# Sprawdź logi
docker logs qdrant

# Sprawdź dostępność
curl http://qdrant:6333/collections
```

### Problem: "Brak dokumentów w knowledge/"

**Rozwiązanie**:
```bash
# Uruchom parser
python helpers/parse_knowledge_base.py

# Sprawdź czy pliki źródłowe istnieją
ls -la chatbot-baza-wiedzy-nowa/
```

### Problem: "Duplikaty w bazie"

**Rozwiązanie**:
```bash
# Uruchom check jakości
docker exec agent1_student python helpers/check_knowledge_quality.py

# Przeładuj bazę (usuwa duplikaty)
docker exec agent1_student python helpers/load_knowledge_base.py
```

## 📝 Best Practices

### 1. Organizacja Plików Źródłowych

- **Katalog per kategoria**: Wszystkie pliki danej kategorii w jednym folderze
- **Nazwy plików**: Opisowe, snake_case, bez spacji
- **Encoding**: UTF-8 (szczególnie dla plików .txt)
- **Aktualizacje**: Trzymaj kopie zapasowe przed modyfikacją

### 2. Chunking i Granularność

- Dokumenty > 1000 słów: Automatyczny chunking w parse_knowledge_base.py
- Małe dokumenty (<500 słów): Jeden dokument = jeden punkt w Qdrant
- QA pairs: Dodatkowe punkty dla precyzyjnych odpowiedzi

### 3. Kategoryzacja

- **Konsekwentne nazwy**: snake_case, małe litery
- **Jednoznaczność**: Jeden dokument = jedna kategoria
- **Słowa kluczowe**: Definiuj w `query_logger.py` dla auto-detection

### 4. Embeddingi

- **Model**: nomic-embed-text (lekki, wystarczający dla większości)
- **Alternatywy**: bge-large-en-v1.5 (większy, lepszy ale wolniejszy)
- **Spójność**: Ten sam model dla indeksowania i query

### 5. Logowanie

- **Query logs**: Zawsze loguj zapytania użytkowników
- **QA logs**: Loguj tylko finalne odpowiedzi (po weryfikacji)
- **Anonimizacja**: Używaj hashed user_id jeśli konieczne

### 6. Jakość Danych

- **Regularnie**: Uruchamiaj `check_knowledge_quality.py`
- **Weryfikuj**: Po każdej aktualizacji - `verify_knowledge_base.py`
- **Testuj**: Wypróbuj różne query przed deploymentem

## Powiązane Pliki

- [AGENT1_OVERVIEW.md](../AGENT1_OVERVIEW.md) - Główna dokumentacja techniczna
- [QUICK_START.md](./User guide/QUICK_START.md) - Szybki start
- [user_guide.md](./User guide/user_guide.md) - Instrukcja użytkownika
- [LOGGING_EXAMPLES.md](./LOGGING_EXAMPLES.md) - Przykłady logowania
- [TEST_REPORT.md](./Test reports/TEST_REPORT.md) - Raport testów
- [mobile_tests.md](./Test reports/mobile_tests.md) - Testy mobilne
- [app.py](../app.py) - Główna aplikacja FastAPI

## 📅 Historia Zmian

| Data | Wersja | Zmiany |
|------|--------|--------|
| 2026-02-10 | 1.0 | Utworzenie dokumentacji, reorganizacja do helpers/ |
| 2026-02-08 | 0.9 | Załadowanie 215 dokumentów do Qdrant |
| 2026-02-07 | 0.8 | Inicjalizacja kolekcji logów |

---

**Autor**: Agent1 Student Team  
**Ostatnia aktualizacja**: 10 lutego 2026  
**Status**: Active Development

## Maintainers
- Paweł Ponikowski (pponikowski)
