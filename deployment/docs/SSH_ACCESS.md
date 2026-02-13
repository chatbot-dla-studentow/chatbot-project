# 🔐 SSH Access - Dokumentacja

> **VPS:** `51.68.151.45` | **User:** `ubuntu` | **Hostname:** `vps-fcbe5571.vps.ovh.net`

---

## 📍 Klucze SSH (Lokalizacja)

```
C:\Users\adams\.ssh\
├── chatbot_vps_new       ← 🔒 PRYWATNY (NIGDY NIE UDOSTĘPNIAJ!)
└── chatbot_vps_new.pub   ← 🔓 PUBLICZNY (bezpieczny do udostępnienia)
```

---

## 🚀 Logowanie do VPS

### Metoda 1: Z kluczem SSH (rekomendowane)

```powershell
# Pełna ścieżka
ssh -i $HOME\.ssh\chatbot_vps_new ubuntu@51.68.151.45

# Lub z config (patrz poniżej)
ssh vps
```

### Metoda 2: Alias SSH (najwygodniejsze)

**Utwórz plik:** `C:\Users\adams\.ssh\config`

```ssh-config
Host vps
    HostName 51.68.151.45
    User ubuntu
    IdentityFile ~/.ssh/chatbot_vps_new
    Port 22

Host vps-name
    HostName vps-fcbe5571.vps.ovh.net
    User ubuntu
    IdentityFile ~/.ssh/chatbot_vps_new
    Port 22
```

**Teraz możesz:**
```powershell
ssh vps              # Szybkie logowanie przez IP
ssh vps-name         # Szybkie logowanie przez hostname
```

---

## 👥 Jak Dać Dostęp Innej Osobie

### Krok 1: Osoba generuje swój klucz SSH (u siebie)

```bash
ssh-keygen -t ed25519 -C "osoba@email.com"
# Enter 3 razy (bez passphrase dla wygody)
```

### Krok 2: Osoba wysyła Ci klucz PUBLICZNY

Osoba wysyła zawartość:
```bash
cat ~/.ssh/id_ed25519.pub
```

Dostaniesz linię typu:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEw... osoba@email.com
```

### Krok 3: Dodajesz klucz na VPS

```bash
# Zaloguj się do VPS
ssh vps

# Dodaj klucz osoby
echo "WKLEJ_TU_KLUCZ_PUBLICZNY_OSOBY" >> ~/.ssh/authorized_keys

# Ustaw uprawnienia
chmod 600 ~/.ssh/authorized_keys
```

### Krok 4: Osoba może się zalogować

```bash
ssh ubuntu@51.68.151.45
```

---

## 🔐 Bezpieczeństwo

### ✅ Bezpieczne Praktyki

| Co | Czy bezpieczne? | Dlaczego? |
|----|----------------|-----------|
| 🔓 Wysłać `chatbot_vps_new.pub` | ✅ TAK | To klucz publiczny - jak kłódka |
| 🔒 Wysłać `chatbot_vps_new` | ❌ **NIGDY!** | To klucz prywatny - jak hasło! |
| 💾 Backup klucza prywatnego | ✅ TAK | Ale tylko na bezpiecznym nośniku (USB, sejf) |
| 📧 Email z kluczem prywatnym | ❌ **NIGDY!** | Niezabezpieczone |

### ⚠️ Jeśli Klucz Prywatny Wyciekł

```bash
# 1. Zaloguj się hasłem (jeśli masz) lub przez KVM w panelu OVH
ssh ubuntu@51.68.151.45

# 2. Usuń skompromitowany klucz z authorized_keys
nano ~/.ssh/authorized_keys
# Usuń linię ze starym kluczem

# 3. Wygeneruj NOWY klucz (lokalnie na Windows)
ssh-keygen -t ed25519 -f $HOME\.ssh\chatbot_vps_emergency -N '""'

# 4. Dodaj nowy klucz
type $HOME\.ssh\chatbot_vps_emergency.pub | ssh ubuntu@51.68.151.45 "cat >> ~/.ssh/authorized_keys"
```

---

## 🛠️ Konfiguracja Zaawansowana

### Wyłączenie Logowania Hasłem (zwiększone bezpieczeństwo)

**⚠️ Zrób to TYLKO gdy klucz SSH działa!**

```bash
# Zaloguj się do VPS
ssh vps

# Edytuj konfigurację SSH
sudo nano /etc/ssh/sshd_config

# Znajdź i zmień:
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no

# Zapisz: Ctrl+O, Enter, Ctrl+X

# Restart SSH
sudo systemctl restart sshd
```

### Zmiana Portu SSH (dodatkowe bezpieczeństwo)

```bash
# Edytuj konfigurację
sudo nano /etc/ssh/sshd_config

# Zmień:
Port 2222

# Otwórz port w firewall
sudo ufw allow 2222/tcp
sudo ufw delete allow 22/tcp

# Restart SSH
sudo systemctl restart sshd
```

**Logowanie:**
```powershell
ssh -i $HOME\.ssh\chatbot_vps_new -p 2222 ubuntu@51.68.151.45
```

---

## 📋 Troubleshooting

### Problem: "Permission denied (publickey)"

**Rozwiązanie:**
```bash
# Sprawdź uprawnienia klucza (lokalnie)
icacls $HOME\.ssh\chatbot_vps_new

# Sprawdź uprawnienia na VPS
ssh vps "ls -la ~/.ssh/"
# authorized_keys powinno być 600
# .ssh powinno być 700
```

### Problem: "Too many authentication failures"

**Rozwiązanie:**
```powershell
# Podaj klucz explicite
ssh -o IdentitiesOnly=yes -i $HOME\.ssh\chatbot_vps_new ubuntu@51.68.151.45
```

### Problem: Zapomniałem hasła ubuntu

**Rozwiązanie:**
1. Zaloguj się przez **KVM** w panelu OVH
2. Zresetuj hasło:
```bash
sudo passwd ubuntu
```

---

## 📞 Kontakt VPS

- **Panel:** https://www.ovh.com/manager/
- **IP:** `51.68.151.45`
- **IPv6:** `2001:41d0:601:1100::8533`
- **VPS Name:** `vps-fcbe5571.vps.ovh.net`
- **System:** Ubuntu 24.04 LTS

---

## 🔗 Powiązane Dokumenty

- [deployment/docs/README.md](README.md) - Quick start guide
- [deployment/docs/SECURITY.md](SECURITY.md) - Security configuration
- [DEPLOYMENT.md](../../DEPLOYMENT.md) - Main deployment guide

---

**Ostatnia aktualizacja:** 13.02.2026

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Paweł Ponikowski (pponikowski)
