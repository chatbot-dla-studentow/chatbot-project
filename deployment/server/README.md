# VPS Server Configuration Scripts

> ️ **UWAGA:** To są **template/przykładowe** wersje skryptów. Prawdziwe skrypty z konkretnymi danymi produkcyjnymi znajdują się w `private/deployment-vps/server/`

## Dostępne skrypty

### ️ secure.sh
Kompleksowe zabezpieczenie VPS:
- fail2ban (ochrona SSH brute-force)
- UFW firewall
- SSH hardening (zmiana portu, key-only auth)
- Network security
- Automatic security updates

**Lokalizacja prawdziwej wersji:** `private/deployment-vps/server/secure.sh`

### ssh-secure-setup.sh
Szybkie zabezpieczenie SSH:
- Key-only authentication
- Zmiana portu SSH
- Disable root login

**Lokalizacja prawdziwej wersji:** `private/deployment-vps/server/ssh-secure-setup.sh`

### wireguard-setup.sh
Automatyczna instalacja i konfiguracja WireGuard VPN:
- Instalacja WireGuard
- Generowanie kluczy
- Konfiguracja interfejsu wg0
- Routing i firewall

**Lokalizacja prawdziwej wersji:** `private/deployment-vps/server/wireguard-setup.sh`

### geo-blocking.sh
Blokowanie dostępu spoza EU:
- Lista EU countries
- Automatyczne aktualizacje IP list
- Integracja z UFW/iptables

**Lokalizacja prawdziwej wersji:** `private/deployment-vps/server/geo-blocking.sh`

### monitoring-alerts.sh
Monitoring i email alerts:
- CPU, RAM, disk usage monitoring
- Docker containers health
- Security audit reports
- Email alerts przy problemach

**Lokalizacja prawdziwej wersji:** `private/deployment-vps/server/monitoring-alerts.sh`

## Jak używać

### Dla członków zespołu z dostępem do private/:

```bash
# 1. Skopiuj prawdziwe skrypty na VPS
scp -r private/deployment-vps/server/ <USER>@<VPS_IP>:/tmp/deployment

# 2. Na VPS uruchom w kolejności:
ssh <USER>@<VPS_IP>

# Security first
sudo bash /tmp/deployment/secure.sh

# Potem VPN
sudo bash /tmp/deployment/wireguard-setup.sh

# Opcjonalnie pozostałe
sudo bash /tmp/deployment/geo-blocking.sh
sudo bash /tmp/deployment/monitoring-alerts.sh
```

### Dla zewnętrznych contributors:

Jeśli nie masz dostępu do `private/`:
1. Te skrypty są template - musisz dostosować do swojego środowiska
2. Skontaktuj się z team leaderem o dostęp do pełnych wersji
3. Lub użyj instrukcji z [../DEPLOYMENT.md](../../DEPLOYMENT.md) aby stworzyć własne

## Dlaczego skrypty są w private/?

Skrypty zawierają wrażliwe informacje specyficzne dla naszego VPS:
- Konkretne porty aplikacji (8001-8005)
- Email admina dla alertów
- IP subnet VPN (10.0.0.0/24)
- Konfiguracja portów firewall
- Endpoint IP serwera

Umieszczenie ich w publicznym repo mogłoby:
- Ujawnić architekturę naszego systemu
- Ułatwić ataki na konkretne porty
- Ujawnić dane osobowe (email)

## Powiązane dokumenty

- [../docs/README.md](../docs/README.md) - Quick start guide (publiczny)
- [../../DEPLOYMENT.md](../../DEPLOYMENT.md) - Główna dokumentacja deployment
- [../../private/deployment-vps/README.md](../../private/deployment-vps/README.md) - Pełna dokumentacja VPS (wymagany dostęp)

## Nowy członek zespołu?

Aby otrzymać dostęp do pełnych skryptów:
1. Poproś team leadera o dostęp do folderu `private/`
2. Sklonuj publiczne repo: `git clone https://github.com/chatbot-dla-studentow/chatbot-project.git`
3. Skopiuj folder `private/` z OneDrive do lokalnego repo
4. Sprawdź instrukcje w `private/deployment-vps/README.md`

---

**Ostatnia aktualizacja:** 17 lutego 2026
