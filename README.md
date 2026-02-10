# Chatbot dla Studentów - System Multi-Agentowy

Inteligentny chatbot dla studentów uczelni wyższej wykorzystujący architekturę multi-agentową, RAG (Retrieval-Augmented Generation) i lokalne modele LLM.

## 📋 Spis treści

- [Opis projektu](#opis-projektu)
- [Struktura katalogów](#struktura-katalogów)
- [Zespół i zakres prac](#zespół-i-zakres-prac)
- [Indeks dokumentów](#indeks-dokumentów)
- [Szybki deploy i uruchomienie](#szybki-deploy-i-uruchomienie)
- [VPN i plik konfiguracyjny](#vpn-i-plik-konfiguracyjny)
- [Architektura w skrócie](#architektura-w-skrócie)
- [Troubleshooting](#troubleshooting)

## 🎯 Opis projektu

System składa się z 5 wyspecjalizowanych agentów:
- **Agent1 (Student)** - pytania studenckie (stypendia, BOS, harmonogramy)
- **Agent2 (Ticket)** - zarządzanie zgłoszeniami
- **Agent3 (Analytics)** - analityka i statystyki
- **Agent4 (BOS)** - integracja z Biurem Obsługi Studenta
- **Agent5 (Security)** - bezpieczeństwo i autoryzacja

**Główne funkcjonalności:**
- ✅ konwersacje w języku naturalnym (mistral:7b)
- ✅ RAG - wyszukiwanie w bazie wiedzy (Qdrant)
- ✅ orkiestracja workflow (Node-RED)
- ✅ logowanie zapytań i odpowiedzi
- ✅ interfejs webowy (Open WebUI)
- ✅ bezpieczny dostęp przez VPN (WireGuard)

## 📂 Struktura katalogów

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
├── docs_agent1/            # Dokumentacja Agent1
├── DEPLOYMENT.md           # Szczegóły wdrożenia
├── README_AGENT1.md        # Dokumentacja Agent1 (szczegółowa)
└── wg-client.conf          # Konfiguracja VPN
```

## 👥 Zespół i zakres prac

| Członek zespołu | Rola | Zadania (skrót) |
|---|---|---|
| Adam Siehen | Project Manager | Do uzupełnienia |
| Patryk Boguski | Tech Ops | Do uzupełnienia |
| Mikołaj Sykucki | Tester/Analityk | Do uzupełnienia |
| Oskar Jurgielaniec | Frontend | Do uzupełnienia |
| Paweł Ponikowski | Baza wiedzy i dokumentacja | FAQ, procedury, stypendia, regulaminy; skrypty: parse/load/update/verify/check/add_qa; dokumentacja: knowledge.md, ARCHITECTURE.md; testy helperów; merge beta -> main |

## 📚 Indeks dokumentów

- [README_AGENT1.md](README_AGENT1.md) - pełna dokumentacja Agent1
- [docs_agent1/knowledge.md](docs_agent1/knowledge.md) - dokumentacja bazy wiedzy
- [docs_agent1/ARCHITECTURE.md](docs_agent1/ARCHITECTURE.md) - architektura systemu
- [docs_agent1/QUICK_START.md](docs_agent1/QUICK_START.md) - szybki start (Agent1)
- [docs_agent1/INDEX.md](docs_agent1/INDEX.md) - indeks dokumentów Agent1
- [DEPLOYMENT.md](DEPLOYMENT.md) - szczegóły wdrożenia i środowiska
- [wg-client.conf](wg-client.conf) - konfiguracja WireGuard (plik w repo)

## 🚀 Szybki deploy i uruchomienie

**Wymagane:** aktywny VPN (WireGuard).

## 🔐 VPN i plik konfiguracyjny

Połączenie VPN jest wymagane, aby uzyskać dostęp do usług.

1. Zainstaluj WireGuard: https://www.wireguard.com/install/
2. Zaimportuj konfigurację z pliku [wg-client.conf](wg-client.conf)
3. Aktywuj tunel i sprawdź połączenie: `ping 10.0.0.1`

### 1) Połączenie z serwerem

```bash
ssh <user>@57.128.212.194
cd /opt/chatbot-project
```

### 2) Start kluczowych usług

```bash
cd /opt/chatbot-project/qdrant && docker compose up -d
cd /opt/chatbot-project/ollama && docker compose up -d
cd /opt/chatbot-project/Open_WebUI && docker compose up -d
cd /opt/chatbot-project/nodered && docker compose up -d
cd /opt/chatbot-project/agents/agent1_student && docker compose up -d --build
```

### 3) Dostęp do usług (po VPN)

- Open WebUI: http://10.0.0.1:3000
- Node-RED: http://10.0.0.1:1880
- Qdrant Dashboard: http://10.0.0.1:6333/dashboard
- Agent1 API: http://10.0.0.1:8001/docs


Szczegóły: [DEPLOYMENT.md](DEPLOYMENT.md#połączenie-vpn-wymagane)

## 🏗️ Architektura w skrócie

Centralnym komponentem jest **Agent1 Student**, który realizuje RAG (Qdrant + Ollama) i udostępnia wiedzę agentom 2-5. Orkiestrację przepływu zapewnia Node-RED.

Pełny opis: [docs_agent1/ARCHITECTURE.md](docs_agent1/ARCHITECTURE.md)

## 🧰 Troubleshooting

- **Brak dostępu do usług (10.0.0.1)**: sprawdź, czy VPN jest aktywny.
- **Agent1 nie odpowiada**: uruchom `docker compose up -d --build` w [agents/agent1_student](agents/agent1_student).
- **Qdrant/Ollama nie startuje**: sprawdź `docker ps` i logi kontenerów (`docker logs <nazwa>`).

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
- **Adam Siehen** (@adamsiehen) - Project Manager, Deployment, Infrastruktura
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
**Maintainers:** Adam Siehen (@adamsiehen), Paweł Ponikowski (@pponikowski)
