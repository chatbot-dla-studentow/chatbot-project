# Przykłady Użycia - System Logowania i Kategoryzacji
## Agent1 Student Query & QA Logging

---

## 1. Podstawowe zapytania do chatbota

### Przykład 1: Zapytanie o stypendium (kategoria: stypendia)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [
      {"role": "user", "content": "Jak mogę uzyskać stypendium socjalne?"}
    ],
    "stream": false
  }' | jq -r '.message.content'
```

**Odpowiedź:**
```
Aby uzyskać stypendium socjalne, należy złożyć wniosek w wyznaczonym terminie. 
Wniosek powinien zawierać dane osobowe, zaświadczenie o dochodach rodziny oraz wymagane dokumenty.
```

**Kategoria wykryta:** stypendia  
**RAG Score:** ~0.85

---

### Przykład 2: Zapytanie o egzamin (kategoria: egzaminy)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [
      {"role": "user", "content": "Jak przebiega egzamin dyplomowy?"}
    ],
    "stream": false
  }' | jq -r '.message.content'
```

**Kategoria wykryta:** egzaminy  
**RAG Score:** ~0.75

---

### Przykład 3: Zapytanie o dane osobowe (kategoria: dane_osobowe)
```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [
      {"role": "user", "content": "Jak zmienić adres zamieszkania w systemie?"}
    ],
    "stream": false
  }' | jq -r '.message.content'
```

**Kategoria wykryta:** dane_osobowe

---

## 2. Pobieranie statystyk

### Statystyki zapytań
```bash
curl http://localhost:8001/admin/logs/queries/stats | jq '.'
```

**Przykładowa odpowiedź:**
```json
{
  "success": true,
  "data": {
    "total_queries": 150,
    "categories": {
      "stypendia": 45,
      "egzaminy": 38,
      "dane_osobowe": 32,
      "rekrutacja": 20,
      "urlopy_zwolnienia": 10,
      "unknown": 5
    }
  }
}
```

---

### Statystyki QA (z RAG score)
```bash
curl http://localhost:8001/admin/logs/qa/stats | jq '.'
```

**Przykładowa odpowiedź:**
```json
{
  "success": true,
  "data": {
    "total_qa_pairs": 150,
    "categories": {
      "stypendia": 45,
      "egzaminy": 38,
      "dane_osobowe": 32,
      "rekrutacja": 20,
      "urlopy_zwolnienia": 10,
      "unknown": 5
    },
    "average_rag_score": 0.742
  }
}
```

**Interpretacja:**
- `total_qa_pairs`: 150 - liczba wszystkich zalogowanych par pytanie-odpowiedź
- `average_rag_score`: 0.742 - średni wynik RAG (wysoki = dobre dopasowanie dokumentów)

---

## 3. Wyszukiwanie podobnych zapytań

### Szukaj zapytań podobnych do "stypendium"
```bash
curl "http://localhost:8001/admin/logs/queries/search?query=stypendium&limit=5" | jq '.'
```

**Odpowiedź:**
```json
{
  "success": true,
  "query": "stypendium",
  "count": 5,
  "results": [
    {
      "query": "Jak mogę uzyskać stypendium socjalne?",
      "category": "stypendia",
      "timestamp": "2026-02-06T16:59:12.826175",
      "score": 0.8445173
    },
    {
      "query": "Jakie dokumenty potrzebne do stypendium rektora?",
      "category": "stypendia",
      "timestamp": "2026-02-06T15:30:45.123456",
      "score": 0.7892341
    },
    {
      "query": "Ile wynosi stypendium dla niepełnosprawnych?",
      "category": "stypendia",
      "timestamp": "2026-02-06T14:22:10.987654",
      "score": 0.7234567
    }
  ]
}
```

**Zastosowanie:**
- Znajdowanie często zadawanych pytań (FAQ)
- Analiza trendów w pytaniach studentów
- Wykrywanie duplikatów zapytań

---

### Szukaj zapytań o "obronie pracy"
```bash
curl "http://localhost:8001/admin/logs/queries/search?query=obrona%20pracy&limit=10" | jq '.'
```

**Parametry:**
- `query` - tekst zapytania (URL encoded jeśli zawiera spacje)
- `limit` - maksymalna liczba wyników (domyślnie 10)

---

## 4. Lista kategorii ze słowami kluczowymi

```bash
curl http://localhost:8001/admin/logs/categories | jq '.'
```

**Odpowiedź:**
```json
{
  "success": true,
  "count": 5,
  "categories": [
    {
      "id": "dane_osobowe",
      "keywords_count": 8,
      "keywords": [
        "dane", "osobowe", "zmiana", "adres", 
        "telefon", "email", "RODO", "ochrona"
      ]
    },
    {
      "id": "egzaminy",
      "keywords_count": 8,
      "keywords": [
        "egzamin", "obrona", "praca", "dyplomowa", 
        "sesja", "reklamacja", "ocena", "termin"
      ]
    },
    {
      "id": "rekrutacja",
      "keywords_count": 7,
      "keywords": [
        "rekrutacja", "przyjęcie", "zmiana", "kierunek", 
        "rezygnacja", "wznowienie", "skreślenie"
      ]
    },
    {
      "id": "stypendia",
      "keywords_count": 6,
      "keywords": [
        "stypendium", "socjalne", "rektora", 
        "niepełnosprawni", "sportowcy", "erasmus"
      ]
    },
    {
      "id": "urlopy_zwolnienia",
      "keywords_count": 5,
      "keywords": [
        "urlop", "dziekański", "zwolnienie", "WF", "nieobecność"
      ]
    }
  ]
}
```

**Zastosowanie:**
- Dokumentacja dostępnych kategorii
- Debugowanie wykrywania kategorii
- Rozszerzanie słowników kategorii

---

## 5. Skrypty Pythonowe

### Inicjalizacja kolekcji logów
```bash
# Jednorazowe - przy pierwszym uruchomieniu
python init_log_collections.py
```

**Wynik:**
```
Inicjalizacja kolekcji logów w Qdrant...

✓ Utworzono kolekcję 'agent1_query_logs' - Logi zapytań użytkowników
✓ Utworzono kolekcję 'agent1_qa_logs' - Logi par pytanie-odpowiedź

Inicjalizacja zakończona pomyślnie!
Utworzono 2 kolekcje do logowania.
```

---

### Testowanie kategoryzacji (Python)
```python
from query_logger import QueryLogger, CATEGORIES
from qdrant_client import QdrantClient

# Inicjalizacja
client = QdrantClient(host="localhost", port=6333)
logger = QueryLogger(client, embedding_func=lambda x: [0.1]*768)

# Testuj wykrywanie kategorii
queries = [
    "Jak mogę uzyskać stypendium?",
    "Kiedy jest egzamin dyplomowy?",
    "Chcę zmienić adres email",
    "Jak złożyć podanie o urlop dziekański?"
]

for q in queries:
    category = logger.detect_category(q)
    print(f"'{q}' → {category}")
```

**Wynik:**
```
'Jak mogę uzyskać stypendium?' → stypendia
'Kiedy jest egzamin dyplomowy?' → egzaminy
'Chcę zmienić adres email' → dane_osobowe
'Jak złożyć podanie o urlop dziekański?' → urlopy_zwolnienia
```

---

## 6. Integracja z systemem monitoringu

### Skrypt do codziennego raportowania
```bash
#!/bin/bash
# daily_report.sh

echo "=== Raport dzienny - $(date) ===" > report.txt

# Statystyki zapytań
echo -e "\n## Statystyki zapytań:" >> report.txt
curl -s http://localhost:8001/admin/logs/queries/stats | jq '.data' >> report.txt

# Statystyki QA
echo -e "\n## Statystyki QA:" >> report.txt
curl -s http://localhost:8001/admin/logs/qa/stats | jq '.data' >> report.txt

# Wyślij raport
cat report.txt | mail -s "Agent1 - Raport dzienny" admin@example.com
```

---

### Monitoring RAG score
```python
import requests
import time

def check_rag_score():
    """Sprawdza średni RAG score i alarmuje jeśli jest niski"""
    response = requests.get("http://localhost:8001/admin/logs/qa/stats")
    data = response.json()
    
    avg_score = data['data']['average_rag_score']
    
    if avg_score < 0.5:
        print(f"ALERT: Niski RAG score: {avg_score}")
        # Wyślij alert (email, Slack, etc.)
    else:
        print(f"OK: RAG score: {avg_score}")

# Uruchom co godzinę
while True:
    check_rag_score()
    time.sleep(3600)  # 1 godzina
```

---

## 7. Analiza danych w Qdrant Dashboard

### Przeglądanie kolekcji
1. Otwórz: http://localhost:6333/dashboard
2. Wybierz kolekcję `agent1_query_logs` lub `agent1_qa_logs`
3. Sprawdź:
   - Liczbę punktów (Points count)
   - Wymiar wektorów (Vector size: 768)
   - Payloady przykładowych dokumentów

### Przykładowy payload - agent1_query_logs
```json
{
  "query": "Jak mogę uzyskać stypendium socjalne?",
  "category": "stypendia",
  "timestamp": "2026-02-06T16:59:12.826175",
  "user_id": "anonymous",
  "log_id": "550e8400-e29b-41d4-a716-446655440000",
  "model": "mistral:7b"
}
```

### Przykładowy payload - agent1_qa_logs
```json
{
  "query": "Jak mogę uzyskać stypendium socjalne?",
  "answer": "Aby uzyskać stypendium socjalne...",
  "category": "stypendia",
  "timestamp": "2026-02-06T16:59:13.123456",
  "user_id": "anonymous",
  "log_id": "660e8400-e29b-41d4-a716-446655440111",
  "sources": [
    {"file": "stypendia/FAQ - stypendium socjalne.md", "chunk": 1},
    {"file": "stypendia/Stawki stypendiów.md", "chunk": 3}
  ],
  "rag_score": 0.854,
  "model": "mistral:7b"
}
```

---

## 8. Export danych do analizy

### Export logów zapytań (curl + jq)
```bash
# Pobierz wszystkie logi z Qdrant
curl -X POST http://localhost:6333/collections/agent1_query_logs/points/scroll \
  -H "Content-Type: application/json" \
  -d '{"limit": 1000, "with_payload": true, "with_vector": false}' \
  | jq '.result.points[].payload' > query_logs.json
```

### Analiza w Python
```python
import json
import pandas as pd
from collections import Counter

# Załaduj logi
with open('query_logs.json') as f:
    logs = [json.loads(line) for line in f]

# Analiza kategorii
df = pd.DataFrame(logs)
print(df['category'].value_counts())

# Top 10 najczęstszych pytań
print(df['query'].value_counts().head(10))

# Rozkład czasowy
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp').resample('1H')['query'].count().plot()
```

---

## 9. Rozwiązywanie problemów

### Problem: Kategoria "unknown" dla oczywistych zapytań

**Przyczyna:** Brak słowa kluczowego w słowniku

**Rozwiązanie:**
1. Sprawdź aktualne słowa kluczowe:
```bash
curl http://localhost:8001/admin/logs/categories | jq '.categories[] | select(.id=="stypendia")'
```

2. Dodaj nowe słowa kluczowe w `query_logger.py`:
```python
CATEGORIES = {
    "stypendia": ["stypendium", "socjalne", "rektora", "niepełnosprawni", 
                  "sportowcy", "erasmus", "wsparcie", "pomoc finansowa"],  # NOWE
    ...
}
```

3. Przebuduj i zrestartuj:
```bash
docker compose up -d --build
```

---

### Problem: Niski RAG score

**Przyczyna:** Słabe dopasowanie dokumentów w bazie wiedzy

**Diagnostyka:**
```bash
# Sprawdź średni score
curl http://localhost:8001/admin/logs/qa/stats | jq '.data.average_rag_score'
```

**Rozwiązanie:**
1. Dodaj więcej dokumentów do bazy wiedzy
2. Popraw chunking (mniejsze fragmenty)
3. Dodaj więcej Q&A pairs:
```bash
python add_qa_pairs.py
python load_knowledge_base.py
```

---

## 10. Best Practices

### 1. Regularne czyszczenie logów
```bash
# Co miesiąc - usuń stare logi (>30 dni)
# TODO: Zaimplementować retention policy
```

### 2. Backup kolekcji Qdrant
```bash
# Backup volume Qdrant
docker run --rm -v agent1_student_qdrant_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant_backup_$(date +%Y%m%d).tar.gz /data
```

### 3. Monitoring alertów
- RAG score < 0.5 → sprawdź bazę wiedzy
- Kategoria "unknown" > 20% → rozszerz słowniki
- Total queries/day = 0 → sprawdź czy system działa

### 4. Analiza trendów
```bash
# Co tydzień - sprawdź najpopularniejsze kategorie
curl http://localhost:8001/admin/logs/queries/stats | \
  jq '.data.categories | to_entries | sort_by(.value) | reverse | .[0:5]'
```

---

**Dokument stworzony:** 6 lutego 2026  
**Wersja:** 1.0  
**Agent:** Agent1 Student

## Maintainers
- Adam Siehen (adamsiehen)
