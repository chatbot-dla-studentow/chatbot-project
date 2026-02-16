# Instrukcje Konfiguracji: GitHub Actions + WireGuard Deployment

> ⚠️ **UWAGA:** Rzeczywiste wartości IP, kluczy i credentials znajdują się w prywatnym folderze `private/docs/GITHUB_ACTIONS_SETUP.md` (OneDrive backup)

## 1. Setup WireGuard na VPS

### Krok 1: Uruchomić setup skrypt

```bash
ssh <USER>@<VPS_IP>
sudo bash -c "$(curl -s https://raw.githubusercontent.com/chatbot-dla-studentow/chatbot-project/main/deployment/server/wireguard-setup.sh)"
```

Lub lokalnie z repo:
```bash
scp deployment/server/wireguard-setup.sh <USER>@<VPS_IP>:~/
ssh <USER>@<VPS_IP> 'sudo bash ~/wireguard-setup.sh'
```

### Krok 2: Zapisać wygenerowane klucze z outputu

Skrypt wygeneruje:
```
Private Key: [ZAPISZ TO DO private/configs/]
Public Key: [ZAPISZ TO DO private/docs/]
```

**⚠️ WAŻNE:** Zapisz te klucze w bezpiecznym miejscu (OneDrive private/) - będą potrzebne dla GitHub Actions!

### Krok 3: Sprawdzić status WireGuard

```bash
ssh <USER>@<VPS_IP>
sudo wg show
```

Powinno pokazać:
```
interface: wg0
  public key: [klucz serwera]
  listen port: 51820

peer: [PEER_PUBLIC_KEY]
  endpoint: X.X.X.X:XXXXX
  allowed ips: 10.0.0.2/32
  latest handshake: ...
  transfer: ... received, ... sent
```

---

## 2. Generowanie SSH klucza dla GitHub Actions

### Lokalnie (na Windows/Dev maszynie):

```powershell
# Wygeneruj nowy klucz dla deployment
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\github_deploy" -C "github-actions-deploy" -N ""

# Pokaż public key
Get-Content "$env:USERPROFILE\.ssh\github_deploy.pub"
```

### Na VPS - dodaj public key do authorized_keys:

```bash
ssh <USER>@<VPS_IP>
echo "[WKLEJ_PUBLIC_KEY_Z_GÓRY]" >> ~/.ssh/authorized_keys
```

---

## 3. Konfiguracja GitHub Secrets

W ustawieniach repozytorium GitHub (Settings → Secrets and variables → Actions):

### Dodaj te Secrets:

| Secret Name | Wartość | Gdzie znaleźć |
|-------------|---------|---------------|
| `SSH_PRIVATE_KEY` | Zawartość `github_deploy` (cały plik, include BEGIN/END) | Wygenerowane w kroku 2 |
| `DEPLOY_USER` | Nazwa użytkownika SSH | Zazwyczaj `ubuntu` lub `root` |
| `DEPLOY_HOST` | `10.0.0.1` (VPN IP serwera) | IP wewnętrzne VPN |
| `WIREGUARD_PRIVATEKEY` | Private Key z `wireguard-setup.sh` output | Z kroku 1 |
| `WIREGUARD_PUBLICKEY` | Public Key z serwera **wg0.conf** | Zobacz poniżej |
| `WIREGUARD_ENDPOINT` | `<VPS_PUBLIC_IP>:51820` | Publiczny IP VPS + port 51820 |

### Gdzie znaleźć wartości:

**WIREGUARD_PUBLICKEY** - na serwerze:
```bash
ssh <USER>@<VPS_IP>
cat /etc/wireguard/publickey
```

**VPS_PUBLIC_IP** - znajdź w panelu VPS lub:
```bash
curl ifconfig.me
```

---

## 4. SSH - Ograniczyć dostęp tylko do VPN

Na VPS, edytuj `/etc/ssh/sshd_config`:

```bash
sudo nano /etc/ssh/sshd_config
```

Zmień/dodaj linie:
```
# Listen only on VPN interface
ListenAddress 10.0.0.1
Port 22

# Restrict to VPN network only
AllowUsers <USER>@10.0.0.0/24

# Security best practices
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
PrintMotd no
```

Zrestartuj SSH:
```bash
sudo systemctl restart ssh
sudo systemctl status ssh
```

---

## 5. Test GitHub Actions

### Lokalnie - trigger deployment:

```bash
git add deployment/
git commit -m "test: GitHub Actions deployment"
git push origin main
```

### Sprawdzić status w GitHub:

1. Otwórz: https://github.com/chatbot-dla-studentow/chatbot-project/actions
2. Kliknij ostatni workflow run
3. Sprawdź logi każdego kroku

### Debug - jeśli coś nie działa:

```bash
# Na serwerze - sprawdzić czy SSH działa z VPN IP
ssh -i ~/.ssh/github_deploy <USER>@10.0.0.1

# Check WireGuard status
sudo wg show

# Check SSH logs
sudo tail -f /var/log/auth.log

# Check UFW firewall
sudo ufw status
```

---

## 📚 Powiązana dokumentacja

- [deployment/docs/SSH_ACCESS.md](SSH_ACCESS.md) - Dostęp SSH (template)
- [deployment/docs/SECURITY.md](SECURITY.md) - Zabezpieczenia
- [README.md](../../README.md) - Główna dokumentacja
- [DEPLOYMENT.md](../../DEPLOYMENT.md) - Instrukcje deployment

---

**Rzeczywiste wartości (IP, klucze, credentials) znajdują się w:**
- `private/docs/GITHUB_ACTIONS_SETUP.md` (kopia z prawdziwymi danymi)
- `private/configs/wg-client.conf` (prawdziwa konfiguracja WireGuard)

📦 **Backup:** OneDrive → Praca inżynierska → chatbot-private/

---

## 6. Local Development - Zamiast Actions

Jeśli chcesz deployować ręcznie przez VPN:

```powershell
# Uruchom WireGuard (Windows - np. WireGuard Client)
# - Załaduj wg-client.conf
# - Connect do VPN

# Potem SSH będzie dostępny na 10.0.0.1
ssh -i $env:USERPROFILE\.ssh\github_deploy <USER>@10.0.0.1

# Na VPS - deployment
cd ~/chatbot-project
git pull origin main
bash deployment/app/deploy.sh update
bash deployment/app/deploy.sh status
```

---

## Architektura Bezpieczeństwa

```
┌─────────────────────────────────────────────────────────────┐
│ GitHub Actions Runner (w chmurze)                           │
│ - Checkout code z GitHub                                    │
│ - Setup WireGuard (tymczasowy tunel)                        │
│ - SSH przez VPN (10.0.0.2 → 10.0.0.1)                      │
└─────────────────────────────────────────────────────────────┘
               ↓ SSH (tunelowany przez WireGuard)
┌─────────────────────────────────────────────────────────────┐
│ WireGuard Server (VPS)                                      │
│ - Port 51820/UDP - otwarty do publicznej sieci              │
│ - SSH Port 22 - dostępny TYLKO z 10.0.0.0/24 (VPN)        │
│ - Deployment scripts                                        │
└─────────────────────────────────────────────────────────────┘
               ↓ Lokalnie
┌─────────────────────────────────────────────────────────────┐
│ Developer (ty)                                              │
│ - WireGuard Client (10.0.0.2)                              │
│ - SSH do 10.0.0.1                                           │
│ - Manual deployment/debug jeśli potrzeba                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### GitHub Actions nie łączy się z VPN:
- Sprawdzić czy `WIREGUARD_PRIVATEKEY` ma prawidłowe formatowanie
- Sprawdzić czy `WIREGUARD_ENDPOINT` jest publicznym IP VPS
- Sprawdzić czy firewall VPS zezwala na 51820/UDP

### SSH timeout:
- Sprawdzić czy `DEPLOY_HOST` = 10.0.0.1 (nie public IP!)
- Sprawdzić czy SSH listening only na VPN: `sudo netstat -tlnp | grep ssh`
- Sprawdzić SSH config: `sudo less /etc/ssh/sshd_config`

### WireGuard hand-shake fails:
- Sprawdzić klucze - muszą być w parze
- Sprawdzić DNS: `ping -c 3 10.0.0.1`
- Sprawdzić logs: `sudo journalctl -u wg-quick@wg0 -n 20`

