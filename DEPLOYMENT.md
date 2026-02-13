# Instrukcja wdrożenia i dostępu do chatbota

> **Powiązana dokumentacja:** [README.md](README.md) | [AGENT1_OVERVIEW.md](AGENT1_OVERVIEW.md) | [docs_agent1/ARCHITECTURE.md](docs_agent1/ARCHITECTURE.md) | [docs_agent1/QUICK_START.md](docs_agent1/QUICK_START.md)

⚠️ **VPS został zaatakowany i zbanowany. Przenieśliśmy się na nowy serwer.**

> 📘 **Nowa infrastruktura deployment jest gotowa!** Przejdź do [deployment/README.md](deployment/README.md) aby poznać automatyczną procedurę wdrożenia dla **świeżego VPS**.

### ⚡ Breaking Change v2.0 (Stycz-2026)

**Zmiany:**
- `agents/*/docker-compose.yml` - PRZYWRÓCONE (do uruchamiania pojedynczych agentów)
- Deploy skrypty przeniesione do `deployment/app/` i `deployment/server/`

✅ **Noweł struktura /deployment:**
```
deployment/
├── setup.sh                  ← Uruchom ten! (ALL-IN-ONE)
├── server/                   ← Bezpieczeństwo serwera
├── app/                      ← Wdróżenie aplikacji
└── docs/                    ← Dokumentacja
```

✅ **Do wdrożenia teraz używaj:**
- **Nowy VPS?** → `./deployment/setup.sh` (rekomendowane!) ← ALL-IN-ONE
- **Manualnie?** → `./deployment/server/secure.sh` + inne skrypty
- **Aplikacji?** → `./deployment/app/deploy.sh`
- **Lokalmente na dev?** → `make deploy` (z Makefile'a)

✅ **Uruchamianie pojedynczych agentów (opcjonalnie):**
- `agents/*/docker-compose.yml` (wymaga uruchomionych `qdrant` i `ollama` w sieci `ai_network`)

## Spis treści

- [🚀 Automatyczne wdrożenie](#-automatyczne-wdrożenie-nowa-maszyna)
  - [Quick Start - Świeży VPS](#quick-start---świeży-vps) ← **START TUTAJ DLA NOWEGO VPS**
  - [Wymagania systemowe](#wymagania-systemowe)
  - [Konfiguracja środowiska](#konfiguracja-środowiska)
  - [Komenda deployment](#komendy-deployment)
- [Połączenie VPN](#połączenie-vpn-wymagane)
- [Dostęp SSH](#dostęp-ssh)
- [Zasoby serwera](#zasoby-serwera)
- [Lista usług](#lista-usług)
- [Zarządzanie bazą wiedzy](#zarządzanie-bazą-wiedzy)
- [Daily Operations](#daily-operations)
- [Bezpieczeństwo](#bezpieczeństwo)
- [Diagnostyka](#diagnostyka)
- [Git Workflow](#git-workflow-strategia-branchowania)

---

## 🚀 Automatyczne wdrożenie (nowa maszyna)

> ✅ **Używaj tego dla nowego VPS!** Pełne bezpieczeństwo + wdrożenie w jednym skrypcie interaktywnym.

### Quick Start - Świeży VPS

Szybko wdróż całą infrastrukturę na świeżej maszynie VPS/VM w **oneshot command**:

```bash
# 1. Zaloguj się do nowego VPS
ssh root@<new-vps-ip>

# 2. Sklonuj repozytorium
git clone <repo-url> /opt/chatbot-project
cd /opt/chatbot-project

# 3. Uruchom interaktywny wizard (all-in-one setup)
chmod +x deployment/setup.sh
sudo ./deployment/setup.sh
```

**Czas całej konfiguracji:** ~20 minut (zabezpieczenia + aplikacja)

### Co obejmuje `setup.sh` ?

```
Phase 1: 🔒 Zabezpieczenie systemu (5 min)
  ├─ fail2ban (ochrona brute-force SSH)
  ├─ UFW firewall (port whitelisting)
  ├─ SSH hardening (port 2222, key auth only)
  ├─ Network security (SYN cookies, IP spoofing protection)
  └─ Automatic updates (daily security patches)

Phase 2: 🌍 Geo-blocking (2 min)
  └─ EU-only access (28 krajów, weekly updates)

Phase 3: 📬 Monitoring & Alerts (3 min)
  ├─ Email alerts do adam.siehen@outlook.com
  ├─ Health checks (co 4 godziny)
  ├─ Security audits (codziennie)
  └─ chatbot-status dashboard

Phase 4: 🚀 Deployment aplikacji (8-10 min)
  ├─ Docker + Compose installation
  ├─ Pobieranie modelu Ollama (mistral:7b)
  ├─ Inicjalizacja bazy wiedzy
  └─ Start wszystkich serwisów
```

**Wynik:** Całowicie zabezpieczony system gotowy do produkcji ✓

---

### Przydatne linkii do dokumentacji

| Dokument | Opis |
|----------|------|
| [deployment/README.md](deployment/README.md) | 📖 Przewodnik szybkiego startu (czytaj pierwszy!) |
| [deployment/SECURITY.md](deployment/SECURITY.md) | 🔒 Szczegółowa dokumentacja bezpieczeństwa |
| [INSTALL.md](INSTALL.md) | 🔧 Instrukcja instalacji krok po kroku |
| [README_DEPLOYMENT.md](README_DEPLOYMENT.md) | 📚 Pełna dokumentacja deployment'u |

### Po uruchomieniu `setup.sh` wszystkie serwisy będą dostępne

**Dostęp wymaga VPN na subnecie:**
- IPv4: `10.0.0.0/24`
- IPv6: `fd00::/8`
- SSH: port **2222** (tylko przez VPN)

**Serwicy aplikacji (przez VPN):**
- 🤖 Agent1 (Student Support): `http://<vps-ip>:8001`
- 🤖 Agent2 (Ticket System): `http://<vps-ip>:8002`
- 🤖 Agent3 (Analytics): `http://<vps-ip>:8003`
- 🤖 Agent4 (BOS): `http://<vps-ip>:8004`
- 🤖 Agent5 (Security): `http://<vps-ip>:8005`
- 📊 Qdrant (Vector DB): `http://<vps-ip>:6333`
- 🧠 Ollama (LLM): `http://<vps-ip>:11434`
- 🔄 Node-RED (Workflows): `http://<vps-ip>:1880`
- 🌐 Open WebUI: `http://<vps-ip>:3000`

**Monitorowanie:**
- Email alerts wysyłane do: `adam.siehen@outlook.com`
- Dashboard: `chatbot-status` (dostępna komenda SSH)

---

## 📌 Ważne informacje o starym VPS

Poprzedni serwer został zaatakowany i zbanowany przez dostawcę. **Ta nowa infrastruktura jest trwale zainstalowana na nowym VPS.**

**Główne ulepszenia:**
- ✅ fail2ban z ochroną brute-force na 1h bany
- ✅ UFW firewall z dostępem tylko przez VPN
- ✅ EU-only geo-blocking (28 krajów)
- ✅ Email monitoring na adam.siehen@outlook.com
- ✅ SSH na porcie 2222 z key auth only
- ✅ Automatyczne security patches codziennie
- ✅ Systemd service dla auto-start
- ✅ Backup/restore scripts
- ✅ Health checks i monitoring

---

### Wymagania systemowe

**Minimalna konfiguracja:**
- OS: Ubuntu 22.04+ / Debian 11+ / RHEL 8+
- RAM: 8 GB (16 GB zalecane)
- CPU: 4 rdzenie (dla modelu Ollama mistral:7b)
- Dysk: 30 GB wolnej przestrzeni
- Połączenie: Stały dostęp do internetu

**Oprogramowanie (instalowane automatycznie):**
- Docker 24.0+
- Docker Compose V2
- Git
- Python 3.10+
- curl, wget

### Konfiguracja środowiska

**1. Skopiuj przykładowy plik środowiskowy:**
```bash
cp .env.example .env
```

**2. Edytuj `.env` i dostosuj konfigurację:**
```bash
nano .env
```

**Kluczowe parametry do dostosowania:**

```bash
# Porty serwisów (zmień jeśli masz konflikty)
AGENT1_PORT=8001
QDRANT_PORT=6333
OLLAMA_PORT=11434
NODERED_PORT=1880

# Model Ollama (zmień na większy jeśli masz więcej RAM)
OLLAMA_MODEL=mistral:7b

# Ścieżka wdrożenia
DEPLOY_PATH=/opt/chatbot-project

# Bezpieczeństwo (ZMIEŃ W PRODUKCJI!)
SECRET_KEY=<wygeneruj-bezpieczny-klucz>
API_KEY=<wygeneruj-bezpieczny-klucz>

# Środowisko
ENVIRONMENT=production
```

**Generowanie bezpiecznych kluczy:**
```bash
# Secret Key
openssl rand -base64 32

# API Key
openssl rand -base64 32
```

**3. Zaktualizuj URL repozytorium w `deploy.sh`:**
```bash
# Linia 13 w deploy.sh
GIT_REPO="https://github.com/your-username/chatbot-project.git"
```

### Komendy deployment

**Główny skrypt: `./deployment/app/deploy.sh` (Ubuntu/Debian)**
**Dla Arch Linux: `./deployment/app/deploy-arch.sh`**

#### Instalacja systemu

```bash
# Ubuntu/Debian
sudo ./deployment/app/deploy.sh install_dependencies

# Arch Linux
sudo ./deployment/app/deploy-arch.sh install_dependencies

# Pełne wdrożenie (wszystkie kroki)
./deployment/app/deploy.sh deploy       # Ubuntu/Debian
./deployment/app/deploy-arch.sh deploy  # Arch Linux
```

#### Zarządzanie serwisami

```bash
# Uruchom wszystkie serwisy
./deployment/app/deploy.sh start

# Zatrzymaj wszystkie serwisy
./deployment/app/deploy.sh stop

# Restart wszystkich serwisów
./deployment/app/deploy.sh restart

# Sprawdź status serwisów
./deployment/app/deploy.sh status
```

#### Logi i diagnostyka

```bash
# Pokaż logi wszystkich serwisów (live)
./deployment/app/deploy.sh logs

# Pokaż logi konkretnego serwisu
./deployment/app/deploy.sh logs agent1_student
./deployment/app/deploy.sh logs qdrant
./deployment/app/deploy.sh logs ollama
./deployment/app/deploy.sh logs node-red
```

#### Zarządzanie bazą wiedzy

```bash
# Zainicjalizuj/odśwież bazę wiedzy
./deployment/app/deploy.sh init-kb

# Lub użyj dedykowanego skryptu
./deployment/app/init-knowledge.sh
```

#### Czyszczenie systemu

```bash
# Usuń wszystkie kontenery i wolumeny (UWAGA: usuwa dane!)
./deployment/app/deploy.sh cleanup
```

### Architektura deployment

**Kolejność uruchamiania serwisów:**

```
1. Infrastruktura
   ├── Qdrant (Vector Database)
   ├── Ollama (LLM Service)
   └── Node-RED (Workflow Engine)
   
2. Inicjalizacja
   ├── Pobierz model Ollama (mistral:7b)
   └── Załaduj bazę wiedzy do Qdrant
   
3. Agenci
   ├── Agent1 (Student Support) - główny
   ├── Agent2 (Ticket Management)
   ├── Agent3 (Analytics)
   ├── Agent4 (BOS)
   └── Agent5 (Security)
   
4. Opcjonalne
   └── Open WebUI (interfejs użytkownika)
```

**Network Architecture:**
```
ai_network (bridge)
├── qdrant:6333
├── ollama:11434
├── node-red:1880
├── agent1_student:8000 → host:8001
├── agent2_ticket:8000 → host:8002
├── agent3_analytics:8000 → host:8003
├── agent4_bos:8000 → host:8004
├── agent5_security:8000 → host:8005
└── open-webui:8080 → host:3000
```

### Troubleshooting deployment

**Problem: Brak Dockera**
```bash
sudo ./deployment/app/deploy.sh install_dependencies
```

**Problem: Port już zajęty**
```bash
# Sprawdź co używa portu
sudo netstat -tulpn | grep :8001

# Zmień port w .env
AGENT1_PORT=8101
```

**Problem: Brak pamięci dla Ollamy**
```bash
# Użyj mniejszego modelu
OLLAMA_MODEL=mistral:7b  # zamiast llama2:13b

# Lub zwiększ swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Problem: Qdrant nie odpowiada**
```bash
# Sprawdź logi
./deployment/app/deploy.sh logs qdrant

# Restart serwisu
docker compose restart qdrant
```

**Problem: Baza wiedzy pusta**
```bash
# Re-inicjalizuj bazę wiedzy
./deployment/app/init-knowledge.sh

# Sprawdź kolekcję
curl http://localhost:6333/collections/agent1_student
```

### Monitoring deployment

**Sprawdzenie stanu wszystkich serwisów:**
```bash
./deployment/app/deploy.sh status
```

**Lub ręcznie:**
```bash
# Kontenery
docker ps

# Zdrowie serwisów
curl http://localhost:8001/health      # Agent1
curl http://localhost:6333/health      # Qdrant
curl http://localhost:11434/api/tags   # Ollama

# Kolekcje Qdrant
curl http://localhost:6333/collections

# Modele Ollama
docker exec ollama ollama list
```

### Backup i przywracanie

**Backup wolumenów Docker:**
```bash
# Backup Qdrant
docker run --rm -v qdrant_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/qdrant-backup-$(date +%Y%m%d).tar.gz -C /data .

# Backup Ollama
docker run --rm -v ollama_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/ollama-backup-$(date +%Y%m%d).tar.gz -C /data .

# Backup Node-RED
docker run --rm -v nodered_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/nodered-backup-$(date +%Y%m%d).tar.gz -C /data .
```

**Przywracanie:**
```bash
# Restore Qdrant
docker run --rm -v qdrant_data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/qdrant-backup-20260213.tar.gz -C /data
```

---

## Połączenie VPN (WYMAGANE)

Wszystkie usługi są zabezpieczone przez firewall i dostępne tylko przez VPN WireGuard.

### Instalacja i konfiguracja VPN

**Konfiguracja WireGuard znajduje się w repozytorium:**
- Plik: `wg-client.conf` (w głównym katalogu projektu)
- Typ: Konfiguracja klienta WireGuard
- Dostęp: Repozytorium jest prywatne, więc plik jest bezpiecznie udostępniony zespołowi

**Parametry konfiguracji:**
```
[Interface]
Address = 10.0.0.2/24          # IP klienta w sieci VPN
DNS = 1.1.1.1                   # DNS Cloudflare

[Peer]
PublicKey = di0w...             # Klucz publiczny serwera
Endpoint = 57.128.212.194:51820 # Adres serwera VPS
AllowedIPs = 10.0.0.0/24        # Sieć VPN
PersistentKeepalive = 25        # Utrzymanie połączenia
```

**Kroki instalacji:**

1. Pobierz i zainstaluj WireGuard:
   - Windows: https://www.wireguard.com/install/
   - macOS: https://apps.apple.com/us/app/wireguard/id1451685025
   - Linux: `sudo apt install wireguard` (Ubuntu/Debian)

2. Zaimportuj konfigurację klienta:
   - Otwórz aplikację WireGuard
   - Kliknij "Import tunnel(s) from file"
   - Wybierz plik `wg-client.conf` z katalogu projektu
   - Nazwij tunel: "Chatbot VPS"

3. Aktywuj tunel:
   - W aplikacji WireGuard kliknij "Activate"
   - Status powinien zmienić się na "Active"

**Weryfikacja połączenia:**
```bash
# Windows PowerShell / Linux / macOS
ping 10.0.0.1

# Test dostępu do usług
curl http://10.0.0.1:8001/api/version  # Agent1
curl http://10.0.0.1:6333/collections  # Qdrant
```

**Adresy IP w sieci VPN:**
- Serwer VPS: `10.0.0.1`
- Klient (Ty): `10.0.0.2`
- Zakres sieci: `10.0.0.0/24`

**Uwaga:** Plik `wg-client.conf` zawiera klucze prywatne i jest udostępniony tylko w prywatnym repozytorium zespołu. Nie udostępniaj go publicznie.

## Lokalizacja projektu na serwerze

**Ścieżka główna:**
```
/opt/chatbot-project
```

**Struktura katalogów:**
- `/opt/chatbot-project/agents/` - kod agentów (agent1-5)
- `/opt/chatbot-project/nodered/` - konfiguracja Node-RED
- `/opt/chatbot-project/qdrant/` - konfiguracja Qdrant
- `/opt/chatbot-project/Open_WebUI/` - konfiguracja Open WebUI
- `/opt/chatbot-project/ollama/` - konfiguracja Ollama

**Uprawnienia:**
- Właściciel: `asiehen`
- Grupa: `chatbot-devs`
- Uprawnienia grupy: `rwX` (odczyt, zapis, wykonywanie)
- Wszyscy członkowie grupy `chatbot-devs` mają pełny dostęp

## Dostęp SSH

**Serwer produkcyjny:**
- Adres: `57.128.212.194`
- Port: `22` (SSH)
- System: **Ubuntu 24.10 LTS**

**Uprawnieni użytkownicy (grupa `chatbot-devs`):**

| Login | Email | Rola | Dostęp |
|-------|-------|------|--------|
| asiehen | adam.siehen@outlook.com | Admin | Full (sudo, git, docker, config) |
| pboguski | pboguski@pboguski.pl | Admin | Full (sudo, git, docker, config) |
| msykucki | msykucki@msykucki.pl | Admin | Full (sudo, git, docker, config) |
| ojurgielaniec | ojurgielaniec@ojurgielaniec.pl | Admin | Full (sudo, git, docker, config) |
| pponikowski | pponikowski@pponikowski.pl | Admin | Full (sudo, git, docker, config) |

**Łączenie się z serwerem:**
```bash
# Podstawowe połączenie
ssh <login>@57.128.212.194

# Przykład
ssh pboguski@57.128.212.194

# Z kluczem SSH (jeśli skonfigurowany)
ssh -i ~/.ssh/chatbot-key <login>@57.128.212.194
```

**Symlink dla wygody:**
```bash
~/chatbot-project -> /opt/chatbot-project
```

**Przykładowe komendy:**
```bash
# Przejście do projektu
cd /opt/chatbot-project

# Restart agenta
cd /opt/chatbot-project/agents/agent1_student
docker compose restart

# Sprawdzenie logów
docker logs agent1_student --tail 50
```

## Lista usług

### Interfejsy użytkownika

**Open WebUI (główny chatbot):**
- URL: http://10.0.0.1:3000
- Opis: Interfejs webowy do konwersacji z chatbotem
- Model: mistral:7b z RAG (baza wiedzy)

**Node-RED (orkiestracja workflow):**
- URL: http://10.0.0.1:1880
- Opis: Edytor workflow i orkiestracja agentów
- Dostęp: Dashboard i edytor flow
- Funkcje:
  - Wizualna orkiestracja przepływu danych między 5 agentami
  - Routing zapytań do odpowiednich agentów
  - Automatyzacja procesów
  - Edycja flow w czasie rzeczywistym
- Restart: `cd /opt/chatbot-project/nodered && docker compose restart`
- Logi: `docker logs node-red --tail 50`

### Infrastruktura

**Qdrant (baza wektorowa):**
- API: http://10.0.0.1:6333
- Dashboard: http://10.0.0.1:6333/dashboard
- Opis: Baza wektorowa dla RAG i logowania
- Kolekcje: agent1_student, queries_log, qa_pairs_log

**Ollama (silnik LLM):**
- API: http://10.0.0.1:11434
- Opis: Lokalny serwer modeli językowych
- Model: mistral:7b (4.4 GB)

### Agenci (API endpoints)

**Agent 1 - Student:**
- URL: http://10.0.0.1:8001
- Endpoint główny: http://10.0.0.1:8001/api/chat
- Dokumentacja API: http://10.0.0.1:8001/docs
- **Więcej informacji:** [AGENT1_OVERVIEW.md](AGENT1_OVERVIEW.md) | [docs_agent1/knowledge.md](docs_agent1/knowledge.md)

**Agent 2 - Ticket:**
- URL: http://10.0.0.1:8002
- Dokumentacja API: http://10.0.0.1:8002/docs

**Agent 3 - Analytics:**
- URL: http://10.0.0.1:8003
- Dokumentacja API: http://10.0.0.1:8003/docs

**Agent 4 - BOS:**
- URL: http://10.0.0.1:8004
- Dokumentacja API: http://10.0.0.1:8004/docs

**Agent 5 - Security:**
- URL: http://10.0.0.1:8005
- Dokumentacja API: http://10.0.0.1:8005/docs

## Endpointy administracyjne

### Agent1 - Statystyki i logi

**Statystyki zapytań:**
- URL: http://10.0.0.1:8001/admin/logs/queries/stats
- Metoda: GET
- Zwraca: Liczba zapytań, kategorie, rozkład czasowy

**Statystyki par Q&A:**
- URL: http://10.0.0.1:8001/admin/logs/qa/stats
- Metoda: GET
- Zwraca: Liczba par, średni score RAG, źródła

**Wyszukiwanie podobnych zapytań:**
- URL: http://10.0.0.1:8001/admin/logs/queries/search?query=TEXT&limit=10
- Metoda: GET
- Zwraca: Lista podobnych zapytań z score

**Lista kategorii:**
- URL: http://10.0.0.1:8001/admin/logs/categories
- Metoda: GET
- Zwraca: Dostępne kategorie zapytań

### Ollama API

**Lista modeli:**
- URL: http://10.0.0.1:11434/api/tags
- Metoda: GET

**Wersja Ollama:**
- URL: http://10.0.0.1:11434/api/version
- Metoda: GET

**Generowanie odpowiedzi:**
- URL: http://10.0.0.1:11434/api/generate
- Metoda: POST
- Body: `{"model": "mistral:7b", "prompt": "pytanie"}`

## Bezpieczeństwo

### Firewall
Serwer ma skonfigurowany firewall (iptables), który blokuje wszystkie połączenia z Internetu poza:
- Port 22 (SSH)
- Port 51820 (WireGuard VPN)

### Dostęp do kontenerów Docker
Kontenery Docker są dostępne tylko:
1. Z sieci VPN (10.0.0.0/24)
2. Z localhost na serwerze
3. Między sobą przez sieć Docker (ai_network)

### Reguły iptables
```bash
# Blokada dostępu z Internetu do kontenerów Docker
iptables -I DOCKER-USER -i eth0 ! -s 10.0.0.0/24 -j DROP

# Dozwolone połączenia:
# - SSH (port 22)
# - WireGuard (port 51820 UDP)
# - VPN traffic (10.0.0.0/24)
```

## Diagnostyka

### Sprawdzenie połączenia VPN
```bash
# Windows PowerShell
ping 10.0.0.1

# Linux/macOS
ping -c 4 10.0.0.1
```

### Sprawdzenie statusu usług (na serwerze)
```bash
# SSH do serwera
ssh asiehen@57.128.212.194

# Status kontenerów
docker ps

# Status Ollama
systemctl status ollama

# Logi agenta
docker logs agent1_student
```

### Test API
```bash
# Test Ollama
curl http://10.0.0.1:11434/api/tags

# Test Agent1
curl http://10.0.0.1:8001/api/version

# Test Qdrant
curl http://10.0.0.1:6333/health
```

## Rozwiązywanie problemów

### VPN nie łączy się
1. Sprawdź czy WireGuard jest zainstalowany
2. Zweryfikuj plik konfiguracyjny `wg-client.conf`
3. Sprawdź firewall na swoim komputerze
4. Upewnij się że port UDP 51820 nie jest blokowany

### Nie mogę połączyć się z usługą
1. Sprawdź czy VPN jest aktywny
2. Zweryfikuj adres IP: `ping 10.0.0.1`
3. Sprawdź status kontenera: `docker ps`
4. Zobacz logi: `docker logs <nazwa_kontenera>`

### Chatbot nie odpowiada
1. Sprawdź czy model jest pobrany: `ollama list`
2. Zobacz logi agent1: `docker logs agent1_student`
3. Sprawdź Qdrant: `curl http://10.0.0.1:6333/health`
4. Zweryfikuj połączenie Ollama: `curl http://10.0.0.1:11434/api/version`

## Zasoby serwera

### Wymagania dla wirtualnej maszyny (VM)

Jeśli stawiasz chatbota na własnej VM:

| Zasób | Minimum | Rekomendowane |
|-------|---------|---------------|
| RAM | 16 GB | **20 GB** |
| CPU | 2 rdzenie | **4 rdzenie** |
| Storage | 50 GB | 100 GB (dla historii logów) |
| Sieć | 100 Mbps | 1 Gbps |

**Uzasadnienie:**
- Ollama (mistral:7b): ~8 GB RAM w runtime
- Qdrant (baza wektorowa): ~2-4 GB RAM
- 5 agentów Docker: ~2-3 GB RAM
- Open WebUI + Node-RED: ~1-2 GB RAM
- System operacyjny: ~2 GB
- Bufor operacyjny: ~4-6 GB

**Sprawdzenie zasobów na uruchomionej maszynie:**
```bash
# RAM i CPU
free -h
top -bn1 | head -10

# Dysk
df -h /opt/chatbot-project

# Docker memory usage
docker stats --no-stream
```

### Konfiguracja serwera produkcyjnego

**Dane dostępowe:**
- Adres publiczny: `57.128.212.194`
- Hostname: `vps-5f2a574b.vps.ovh.net`
- System: **Ubuntu 24.10 LTS**
- Właściciel: `asiehen`

## Konfiguracja serwera

### Sieć Docker
- Nazwa: ai_network
- Typ: bridge
- Zakres: 172.18.0.0/16

### Sieć VPN
- Zakres: 10.0.0.0/24
- Serwer: 10.0.0.1
- Klient: 10.0.0.2
- Interface: wg0

## Zarządzanie bazą wiedzy

**Lokalizacja skryptów:**
```
/opt/chatbot-project/agents/agent1_student/helpers/
```

**Główne skrypty:**

| Skrypt | Przeznaczenie | Kiedy używać |
|--------|---------------|-------------|
| `parse_knowledge_base.py` | Konwersja TXT/DOCX/PDF → JSON | Przy dodaniu nowych dokumentów |
| `load_knowledge_base.py` | Załadowanie bazy (ZNISZCZA starą) | Pełna reinicjalizacja |
| `update_knowledge.py` | Aktualizacja przyrostowa (bezpieczna) | **REGULARNIE** - bezpieczne dodawanie |
| `verify_knowledge_base.py` | Weryfikacja poprawności danych | Po załadowaniu |
| `delete_qdrant_collection.py` | Usunięcie kolekcji | Czyszczenie testów |
| `query_logger.py` | Podgląd logów zapytań | Analiza trendów |

**Dodawanie nowych dokumentów (bezpieczne):**
```bash
cd /opt/chatbot-project/agents/agent1_student

# 1. Umieść nowe dokumenty w chatbot-baza-wiedzy-nowa/
cp -r ~/nowe_dokumenty ./chatbot-baza-wiedzy-nowa/

# 2. Uruchom aktualizację (BEZPIECZNA - nie usuwaj starych)
python helpers/update_knowledge.py

# 3. Zweryfikuj
python helpers/verify_knowledge_base.py
```

**Pełny reload (tylko w przypadku problemów):**
```bash
cd /opt/chatbot-project/agents/agent1_student

# OSTRZEŻENIE: Usunie wszystkie stare dokumenty!
python helpers/load_knowledge_base.py
```

**Więcej szczegółów:** [docs_agent1/knowledge.md](docs_agent1/knowledge.md)

## Daily Operations

### Monitorowanie usług

**Sprawdzenie statusu wszystkich kontenerów:**
```bash
ssh pboguski@57.128.212.194
cd /opt/chatbot-project
docker ps  # Powinno być 6+ kontenerów
```

**Realtime monitoring:**
```bash
# CPU, RAM, sieć dla wszystkich kontenerów
docker stats

# Tylko Agent1
docker stats agent1_student
```

### Restarty usług

**Restart konkretnego agenta:**
```bash
cd /opt/chatbot-project/agents/agent1_student
docker compose restart
```

**Restart Ollama (LLM):**
```bash
sudo systemctl restart ollama
```

### Aktualizacja kodu

**Pobranie najnowszych zmian z `main` (produkcja):**
```bash
cd /opt/chatbot-project
git fetch origin
git checkout main
git pull origin main

# Restart agentów aby stosowały nowy kod
cd agents/agent1_student && docker compose restart
```

**Testowanie na `beta` przed produkcją:**
```bash
git checkout beta
git pull origin beta

# Testy...

# Jeśli OK -> merge do main
git checkout main
git merge beta
git push origin main
```

### Sprawdzenie logów

**Ostatnie 50 linii logów Agent1:**
```bash
docker logs agent1_student --tail 50

# Live (w czasie rzeczywistym)
docker logs agent1_student -f
```

**Logi Ollama:**
```bash
sudo journalctl -u ollama -n 100
```

**Logi Node-RED:**
```bash
docker logs node-red --tail 100
```

### Backup'y

**Backup bazy wektorowej Qdrant:**
```bash
# Export via API
curl http://10.0.0.1:6333/telemetry -o qdrant-backup.json

# Lub bezpośrednio katalog Docker volume
sudo tar -czf qdrant-backup-$(date +%Y%m%d).tar.gz /var/lib/docker/volumes/chatbot-qdrant/_data/
```

**Backup całego projektu:**
```bash
cd /opt && sudo tar -czf chatbot-backup-$(date +%Y%m%d).tar.gz chatbot-project/
```

## Git Workflow (Strategia Branchowania)

**Projekt używa dwóch głównych branchy:**

| Branch | Przeznaczenie | Kto commituje | Kiedy mergować |
|--------|---------------|---------------|-----------------|
| **`beta`** | Roboczy/deweloperski | Cały zespół | Daily merges OK |
| **`main`** | Produkcyjny (stabilny) | Tylko proven code | Po testach |

**Detale:**
- **`beta`** → Tutaj pracuje cały zespół równolegle; można commitować eksperymentalne zmiany; w razie konfliktów, `main` jest zabezpieczeniem
- **`main`** → Tylko w pełni działające i przetestowane funkcje; merge z `beta` tylko po weryfikacji; wersja "ostatnia działająca"

**Workflow dla pracy na serwerze:**
```bash
# 1. SSH na serwer
ssh pboguski@57.128.212.194

# 2. Przejdź do projektu
cd /opt/chatbot-project

# 3. Upewnij się że jesteś na beta
git checkout beta
git pull origin beta

# 4. Pracuj lokalnie i commituj zmiany
git add .
git commit -m "feat(agent1): nowa funkcja"

# 5. Push do beta
git push origin beta

# 6. Testy na serwerze (np. restart kontenerów)
cd agents/agent1_student && docker compose restart

# 7. TYLKO gdy funkcja działa PRODUCTION-READY -> merge do main
git checkout main
git pull origin main
git merge beta
git push origin main

# 8. Informuj zespół na tym branch'u
git checkout beta  # wróć na branch roboczy
```

**Przykładowe commity (Conventional Commits):**
```
feat(agent1): dodanie obsługi stypendiów
fix(ollama): naprawa timeoutu połączenia
docs: aktualizacja README i DEPLOYMENT.md
chore: konfiguracja docker-compose
test(agent1): dodanie testów API
refactor(knowledge): optymalizacja parsowania dokumentów
```

**Merge PR workflow (jeśli używacie GitHub Web):**
1. Utwórz Pull Request: `beta` → `main`
2. Opisz zmiany i testowanie
3. Czekaj na review dwóch osób
4. Merge po zatwierddzeniu
5. Delete branch po merge'u


## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Mikołaj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Paweł Ponikowski (pponikowski)
