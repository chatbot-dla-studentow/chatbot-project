# Instrukcje Konfiguracji: GitHub Actions + WireGuard Deployment

## 1. Setup WireGuard na VPS

### Krok 1: Uruchomić setup skrypt

```bash
ssh ubuntu@51.68.151.45
sudo bash -c "$(curl -s https://raw.githubusercontent.com/chatbot-dla-studentow/chatbot-project/main/deployment/server/wireguard-setup.sh)"
```

Lub lokalnie z repo:
```bash
scp deployment/server/wireguard-setup.sh ubuntu@51.68.151.45:~/
ssh ubuntu@51.68.151.45 'sudo bash ~/wireguard-setup.sh'
```

### Krok 2: Zapisać wygenerowane klucze z outputu

Skrypt wygeneruje:
```
Private Key: [ZAPISZ TO]
Public Key: [ZAPISZ TO]
```

**⚠️ WAŻNE:** Zapisz te klucze - będą potrzebne dla GitHub Actions!

### Krok 3: Sprawdzić status WireGuard

```bash
ssh ubuntu@51.68.151.45
sudo wg show
```

Powinno pokazać:
```
interface: wg0
  public key: [klucz serwera]
  listen port: 51820

peer: di0wRfrPoUGMBY46n5f8/1VGsZ9bhAPSab3tmiLTzXc=
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
ssh ubuntu@51.68.151.45
echo "[WKLEJ_PUBLIC_KEY_Z_GÓRY]" >> ~/.ssh/authorized_keys
```

---

## 3. Konfiguracja GitHub Secrets

W ustawieniach repozytorium GitHub (Settings → Secrets and variables → Actions):

### Dodaj te Secrets:

| Secret Name | Wartość |
|-------------|---------|
| `SSH_PRIVATE_KEY` | Zawartość `github_deploy` (cały plik, include BEGIN/END) |
| `DEPLOY_USER` | `ubuntu` |
| `DEPLOY_HOST` | `10.0.0.1` (VPN IP serwera) |
| `WIREGUARD_PRIVATEKEY` | Private Key z `wireguard-setup.sh` output |
| `WIREGUARD_PUBLICKEY` | Public Key z serwera **wg0.conf** |
| `WIREGUARD_ENDPOINT` | `57.128.212.194:51820` |

### Gdzie znaleźć wartości:

**WIREGUARD_PUBLICKEY** - na serwerze:
```bash
ssh ubuntu@51.68.151.45
cat /etc/wireguard/publickey
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
AllowUsers ubuntu@10.0.0.0/24

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
ssh -i ~/.ssh/github_deploy ubuntu@10.0.0.1

# Check WireGuard status
sudo wg show

# Check SSH logs
sudo tail -f /var/log/auth.log

# Check UFW firewall
sudo ufw status
```

---

## Maintainers

- **Adam Siehen** - GitHub Actions workflow, deployment automation, VPN integration
- **Patryk Boguski** - VPS security, WireGuard setup, deployment infrastructure

---

## 6. Local Development - Zamiast Actions

Jeśli chcesz deployować ręcznie przez VPN:

```powershell
# Uruchom WireGuard (Windows - np. WireGuard Client)
# - Załaduj wg-client.conf
# - Connect do VPN

# Potem SSH będzie dostępny na 10.0.0.1
ssh -i $env:USERPROFILE\.ssh\github_deploy ubuntu@10.0.0.1

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

