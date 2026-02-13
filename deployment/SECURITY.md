# 🛡️ ChatBot VPS Security Configuration

## Quick Security Setup

Kompleksowe zabezpieczenie świeżego VPS przed atakami i zagrożeniami.

### 📋 Co jest konfigurowane?

1. **fail2ban** - Ochrona przed brute-force atakami SSH
2. **UFW Firewall** - Zapora sieciowa z dostępem tylko przez VPN
3. **SSH Hardening** - Zmiana portu, wyłączenie hasła, key auth only
4. **Network Security** - SYN cookies, IP spoofing protection, rate limiting
5. **Automatic Updates** - Codziennie Security patches
6. **Geo-Blocking** - Dostęp tylko z UE
7. **Monitoring & Alerting** - Email alerts na adam.siehen@outlook.com
8. **Centralized Logging** - Wszystkie zdarzenia bezpieczeństwa logowane

---

## 🚀 Instalacja na Świeżym VPS

### Krok 1: Połącz się z VPS

```bash
ssh root@<vps-ip>
```

### Krok 2: Zaklonuj repozytorium

```bash
git clone <your-repo> /opt/chatbot-project
cd /opt/chatbot-project
```

### Krok 3: Uruchom interaktywny setup (ALL-IN-ONE)

```bash
# Użyj głównego skryptu który robi wszystko:
chmod +x deployment/setup-new-vps.sh
sudo ./deployment/setup-new-vps.sh
```

**Alternatywnie - Krok po kroku (manual):**
```bash
# 1. Główny security hardening (obowiązkowy)
sudo chmod +x deployment/secure.sh
sudo ./deployment/secure.sh

# 2. Geo-blocking dla UE (zalecane)
sudo chmod +x deployment/geo-blocking.sh
sudo ./deployment/geo-blocking.sh

# 3. Monitoring i alerty (zalecane)
sudo chmod +x deployment/monitoring-alerts.sh
sudo ./deployment/monitoring-alerts.sh

# 4. Wdróż aplikację
sudo chmod +x deploy.sh
sudo ./deploy.sh install_dependencies
./deploy.sh deploy
```

---

## 📊 Szczegółowa Konfiguracja

### 1. fail2ban - SSH Brute Force Protection

**Konfiguracja:**
- Ban time: 1 godzina
- Max retries: 3 próby
- Monitoring period: 10 minut

**Logowanie:** `/var/log/fail2ban.log`

**Widok bańów:**
```bash
fail2ban-client status
fail2ban-client status sshd
```

**Ręczne zabanowanie IP:**
```bash
fail2ban-client set sshd banip <ip-address>
```

**Odbanowanie IP:**
```bash
fail2ban-client set sshd unbanip <ip-address>
```

---

### 2. UFW Firewall - Port Whitelisting

**Tylko dostęp przez VPN:**

Otwarte porty:
- **22, 2222** - SSH (tylko z VPN)
- **8001-8005** - Agenci API (tylko z VPN)
- **6333** - Qdrant (tylko z VPN)
- **11434** - Ollama (tylko z VPN)
- **1880** - Node-RED (tylko z VPN)
- **3000** - Open WebUI (tylko z VPN)

```bash
# Pokaż status firewalla
sudo ufw status verbose

# Pokaż detale
sudo ufw show raw

# Dodaj nową regułę
sudo ufw allow from 10.0.0.0/24 to any port 8001 proto tcp
```

---

### 3. SSH Hardening

**Nowy SSH port:** 2222

**Wyłączone:**
- ✗ Root login
- ✗ Password authentication
- ✗ Empty passwords
- ✗ X11 forwarding

**Włączone:**
- ✓ Public key authentication
- ✓ Ed25519 keys
- ✓ Secure ciphers (chacha20-poly1305, aes256-gcm)
- ✓ Secure key exchange
- ✓ Login banner

**Aktualizuj SSH client config:**

```bash
# ~/.ssh/config
Host chatbot-vps
    HostName <vps-ip>
    Port 2222
    User asiehen
    IdentityFile ~/.ssh/id_rsa
    StrictHostKeyChecking accept-new
```

**Zaloguj się:**
```bash
ssh chatbot-vps
# lub
ssh -i ~/.ssh/id_rsa -p 2222 asiehen@<vps-ip>
```

---

### 4. Network Security Hardening

**Włączone:**
- SYN cookies (ochrona przed SYN flood)
- IP spoofing protection (rp_filter)
- ICMP redirect protection
- Log martians
- TCP hardening
- Kernel security flags

**Plik konfiguracji:**
```bash
cat /etc/sysctl.conf | grep -A 50 "Network Security"
```

---

### 5. Automatic Security Updates

**Włączone:**
- Automatic `apt update` - codziennie
- Automatic `apt upgrade` - dla security patches
- Automatic reboot - DISABLED (aby nie przerwać usługi)

**Logi:**
```bash
tail -f /var/log/unattended-upgrades/unattended-upgrades.log
```

**Ręczna aktualizacja:**
```bash
sudo apt update
sudo apt upgrade -y
```

---

### 6. Geo-Blocking - EU Only Access

**Kraje UE:** AT, BE, BG, HR, CY, CZ, DK, EE, FI, FR, DE, GR, HU, IE, IT, LV, LT, LU, MT, NL, PL, PT, RO, SK, SI, ES, SE

**IP ranges:** Automatycznie pobierane i aktualizowane codziennie

**Weryfikacja:**
```bash
ipset list eu_ips
```

**Ręczna aktualizacja:**
```bash
sudo /usr/local/bin/update-geo-blocking.sh
```

---

### 7. Monitoring & Alerting

**Email alerts:** adam.siehen@outlook.com

**Sprawdzane:**
- Użycie dysku (> 85% = alert)
- Użycie RAM (> 90% = alert)
- Load average (> CPU cores * 1.5 = alert)
- Docker daemon status
- Kontener status (qdrant, ollama, agent1, node-red)
- fail2ban active bans
- SSH security events
- System reboot

**Harmonogram:**
- Health check: Co 4 godziny
- Security audit: Codziennie o 7 AM
- Service tracking: Codziennie o 8 AM
- Geo-blocking update: Co tydzień (Niedziela 3 AM)

**Przegląd dashboardu:**
```bash
chatbot-status
```

**Ręczne sprawdzenie zdrowia:**
```bash
sudo /usr/local/lib/chatbot-monitors/check-health.sh
```

**Ręczny security audit:**
```bash
sudo /usr/local/lib/chatbot-monitors/security-audit.sh
```

---

## 🔐 Best Practices

### 1. SSH Keys

```bash
# Generuj klucz (jeśli nie masz)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Skopiuj klucz na VPS
ssh-copy-id -i ~/.ssh/id_ed25519 -p 2222 asiehen@<vps-ip>
```

### 2. Fail2ban Monitoring

```bash
# Monitoruj bany w real-time
tail -f /var/log/fail2ban.log | grep Ban

# Sprawdź wszystkie bany
fail2ban-client status --all

# Przywracaj IPs, gdy uznajesz za bezpieczne
sudo fail2ban-client set sshd unbanip <ip>
```

### 3. Firewall Testing

```bash
# Z maszyny, która NIE jest w VPN (powinno być zablokowane)
nmap -p 2222,8001 <vps-ip>  # Powinno być closed

# Z VPN (powinno być accessible)
ssh -p 2222 asiehen@10.0.0.1  # Powinno działać
```

### 4. Logi Bezpieczeństwa

```bash
# SSH attempts
grep "sshd" /var/log/auth.log | tail -50

# fail2ban bans
grep "Ban" /var/log/fail2ban.log | tail -50

# Firewall rejects
sudo tail -f /var/log/ufw.log

# Wszystkie security events
sudo journalctl -u fail2ban -u ufw -n 100
```

### 5. Regular Backups

```bash
# Backup konfiguracji bezpieczeństwa
sudo tar czf /tmp/security-backup.tar.gz \
  /etc/ssh/sshd_config \
  /etc/fail2ban/ \
  /etc/ufw/ \
  /etc/sysctl.conf

# Backup bazy danych
/opt/chatbot-project/backup.sh
```

---

## ⚠️ Częste Problemy

### Problem: "Connection refused" na porcie 2222

**Rozwiązanie:**
```bash
# Sprawdź czy SSH nasłuchuje na porcie 2222
sudo netstat -tulpn | grep ssh
sudo ss -tulpn | grep ssh

# Zmień port wstecz lub dodaj regułę UFW
sudo ufw allow from 10.0.0.0/24 to any port 2222 proto tcp
sudo systemctl restart ssh
```

### Problem: fail2ban bani mnie

**Rozwiązanie:**
```bash
# Sprawdź czy IP jest zbanowane
fail2ban-client status sshd | grep "Banned IP"

# Odbanuj się
sudo fail2ban-client set sshd unbanip <your-ip>

# Sprawdzaj logi
tail -f /var/log/fail2ban.log
```

### Problem: Nie dostaję emaili

**Rozwiązanie:**
```bash
# Sprawdź postfix status
sudo systemctl status postfix

# Sprawdzanie queue
mailq

# Test
echo "Test" | mail -s "Test" adam.siehen@gmail.com

# Logi
sudo tail -f /var/log/mail.log
```

### Problem: UFW blokuje port 8001

**Rozwiązanie:**
```bash
# Lista reguł
sudo ufw show added

# Sprawdzenie konkretnej reguły
sudo ufw status verbose | grep 8001

# Dodaj regułę
sudo ufw allow from 10.0.0.0/24 to any port 8001 proto tcp

# Reload
sudo ufw reload
```

---

## 📋 Checklist Bezpieczeństwa

- [ ] fail2ban zainstalowany i aktywny
- [ ] UFW firewall zainstalowany i aktywny
- [ ] SSH port zmieniony na 2222
- [ ] SSH keys zainstalowane (no password auth)
- [ ] Automatic updates włączone
- [ ] Geo-blocking skonfigurowany dla UE
- [ ] Monitoring alerts działają
- [ ] Otrzymywasz test email na adam.siehen@gmail.com
- [ ] VPN connection testowana
- [ ] Backup strategy wdrożona
- [ ] SSH client skonfigurowany
- [ ] Logi sprawdzane regularnie

---

## 🔗 Kolejne Kroki

1. Po uruchomieniu setupów: `./deploy.sh deploy`
2. Sprawdź status: `./deploy.sh status`
3. Test zdrowia: `./health-check.sh`
4. Backup: `/opt/chatbot-project/backup.sh`

---

## 📞 Support

Jeśli coś nie działa:

```bash
# Sprawdzaj logi
sudo journalctl -xe

# Sprawdzaj fail2ban
tail -f /var/log/fail2ban.log

# Sprawdzaj firewall
sudo ufw show raw

# Sprawdzaj SSH
sudo sshd -T
```

---

**Gotowe!** VPS jest teraz zabezpieczony. 🛡️
