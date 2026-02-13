# 🚀 ChatBot Deployment System

⚠️ **BREAKING CHANGE v2.0 (Feb 2026):** Stare pliki `agents/*/docker-compose.yml` zostały USUNIĘTE. Plik `deploy.ps1` usunięty (tylko Linux/WSL/Ubuntu).

✅ **Teraz wykorzystuj:**
- Nowy VPS? → `./deployment/setup.sh` ← **REKOMENDOWANE!**
- Manualnie? → główny `docker-compose.yml` w root katalogu
- Dev lokalne? → `make deploy` z Makefile

Kompletny system automatycznego wdrożenia chatbota na świeżą maszynę wirtualną lub VPS.

## 📋 Nowa struktura `deployment/` (v2.0)

### Główny orchestrator

**`deployment/setup.sh`** - ALL-IN-ONE setup dla nowego VPS
- Sekwencyjnie uruchamia wszystkie fazy
- Interactive prompts
- Zalecane dla wdrożenia od zera

### deployment/server/ - Konfiguracja serwera

1. **`secure.sh`** - Security hardening
   - fail2ban, UFW, SSH hardening
   - Network security, automatic updates
   - Trwa: ~5 minut

2. **`geo-blocking.sh`** - EU-only geo-blocking
   - ipset z IP ranges 28 krajów UE
   - Weekly automatic updates
   - Trwa: ~2 minuty

3. **`monitoring-alerts.sh`** - Monitoring i alerty email
   - Postfix configuration
   - Health checks (co 4h)
   - Security audits (daily)
   - Trwa: ~3 minuty

### deployment/app/ - Wdrożenie aplikacji

1. **`deploy.sh`** - Główny skrypt wdrożenia dla Linux/VPS
   - Instalacja zależności (Docker, Docker Compose, Python)
   - Automatyczne wdrożenie całego systemu
   - Zarządzanie serwisami (start/stop/restart)
   - Diagnostyka i logi

2. **`init-knowledge.sh`** - Inicjalizacja bazy wiedzy
   - Parsowanie dokumentów
   - Ładowanie do Qdrant
   - Weryfikacja i sprawdzanie jakości

### Konfiguracja i pliki pomocnicze

4. **`docker-compose.yml`** - Główny orchestrator
   - Wszystkie serwisy w jednym pliku
   - Zależności i health checks
   - Automatyczne uruchamianie w odpowiedniej kolejności

5. **`.env.example`** - Przykładowa konfiguracja
   - Porty serwisów
   - Parametry Ollama i Qdrant
   - Zmienne środowiskowe

### Monitoring i utrzymanie

4. **`health-check.sh`** - Sprawdzanie zdrowia systemu
   - Backup wolumenów Docker
   - Backup konfiguracji
   - Czyszczenie starych backupów

8. **`restore.sh`** - Przywracanie z backupów
   - Restore konkretnego lub najnowszego backupu
   - Bezpieczne przywracanie danych

### Automatyzacja i system

10. **`chatbot.service`** - Systemd service (ROOT level)
    - Codzienne backupy
    - Monitoring zdrowia
    - Automatyczne czyszczenie

12. **`Makefile`** - Skróty komend (ROOT level)
14. **`deployment/docs/SECURITY.md`** - Szczegółowa dokumentacja bezpieczeństwa (NOWA LOKALIZACJA)
15. **`INSTALL.md`** - Szybki przewodnik instalacji (ROOT level)
16. **`DEPLOYMENT.md`** - Zaktualizowany o automatyczne wdrożenie (ROOT level)

## 🎯 Quick Start

### Linux/VPS (RECOMMENDED - 1 komenda)

```bash
# 1. Sklonuj projekt
git clone https://github.com/your-username/chatbot-project.git
cd chatbot-project

# 2. Uruchom all-in-one setup
./deployment/setup.sh
```

**Alternatywnie - Krok po kroku (manual):**

```bash
# 1. Security
sudo ./deployment/server/secure.sh

# 2. Geo-blocking
sudo ./deployment/server/geo-blocking.sh

# 3. Monitoring
sudo ./deployment/server/monitoring-alerts.sh

# 4. Application
sudo ./deployment/app/deploy.sh install_dependencies
./deployment/app/deploy.sh deploy
```

### Windows (z WSL - not supported)

```bash
# Zamiast natywnego Windows, użyj WSL:
wsl bash
cd /home/user/chatbot-project
./deployment/setup.sh
```

**LUB Linux/VPS (recommended)**

### Użycie Make (opcjonalnie - Linux)

```bash
# Instalacja
sudo make install

# Deployment
make deploy

# Status
make status

# Backup
make backup
```

## 📋 Komendy deploy.sh

```bash
# Deployment i setup
./deployment/app/deploy.sh install_dependencies  # Zainstaluj Docker i zależności (sudo)
./deployment/app/deploy.sh deploy               # Pełne wdrożenie systemu

# Zarządzanie
./deployment/app/deploy.sh start                # Uruchom wszystkie serwisy
./deployment/app/deploy.sh stop                 # Zatrzymaj wszystkie serwisy
./deployment/app/deploy.sh restart              # Restart wszystkich serwisów
./deployment/app/deploy.sh status               # Sprawdź status serwisów

# Diagnostyka
./deployment/app/deploy.sh logs                 # Pokaż wszystkie logi
./deployment/app/deploy.sh logs agent1_student  # Logi konkretnego serwisu

# Utrzymanie
./deployment/app/deploy.sh init-kb              # Odśwież bazę wiedzy
./deployment/app/deploy.sh cleanup              # Usuń wszystko (UWAGA!)
```

## 📋 Komendy Makefile

```bash
make help          # Pokaż wszystkie komendy
make install       # Zainstaluj zależności
make deploy        # Pełne wdrożenie
make start         # Uruchom serwisy
make stop          # Zatrzymaj serwisy
make status        # Status systemu
make health        # Sprawdzenie zdrowia
make backup        # Wykonaj backup
make test-query    # Testowe zapytanie
make logs-agent1   # Logi Agent1
```

## 🛠️ Struktura Systemu

```
chatbot-project/
├── docker-compose.yml          # Główny orchestrator
├── .env.example                # Przykładowa konfiguracja
│
├── deploy.sh                   # Deployment Linux
├── deploy.ps1                  # Deployment Windows
├── init-knowledge.sh           # Init bazy wiedzy
├── backup.sh                   # Backup
├── restore.sh                  # Restore
├── health-check.sh             # Health check
│
├── Makefile                    # Make targets
├── chatbot.service             # Systemd service
├── crontab.example             # Przykłady cronjobs
│
├── INSTALL.md                  # Quick start
├── DEPLOYMENT.md               # Pełna dokumentacja
└── README_DEPLOYMENT.md        # Ten plik
```

## 🔄 Architektura Deployment

### Kolejność uruchamiania

```
1. Infrastructure
   ├── qdrant (Vector DB)
   ├── ollama (LLM)
   └── node-red (Workflows)

2. Initialization
   ├── Pobierz model mistral:7b
   └── Załaduj bazę wiedzy

3. Agents
   ├── agent1_student (główny)
   ├── agent2_ticket
   ├── agent3_analytics
   ├── agent4_bos
   └── agent5_security

4. Optional
   └── open-webui (UI)
```

### Porty serwisów

- **8001** - Agent1 Student Support
- **8002** - Agent2 Ticket Management
- **8003** - Agent3 Analytics
- **8004** - Agent4 BOS
- **8005** - Agent5 Security
- **6333** - Qdrant Vector Database
- **11434** - Ollama LLM
- **1880** - Node-RED
- **3000** - Open WebUI

## 🔧 Konfiguracja

### 1. Zmień URL repozytorium

W pliku `deploy.sh` (linia 13):
```bash
GIT_REPO="https://github.com/YOUR-USERNAME/chatbot-project.git"
```

### 2. Dostosuj środowisko

```bash
cp .env.example .env
nano .env
```

Ważne parametry:
```bash
AGENT1_PORT=8001
OLLAMA_MODEL=mistral:7b
ENVIRONMENT=production
SECRET_KEY=<wygeneruj-bezpieczny>
```

### 3. Generuj bezpieczne klucze

```bash
openssl rand -base64 32
```

## 📊 Monitoring

### Health Check

```bash
# Ręcznie
./health-check.sh

# Automatycznie (cron)
*/15 * * * * /opt/chatbot-project/health-check.sh >> /var/log/chatbot-health.log 2>&1
```

### Backup

```bash
# Ręcznie
./backup.sh /opt/chatbot-backups

# Automatycznie (cron)
0 2 * * * /opt/chatbot-project/backup.sh /opt/chatbot-backups >> /var/log/chatbot-backup.log 2>&1
```

### Restore

```bash
# Najnowszy backup
./restore.sh /opt/chatbot-backups

# Konkretny backup
./restore.sh /opt/chatbot-backups 20260213-143022
```

## 🚀 Systemd (autostart przy boot)

```bash
# Zainstaluj service
sudo cp chatbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable chatbot
sudo systemctl start chatbot

# Zarządzanie
sudo systemctl status chatbot
sudo systemctl restart chatbot
sudo systemctl stop chatbot
```

## 🆘 Troubleshooting

### Problem: Brak Dockera
```bash
sudo ./deployment/app/deploy.sh install_dependencies
```

### Problem: Port zajęty
```bash
# Sprawdź
sudo netstat -tulpn | grep :8001

# Zmień w .env
AGENT1_PORT=8101
```

### Problem: Brak pamięci
```bash
# Dodaj swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Problem: Baza wiedzy pusta
```bash
./init-knowledge.sh
```

## 📝 Przykładowe użycie

### Pierwsze wdrożenie

```bash
# Świeży VPS
git clone <your-repo>
cd chatbot-project
sudo ./deployment/app/deploy.sh install_dependencies
# [wyloguj się i zaloguj ponownie]
./deployment/app/deploy.sh deploy
```

### Codzienne operacje

```bash
# Status
make status

# Logi
make logs-agent1

# Backup
make backup

# Health check
./health-check.sh
```

### Aktualizacja

```bash
git pull
./deployment/app/deploy.sh restart
```

## 🎨 Customization

### Zmiana modelu Ollama

W `.env`:
```bash
OLLAMA_MODEL=llama2:13b  # zamiast mistral:7b
```

### Dodanie nowego agenta

1. Dodaj service w `docker-compose.yml`
2. Restart systemem: `./deployment/app/deploy.sh restart`

### Customowe porty

W `.env`:
```bash
AGENT1_PORT=9001
QDRANT_PORT=9333
```

## 📚 Dokumentacja

- **[INSTALL.md](INSTALL.md)** - Quick start guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Pełna dokumentacja deployment
- **[README.md](README.md)** - Przegląd projektu
- **[docs_agent1/](docs_agent1/)** - Dokumentacja Agent1

## ✅ Checklist pre-production

- [ ] Zmieniony URL repozytorium w `deploy.sh`
- [ ] Skopiowany i dostosowany `.env` z `.env.example`
- [ ] Wygenerowane bezpieczne klucze (SECRET_KEY, API_KEY)
- [ ] Zainstalowany i skonfigurowany firewall
- [ ] Skonfigurowany backup (cron)
- [ ] Skonfigurowany health check (cron)
- [ ] Zainstalowany systemd service (autostart)
- [ ] Skonfigurowany monitoring (opcjonalnie)
- [ ] Przetestowane wszystkie serwisy
- [ ] Wykonany test backup i restore

---

**Gotowe!** System jest teraz w pełni zautomatyzowany i gotowy do wdrożenia na produkcję. 🎉


## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
