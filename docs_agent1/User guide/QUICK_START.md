# Przewodnik Szybki Start - Baza Wiedzy

## Co zostało zrobione?

1. **Sparsowano pliki** z `chatbot-baza-wiedzy-nowa/` (txt, docx, doc, pdf)
2. **Utworzono folder** `./agents/agent1_student/knowledge/` z 5 kategoriami
3. **Dodano przykładowe pytania i odpowiedzi** (17 QA pairs)
4. **Przygotowano format** kompatybilny z Qdrant
5. **Dodano system logowania** zapytań i odpowiedzi w Qdrant
6. **Dodano wykrywanie kategorii** zapytań użytkowników

## Statystyki

- **Łącznie dokumentów**: 220 (203 sparsowanych + 17 QA pairs)
- **Kategorie**: 5 (dane_osobowe, egzaminy, rekrutacja, stypendia, urlopy_zwolnienia)
- **Format**: JSON z UTF-8 (pełne wsparcie polskich znaków)
- **Rozmiar**: 804KB
- **Logi Qdrant**: 2 kolekcje (agent1_query_logs, agent1_qa_logs)
- **Embeddingi**: 768D (nomic-embed-text)

## Struktura

```
agents/agent1_student/
├── knowledge/                              # FOLDER Z BAZĄ WIEDZY
│   ├── all_documents.json                  # Wszystkie dokumenty
│   ├── dane_osobowe/
│   │   ├── dane_osobowe_documents.json     # 77 chunks
│   │   └── dane_osobowe_qa_pairs.json      # 3 QA
│   ├── egzaminy/
│   │   ├── egzaminy_documents.json         # 16 chunks
│   │   └── egzaminy_qa_pairs.json          # 4 QA
│   ├── rekrutacja/
│   │   ├── rekrutacja_documents.json       # 56 chunks
│   │   └── rekrutacja_qa_pairs.json        # 4 QA
│   ├── stypendia/
│   │   ├── stypendia_documents.json        # 56 chunks
│   │   └── stypendia_qa_pairs.json         # 4 QA
│   └── urlopy_zwolnienia/
│       ├── urlopy_zwolnienia_documents.json # 15 chunks
│       └── urlopy_zwolnienia_qa_pairs.json  # 2 QA
├── chatbot-baza-wiedzy-nowa/               # Źródłowe pliki (txt, docx, pdf)
├── knowledge_manager.py                     # CLI do zarządzania bazą wiedzy
├── helpers/                                 # Skrypty zarządzania
│   ├── parse_knowledge_base.py              # Parser plików źródłowych
│   ├── add_qa_pairs.py                      # Dodaje QA pairs
│   ├── verify_knowledge_base.py             # Weryfikacja struktury
│   ├── load_knowledge_base.py               # Pełny load do Qdrant
│   ├── update_knowledge.py                  # Aktualizacja inkrementalna
│   ├── delete_qdrant_collection.py          # Czyści kolekcję w Qdrant
│   ├── init_log_collections.py              # Inicjalizacja kolekcji logów
│   └── query_logger.py                      # Logowanie zapytań i QA
├── LOGGING_EXAMPLES.md                      # Przykłady użycia logów
├── img/                                     # Obrazy
│   ├── user_guide/                          # User guide images
│   │   └── chat.png, home.png, login.png, menu.png
│   └── mobile_tests/                        # Mobile screenshots
│       └── IMG_*.PNG
├── Test reports/
│   ├── AGENT1_IMPLEMENTATION_REPORT.md      # Raport dla promotora
│   ├── TEST_REPORT.md                       # Raport testów
│   ├── LOGGING_TEST_REPORT.md               # Raport testów logowania
│   └── mobile_tests.md                      # Testy mobilne
└── User guide/
    ├── user_guide.md                        # Instrukcja użytkownika
    └── QUICK_START.md                       # Ten plik
```

## Jak użyć?

### 1. Uruchomienie usługi Docker

```bash
cd agents/agent1_student
docker compose up -d --build
```

Dostęp do serwisów:
- API: http://localhost:8001
- Open WebUI: http://localhost:3000
- Qdrant: http://localhost:6333/dashboard

### 2. Weryfikacja bazy wiedzy (opcjonalne)

```bash
cd agents/agent1_student
python helpers/verify_knowledge_base.py
```

### 3. Wczytanie bazy wiedzy do Qdrant

```bash
cd agents/agent1_student
python helpers/load_knowledge_base.py
```

### 4. Inicjalizacja kolekcji logów (jednorazowo)

```bash
cd agents/agent1_student
python helpers/init_log_collections.py
```

### 5. Testowanie zapytań

```bash
# Podstawowe zapytanie
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistral:7b",
    "messages": [{"role": "user", "content": "Jak mogę uzyskać stypendium?"}],
    "stream": false
  }' | jq '.message.content'

# Sprawdzenie logów - statystyki zapytań
curl http://localhost:8001/admin/logs/queries/stats | jq '.'

# Sprawdzenie logów - statystyki QA
curl http://localhost:8001/admin/logs/qa/stats | jq '.'

# Wyszukiwanie podobnych zapytań
curl "http://localhost:8001/admin/logs/queries/search?query=stypendium&limit=5" | jq '.'

# Lista kategorii
curl http://localhost:8001/admin/logs/categories | jq '.'
```

### 6. Dodanie nowych dokumentów

#### Opcja A: Nowe pliki źródłowe
```bash
# 1. Dodaj pliki do chatbot-baza-wiedzy-nowa/<kategoria>/
# 2. Uruchom parser
cd agents/agent1_student
python helpers/parse_knowledge_base.py

# 3. Dodaj QA (opcjonalne - edytuj add_qa_pairs.py najpierw)
python helpers/add_qa_pairs.py

# 4. Wczytaj do Qdrant
python helpers/load_knowledge_base.py
```

#### Opcja B: Edycja bezpośrednia JSON
```bash
# Edytuj pliki w knowledge/<kategoria>/*.json
# Następnie wczytaj do Qdrant
cd agents/agent1_student
python helpers/load_knowledge_base.py
```

## Przykładowe pytania w bazie

### Dane osobowe
- Jak zmienić swoje dane osobowe w systemie?
- Jakie są zasady ochrony danych osobowych dla studentów?
- Gdzie zgłosić zmianę numeru telefonu lub maila?

### Egzaminy
- Jak wygląda procedura obrony pracy dyplomowej?
- Kiedy odbywa się harmonogram obron prac dyplomowych?
- Jak złożyć reklamację na ocenę z egzaminu?
- Czy mogę poprosić o przedłużenie sesji egzaminacyjnej?

### Rekrutacja
- Jakie są warunki przyjęcia na studia?
- Czy mogę zmienić kierunek studiów?
- Jak wznowić naukę po przerwaniu studiów?
- Czy mogę zrezygnować ze studiów?

### Stypendia
- Jakie rodzaje stypendiów są dostępne dla studentów?
- Jak ubiegać się o stypendium?
- Jaka jest wysokość stypendiów w bieżącym semestrze?
- Czy osoby niepełnosprawne mogą ubiegać się o wyższe stypendium?

### Urlopy/Zwolnienia
- Kiedy mogę wziąć urlop dziekański?
- Czy mogę być zwolniony z zajęć z wychowania fizycznego?

## Skrypty

| Skrypt | Opis | Użycie |
|--------|------|--------|
| `parse_knowledge_base.py` | Parsuje pliki źródłowe (txt/docx/pdf) | `helpers/parse_knowledge_base.py` |
| `add_qa_pairs.py` | Dodaje przykładowe pytania/odpowiedzi | `helpers/add_qa_pairs.py` |
| `verify_knowledge_base.py` | Weryfikuje strukturę i wyświetla stats | `helpers/verify_knowledge_base.py` |
| `load_knowledge_base.py` | Wczytuje dokumenty do Qdrant | `helpers/load_knowledge_base.py` |
| `update_knowledge.py` | Aktualizacja inkrementalna | `helpers/update_knowledge.py` |
| `init_log_collections.py` | Tworzy kolekcje logów w Qdrant | `helpers/init_log_collections.py` |

## Konfiguracja load_knowledge_base.py

```python
KNOWLEDGE_BASE_PATH = "./knowledge"          # Główny folder JSON
COLLECTION_NAME = "agent1_student"           # Nazwa kolekcji w Qdrant
EMBEDDING_MODEL = "nomic-embed-text"         # Model Ollama do embeddingów
```

## Czyszczenie kolekcji Qdrant

Aby usunąć starą kolekcję przed wczytaniem nowej:

```bash
cd agents/agent1_student
python helpers/delete_qdrant_collection.py
```

Kolekcja jest automatycznie usuwana i tworzona na nowo przy każdym uruchomieniu `helpers/load_knowledge_base.py`.

## Logowanie i kategorie

System automatycznie loguje zapytania i odpowiedzi do Qdrant:
- **agent1_query_logs** – zapytania użytkowników
- **agent1_qa_logs** – pary pytanie‑odpowiedź + RAG score

Endpointy administracyjne:
- `GET /admin/logs/queries/stats`
- `GET /admin/logs/qa/stats`
- `GET /admin/logs/queries/search`
- `GET /admin/logs/categories`

## Tips

1. **Chunking**: Długie dokumenty są automatycznie dzielone na ~500 znakowe fragmenty
2. **Metadane**: Każdy dokument ma category, source_file, file_type w metadata
3. **QA pairs**: Są zarówno w osobnych plikach jak i wplecione w documents.json
4. **UTF-8**: Pełne wsparcie polskich znaków
5. **UUID**: Każdy dokument ma unikalny ID dla śledzenia

## Następne kroki

Teraz możesz:
- Uruchomić `helpers/load_knowledge_base.py` aby wczytać wszystko do Qdrant
- Testować chatbota z nową bazą wiedzy
- Dodawać nowe dokumenty i pytania
- Monitorować jakość odpowiedzi i iterować

---

**Utworzono**: 6 lutego 2026
**Status**: Zaktualizowano pod logowanie i kategorie

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
