# Instrukcja dostępu do wdrożonego chatbota

## Połączenie VPN (WYMAGANE)

Wszystkie usługi są zabezpieczone przez firewall i dostępne tylko przez VPN WireGuard.

### Instalacja i konfiguracja VPN

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

## Konfiguracja serwera

### Dane dostępowe
- Adres publiczny: 57.128.212.194
- Hostname: vps-5f2a574b.vps.ovh.net
- System: Ubuntu 24.04 LTS
- Użytkownik: asiehen

### Sieć Docker
- Nazwa: ai_network
- Typ: bridge
- Zakres: 172.18.0.0/16

### Sieć VPN
- Zakres: 10.0.0.0/24
- Serwer: 10.0.0.1
- Klient: 10.0.0.2
- Interface: wg0

## Git Workflow (Strategia Branchowania)

**Ważne:** Projekt używa dwóch głównych branchy:

- **`beta`** - branch roboczy/deweloperski (domyślny dla pracy)
  - Tutaj pracuje cały zespół równolegle
  - Można commitować eksperymentalne zmiany
  - W razie konfliktów lub błędów, `main` jest zabezpieczeniem

- **`main`** - branch produkcyjny (stabilny)
  - Tylko w pełni działające i przetestowane funkcje
  - Merge z `beta` tylko po weryfikacji
  - To jest wersja "ostatnia działająca"

**Workflow dla pracy na serwerze:**
```bash
# 1. Przejdź do projektu
cd /opt/chatbot-project

# 2. Upewnij się że jesteś na beta
git checkout beta
git pull origin beta

# 3. Pracuj i commituj zmiany
git add .
git commit -m "feat(agent1): nowa funkcja"

# 4. Push do beta
git push origin beta

# 5. TYLKO gdy funkcja działa -> merge do main
git checkout main
git merge beta
git push origin main
git checkout beta  # wróć na branch roboczy
```

**Przykładowe commity (Conventional Commits):**
- `feat(agent1): dodanie obsługi stypendiów`
- `fix(ollama): naprawa timeoutu połączenia`
- `docs: aktualizacja README`
- `chore: konfiguracja docker-compose`
