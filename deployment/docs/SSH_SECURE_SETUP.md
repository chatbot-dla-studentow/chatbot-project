# SSH Super Bezpieczne Setup

> 🔒 SSH dostępny TYLKO z VPN, port 2222, key-based auth, fail2ban protection

## Architektura Bezpieczeństwa

```
Internet (39.128.212.194)
     ↓ X - port 22,2222 DENY
     ↓
VPN Network (10.0.0.0/24)
     ↓ ✅ - port 2222 ALLOW
     ↓
SSH @ 10.0.0.1:2222
  - Key-based auth only
  - fail2ban (3 tries = 1h ban)
  - No root login
  - No password auth
```

## Setup na VPS (w console'u)

```bash
# Skopiuj skrypt
sudo bash deployment/server/ssh-secure-setup.sh
```

To automatycznie:
- ✅ Włączy SSH na porcie 2222
- ✅ Skonfiguruje sshd_config (VPN only)
- ✅ Zainstaluje fail2ban
- ✅ Otworzy UFW rules
- ✅ Sprawdzi config

---

## SSH Klucz na Windows

Jeśli jeszcze nie masz - wygeneruj:

```powershell
# Nowy klucz
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\chatbot_vps_new" -C "vps-ssh" -N ""

# Pokaż public key - skopiuj
Get-Content "$env:USERPROFILE\.ssh\chatbot_vps_new.pub"
```

---

## Dodaj klucz do VPS

W console'u VPS:

```bash
# Edytuj authorized_keys
nano ~/.ssh/authorized_keys

# Wklej public key z powyżej (całą linjkę)
# Ctrl+X → Y → Enter
```

---

## Załaduj WireGuard na Windows

1. Pobierz WireGuard: https://www.wireguard.com/install/
2. Zaladuj `wg-client.conf` z repo
3. Connect

---

## Test SSH (gdy WireGuard aktywny)

```powershell
# Port 2222, user ubuntu, z WireGuard VPN
ssh -i $env:USERPROFILE\.ssh\chatbot_vps_new -p 2222 ubuntu@10.0.0.1

# Powinno być: ubuntu@chatbot-vps:~$ ✅
```

---

## SSH Config - co jest bezpieczne?

### ✅ Secured

- **Port 2222** - niestandardowy, ukryty
- **ListenAddress 10.0.0.1** - tylko VPN
- **PermitRootLogin no** - root disable
- **PasswordAuthentication no** - passwords blocked
- **MaxAuthTries 3** - 3 nieudane próby
- **ClientAliveInterval 300** - timeout po 5 min inactivity
- **fail2ban** - 3 tries = 1h ban

### Kryptografia (Modern)

```
Key Exchange: curve25519
Cipher: chacha20-poly1305 + aes-256-gcm
MAC: hmac-sha2-512-etm (Encrypt-Then-MAC)
```

---

## Monitorowanie

### Fail2ban status

```bash
sudo fail2ban-client status sshd
sudo fail2ban-client set sshd unbanip 1.2.3.4  # Odban IP jeśli trzeba
```

### SSH Logs

```bash
# Ostatnie 20 linii
sudo tail -f /var/log/auth.log

# Szukaj failed attempts
sudo grep "Failed password" /var/log/auth.log | tail -10
```

### UFW Rules

```bash
sudo ufw status numbered
```

---

## Troubleshooting

### Connection refused (2222)

```bash
# Na VPS:
sudo ss -tlnp | grep ssh  # Powinno być 10.0.0.1:2222

# UFW:
sudo ufw status | grep 2222

# SSH status:
sudo systemctl status ssh
```

### Bad permissions on ~/.ssh/authorized_keys

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### WireGuard nie podłącza

```bash
# Na Windows
ipconfig /all  # Szukaj tun0 z 10.0.0.2

# Ping test
ping 10.0.0.1
```

---

## Dodatkowe Zabezpieczenie (opcjonalnie)

### Whitelist GitHub Actions IP (jeśli będziesz używać)

GitHub Actions runners mają publiczne IP. Możesz:

```bash
# Dodaj rule dla GitHub IPs (opcjonalnie)
sudo ufw allow from 140.82.112.0/20 to 10.0.0.1 port 2222 comment "GitHub Actions"
```

---

## Maintainers

- **Adam Siehen** - SSH hardening, security configuration
- **Patryk Boguski** - VPS infrastructure, fail2ban setup
