# Chatbot dla Studentów - System Multi-Agentowy

Inteligentny chatbot dla studentów uczelni wyższej wykorzystujący architekturę multi-agentową, RAG (Retrieval Augmented Generation) i lokalne modele LLM.

## 📋 Spis Treści

- [Opis Projektu](#opis-projektu)
- [Architektura Systemu](#architektura-systemu)
- [Lokalizacja na Serwerze](#lokalizacja-na-serwerze)
- [Szybki Start](#szybki-start)
- [Dokumentacja](#dokumentacja)
- [Zespół](#zespół)

## 🎯 Opis Projektu

System chatbota składa się z 5 wyspecjalizowanych agentów:
- **Agent1 (Student)** - Pytania studenckie (stypendia, BOS, harmonogramy)
- **Agent2 (Ticket)** - Zarządzanie zgłoszeniami
- **Agent3 (Analytics)** - Analityka i statystyki
- **Agent4 (BOS)** - Integracja z Biurem Obsługi Studenta
- **Agent5 (Security)** - Bezpieczeństwo i autoryzacja

**Główne funkcjonalności:**
- ✅ Konwersacje w języku naturalnym (mistral:7b)
- ✅ RAG - wyszukiwanie w bazie wiedzy (Qdrant)
- ✅ Orkiestracja workflow (Node-RED)
- ✅ Logowanie zapytań i odpowiedzi
- ✅ Interfejs webowy (Open WebUI)
- ✅ Bezpieczny dostęp (WireGuard VPN)

## 🏗️ Architektura Systemu

### Stack Technologiczny

**Backend:**
- Python 3.11 (FastAPI)
- Ollama + mistral:7b (7.2B parametrów, Q4_K_M)
- LangChain (orchestration)
- httpx (async HTTP client)

**Baza Wiedzy:**
- Qdrant (vector database)
- nomic-embed-text (embeddings)
- Kolekcje: agent1_student, queries_log, qa_pairs_log

**Frontend:**
- Open WebUI (chat interface)

**Orkiestracja:**
- Node-RED (workflow automation)
  - Wizualna orkiestracja przepływu danych między agentami
  - Editor flow dostępny przez przeglądarkę
  - Port: 1880 (http://10.0.0.1:1880)
  - Endpoint publikacji workflow w Agent1: POST /publish-workflow
  - Flow testowy: nodered/flow_test.json
  - Kontener: node-red (obraz nodered/node-red:latest)

**Infrastruktura:**
- Docker + Docker Compose
- WireGuard VPN
- iptables (firewall)
- Ubuntu 24.10 (VPS OVHcloud)

### Komponenty

```
┌─────────────────┐
│   Open WebUI    │ :3000
│  (Chat UI)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent1_Student │ :8001
│  (RAG + LLM)    │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼
┌────────┐ ┌────────┐ ┌───────┐ ┌─────────┐
│ Ollama │ │ Qdrant │ │Node   │ │ Agent   │
│:11434  │ │ :6333  │ │RED    │ │ 2-5     │
│        │ │        │ │:1880  │ │:8002-05 │
└────────┘ └────────┘ └───────┘ └─────────┘
```

## 📂 Lokalizacja na Serwerze

**Ścieżka projektu:**
```bash
/opt/chatbot-project
```

**Struktura katalogów:**
```
/opt/chatbot-project/
├── agents/
│   ├── agent1_student/     # Agent studencki (RAG)
│   ├── agent2_ticket/      # Agent ticketów
│   ├── agent3_analytics/   # Agent analityki
│   ├── agent4_bos/         # Agent BOS
│   └── agent5_security/    # Agent bezpieczeństwa
├── nodered/                # Konfiguracja Node-RED
├── qdrant/                 # Konfiguracja Qdrant
├── Open_WebUI/             # Konfiguracja Open WebUI
├── ollama/                 # Konfiguracja Ollama
├── DEPLOYMENT.md           # Instrukcja wdrożenia
└── TEAM_TASKS.md           # Podział zadań zespołu
```

**Uprawnienia:**
- **Właściciel:** asiehen
- **Grupa:** chatbot-devs
- **Uprawnienia grupy:** rwX (read, write, execute)
- **Członkowie grupy:** wszyscy użytkownicy serwera VPS

**Symlink dla wygody:**
```bash
~/chatbot-project -> /opt/chatbot-project
```

## 🚀 Szybki Start

### 1. Połączenie VPN (WYMAGANE)

Wszystkie usługi są dostępne tylko przez VPN WireGuard.

**Konfiguracja:**
- Plik: `wg-client.conf` (w głównym katalogu projektu)
- Klient VPN: `10.0.0.2/24`
- Serwer VPN: `10.0.0.1`
- Endpoint: `57.128.212.194:51820`

**Instalacja:**
1. Zainstaluj WireGuard: https://www.wireguard.com/install/
2. Zaimportuj `wg-client.conf` do aplikacji WireGuard
3. Aktywuj tunel "Chatbot VPS"
4. Sprawdź: `ping 10.0.0.1`

**Szczegóły:** Zobacz [DEPLOYMENT.md](DEPLOYMENT.md#połączenie-vpn-wymagane) dla pełnej instrukcji.

### 2. Dostęp do Serwera

**SSH:**
```bash
ssh <user>@57.128.212.194
```

**Dostęp do projektu:**
```bash
cd /opt/chatbot-project
# lub
cd ~/chatbot-project  # symlink
```

### 3. Dostęp do Usług

**WYMAGANE:** Połączenie przez WireGuard VPN

Po aktywacji VPN:
- **Open WebUI:** http://10.0.0.1:3000
- **Node-RED:** http://10.0.0.1:1880
- **Qdrant Dashboard:** http://10.0.0.1:6333/dashboard
- **Agent1 API:** http://10.0.0.1:8001/docs

### Zarządzanie Kontenerami

**Sprawdzenie statusu:**
```bash
cd /opt/chatbot-project/agents/agent1_student
docker compose ps
```

**Restart agenta:**
```bash
cd /opt/chatbot-project/agents/agent1_student
docker compose restart
```

**Logi:**
```bash
docker logs agent1_student --tail 50 -f
```

**Restart wszystkich usług:**
```bash
# Qdrant
cd /opt/chatbot-project/qdrant && docker compose restart

# Open WebUI
cd /opt/chatbot-project/Open_WebUI && docker compose restart

# Node-RED
cd /opt/chatbot-project/nodered && docker compose restart

# Agenci 1-5
for i in {1..5}; do
  cd /opt/chatbot-project/agents/agent${i}_* && docker compose restart
done
```

## Node-RED - Orkiestracja Workflow

**Orkiestrator:** Node-RED (nodered/node-red:latest)

**Dostęp:**
- Dashboard: http://10.0.0.1:1880 (VPN wymagane)
- Edytor flow: http://10.0.0.1:1880

**Funkcje:**
- Wizualna orkiestracja przepływu danych między 5 agentami
- Routing zapytań do odpowiednich agentów na podstawie kategorii
- Automatyzacja procesów i workflow
- Edycja flow w czasie rzeczywistym przez GUI
- Logika warunkowa i transformacja danych

**Konfiguracja:**
- Katalog: `/opt/chatbot-project/nodered/`
- Docker Compose: `nodered/docker-compose.yml`
- Wolumen danych: `nodered_data`
- Sieć: `ai_network`
- Port: 1880

**Integracja z agentami:**
- Agent1: endpoint `POST /publish-workflow` do publikacji flow
- Plik workflow: `agents/agent1_student/agent1_flow.json`
- URL wewnętrzny: `http://node-red:1880`

**Zarządzanie:**
```bash
# Restart
cd /opt/chatbot-project/nodered && docker compose restart

# Logi
docker logs node-red --tail 50 -f

# Status
docker ps | grep node-red
```

## 📚 Dokumentacja

### Główne Dokumenty
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Instrukcja wdrożenia i dostępu
- **[TEAM_TASKS.md](TEAM_TASKS.md)** - Podział zadań zespołu

### Dokumentacja Agentów
- **[README_AGENT1.md](README_AGENT1.md)** - Kompletna dokumentacja Agent1 Student
  - Architektura RAG, API, instalacja, konfiguracja
  - Baza wiedzy (220 dokumentów, 5 kategorii)
  - System logowania i troubleshooting
- **[docs_agent1/](docs_agent1/INDEX.md)** - Dokumentacja szczegółowa Agent1
  - Raporty implementacji i testów
  - Przykłady użycia logowania
  - Quick Start Guide

### API Endpoints

**Agent1 Student (http://10.0.0.1:8001):**
- `POST /api/chat` - Chat z RAG
- `POST /api/generate` - Generowanie odpowiedzi
- `GET /api/tags` - Lista modeli
- `POST /api/pull` - Pobieranie modelu
- `GET /admin/logs/queries/stats` - Statystyki zapytań
- `GET /admin/logs/qa/stats` - Statystyki QA

Pełna dokumentacja API: http://10.0.0.1:8001/docs (po połączeniu VPN)

## 👥 Zespół

### Członkowie Zespołu
- **Adam Siehen** (@asiehen) - Project Manager, Deployment, Infrastruktura
- **Patryk Boguski** - Tech Ops, LLM, Backend ML
- **Mikołaj Sykucki** - Tester/Analityk, Python
- **Oskar Jurgielaniec** - Frontend, JavaScript
- **Paweł Ponikowski** (@pponikowski) - Python, Baza Wiedzy

### Zasady Współpracy

**Strategia Branchowania:**
- **`beta`** - branch roboczy/deweloperski (domyślny dla pracy)
- **`main`** - branch produkcyjny (stabilny, tylko działające funkcje)

⚠️ **Zawsze pracuj na `beta`!** Branch `main` to zabezpieczenie - merge tylko gdy funkcja działa.

**Git Workflow:**
```bash
# 1. Upewnij się że jesteś na beta
git checkout beta
git pull origin beta

# 2. Tworzenie feature brancha (opcjonalne, dla większych zmian)
git checkout -b feature/nazwa-zadania

# 3. Commitowanie (Conventional Commits)
git commit -m "feat(agent1): opis funkcjonalności"
git commit -m "fix(ollama): opis naprawy"
git commit -m "docs: aktualizacja dokumentacji"

# 4. Push do beta (bezpośrednio lub przez PR)
git push origin beta
# LUB dla feature brancha:
git push origin feature/nazwa-zadania
# -> Pull Request do beta -> Code Review -> Merge

# 5. Merge beta -> main (TYLKO gdy funkcja działa na 100%)
git checkout main
git merge beta
git push origin main
```

**Typy commitów:**
- `feat:` - nowa funkcjonalność
- `fix:` - naprawa błędu
- `docs:` - dokumentacja
- `test:` - testy
- `refactor:` - refaktoryzacja
- `chore:` - konfiguracja, devops

## 🔗 Linki

- **Repozytorium:** https://github.com/chatbot-dla-studentow/chatbot-project
- **Serwer VPS:** vps-5f2a574b.vps.ovh.net (57.128.212.194)
- **Projekt na VPS:** `/opt/chatbot-project`

## 📊 Metryki Projektu

**Infrastruktura:**
- Serwer: Ubuntu 24.10, 16GB RAM, 300GB SSD
- Kontenery: 7 (Qdrant, Open WebUI, Node-RED, 5× Agent)
- Network: ai_network (172.18.0.0/16)
- VPN: WireGuard (10.0.0.0/24)

**Model LLM:**
- Nazwa: mistral:7b
- Rozmiar: 4.4 GB
- Parametry: 7.2B
- Kwantyzacja: Q4_K_M

**Baza Wiedzy:**
- Silnik: Qdrant
- Embedding: nomic-embed-text
- Kolekcje: 3 (agent1_student, queries_log, qa_pairs_log)
- Dokumenty: ~20+ (stypendia, BOS, harmonogramy)

---

**Ostatnia aktualizacja:** 10 lutego 2026  
**Maintainers:** Adam Siehen (@asiehen), Paweł Ponikowski (@pponikowski)
