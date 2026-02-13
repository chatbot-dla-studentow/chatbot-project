# 🚀 Wdrożenie na Świeży VPS - Szybki Przewodnik

> ⚠️ **WAŻNE - Breaking Change:** Stare pliki `agents/*/docker-compose.yml` zostały **usunięte**. 
> Aby wdrożyć system, **musisz używać** `/deployment/setup-new-vps.sh` lub główny `docker-compose.yml` z głównego katalogu!

## 📖 Struktura Folderu `deployment/`

```
deployment/
├── setup-new-vps.sh                 # Główny skrypt (uruchom pierwszy!)
│
├── server/                          # Skrypty konfiguracji SERWERA
│   ├── secure.sh                   # Security hardening
│   ├── geo-blocking.sh             # EU-only geo-blocking
│   └── monitoring-alerts.sh        # Email alerts & monitoring
│
├── app/                             # Skrypty wdrożenia APLIKACJI
│   ├── deploy.sh                   # Linux deployment
│   ├── deploy.ps1                  # Windows PowerShell deployment
│   ├── health-check.sh             # Monitoring systemu
│   ├── backup.sh                   # Backup wolumenów Docker
│   ├── restore.sh                  # Restore z backupów
│   ├── init-knowledge.sh           # Inicjalizacja bazy wiedzy
│   └── test-system.sh              # Testy automatyczne
│
└── docs/                            # Dokumentacja
    ├── README.md                   # Ten plik
    └── SECURITY.md                 # Szczegółowa dokumentacja bezpieczeństwa
```

## ⚡ Quick Start (3 minuty)

### Na świeżym VPS (Ubuntu 24.04 LTS):

```bash
# 1. SSH do VPS
ssh root@<vps-ip>

# 2. Sklonuj projekt
git clone https://github.com/yourusername/chatbot-project.git /opt/chatbot-project
cd /opt/chatbot-project/deployment

# 3. Uruchom setup (następi seria pytań/konfiguracji)
chmod +x setup-new-vps.sh
./setup-new-vps.sh
```

**Gotowe!** System będzie w pełni zabezpieczony i wdrożony.

---

## 📋 Co setup robi

### Phase 1: Security Hardening (`secure.sh`)
- ✅ Instalacja `fail2ban` - ochrona przed brute-force
- ✅ Konfiguracja `UFW` - firewall z dostępem tylko przez VPN
- ✅ SSH hardening - port 2222, key auth only, no root
- ✅ Network security - SYN cookies, IP spoofing protection
- ✅ Automatic updates - security patches codziennie
- ✅ Logging - centralizowane logowanie zdarzeń

**Czas:** ~5 minut

### Phase 2: Geo-Blocking (`geo-blocking.sh`)
- ✅ EU-only IP ranges - blokuje dostęp spoza UE
- ✅ Weekly updates - IP ranges aktualizowane co tydzień
- ✅ ipset integration - efektywne filtrowanie

**Czas:** ~2 minuty

### Phase 3: Monitoring (`monitoring-alerts.sh`)
- ✅ Email alerts - alerts na adam.siehen@outlook.com
- ✅ Health monitoring - CPU, RAM, disk, Docker
- ✅ Security audits - szczegółowy dzienny raport
- ✅ fail2ban integration - alerty przy ban/unban

**Czas:** ~3 minuty

### Phase 4: Application Deployment (`deploy.sh`)
- ✅ Docker installation
- ✅ Infrastructure (Qdrant, Ollama, Node-RED)
- ✅ Model download (mistral:7b)
- ✅ Knowledge base loading
- ✅ All 5 agents start

**Czas:** ~8-10 minut

---

## 🔐 Security Settings

| Ustawienie | Wartość |
|-----------|---------|
| SSH Port | 2222 |
| SSH Auth | Keys only (no passwords) |
| Firewall | UFW - VPN only |
| VPN Subnet | 10.0.0.0/24 |
| fail2ban Ban | 1 godzina |
| fail2ban Retries | 3 |
| Updates | Automatic (daily) |
| Geo-Block | EU countries only |
| Alerts Email | adam.siehen@gmail.com |
| Alert Frequency | Every 4 hours + daily |

---

## 📌 Ważne Informacje

### Dostęp SSH zmienia się:

**Przed:**
```bash
ssh root@57.128.212.194
```

**Po (port 2222, key auth):**
```bash
ssh -p 2222 asiehen@<new-vps-ip>
# lub jeśli dodane do ~/.ssh/config
ssh chatbot-vps
```

### Dostęp do aplikacji

Wszystkie porty dostępne **tylko z VPN**:
- Port 8001: Agent1 API
- Port 6333: Qdrant
- Port 11434: Ollama
- Port 1880: Node-RED
- Port 3000: Open WebUI

### Monitoring

Będziesz otrzymywać emaile na `adam.siehen@gmail.com` gdy:
- Dysk > 85%
- RAM > 90%
- Docker padł
- SSH brute-force attempt
- fail2ban ban someone
- System reboot
- Service crash

---

## 🛠️ Ręczne Kroki (jeśli chcesz wybrać co instalować)

### Tylko security (bez deployment):

```bash
cd /opt/chatbot-project/deployment
sudo ./secure.sh
# Opcjonalnie:
sudo ./geo-blocking.sh
sudo ./monitoring-alerts.sh
```

### Tylko deployment (po security setupie):

```bash
cd /opt/chatbot-project
sudo ./deploy.sh install_dependencies
./deploy.sh deploy
```

---

## 📊 Monitorowanie

### View system status:
```bash
chatbot-status
```

### View live logs:
```bash
cd /opt/chatbot-project
./deploy.sh logs

# Lub konkretny serwis:
./deploy.sh logs agent1_student
```

### Check fail2ban:
```bash
fail2ban-client status
fail2ban-client status sshd
```

### Check firewall:
```bash
sudo ufw status verbose
```

---

## ⚠️ Common Issues

### Issue: Can't SSH after setup

**Sprawdź:**
```bash
# SSH jest na porcie 2222
ssh -p 2222 asiehen@<vps-ip>

# Dodaj klucz jeśli jeszcze nie
ssh-copy-id -i ~/.ssh/id_rsa -p 2222 asiehen@<vps-ip>
```

### Issue: Porty nie dostępne

**Sprawdzenia:**
```bash
# Czy firewall pozwala?
sudo ufw status verbose

# Czy serwis słucha?
sudo netstat -tulpn | grep 8001
sudo ss -tulpn | grep 8001

# Czy VPN aktywna?
ping 10.0.0.1  # Powinno działać
```

### Issue: Brak emaili z alertami

**Sprawdzenia:**
```bash
# Czy postfix działa?
systemctl status postfix

# Test send email:
echo "Test" | mail -s "Test" adam.siehen@gmail.com

# Pokaż logi:
tail -f /var/log/mail.log
```

---

## 📚 Dodatkowa Dokumentacja

- [SECURITY.md](SECURITY.md) - Szczegółowe ustawienia bezpieczeństwa
- [../DEPLOYMENT.md](../DEPLOYMENT.md) - Pełna dokumentacja deployment
- [../README_DEPLOYMENT.md](../README_DEPLOYMENT.md) - Deployment overview

---

## 🎯 Po Instalacji

### 1. Sprawdź dostęp przez VPN:
```bash
# Powinna być aktywna WireGuard
ping 10.0.0.1
```

### 2. Test SSH connection:
```bash
ssh -p 2222 asiehen@<vps-ip>
./deploy.sh status
```

### 3. Test aplikacji:
```bash
curl http://10.0.0.1:8001/docs  # Agent1 swagger docs
```

### 4. Setup regular backups:
```bash
crontab -e
# Dodaj:
# 0 2 * * * /opt/chatbot-project/backup.sh /opt/chatbot-backups >> /var/log/backup.log 2>&1
```

---

**Gotowe!** VPS jest teraz bezpieczny i pełen funkcjonalny. 🎉
