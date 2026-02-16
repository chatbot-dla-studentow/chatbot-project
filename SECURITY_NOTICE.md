# 🔒 Security Notice

## Wrażliwe Dane

To repozytorium jest publiczne i **NIE ZAWIERA** wrażliwych danych takich jak:

- ❌ Klucze prywatne (WireGuard, SSH)
- ❌ Adresy IP serwerów produkcyjnych
- ❌ Dane osobowe (emaile, usernames)
- ❌ Credentials i hasła
- ❌ GitHub Secrets wartości

## Gdzie są rzeczywiste wartości?

Wszystkie wrażliwe dane znajdują się w **prywatnym folderze** poza tym repozytorium:

```
private/                     # ⚠️ NIGDY nie commitowany do Git
├── README.md               # Instrukcje użycia
├── configs/
│   └── wg-client.conf     # Prawdziwa konfiguracja WireGuard
└── docs/
    ├── GITHUB_ACTIONS_SETUP.md   # Z prawdziwymi IP i kluczami
    └── SSH_ACCESS.md              # Z prawdziwymi credentials
```

**Backup:** OneDrive (dostęp tylko dla członków zespołu)

## Placeholdery w dokumentacji

W plikach tego repo używamy placeholderów:

| Placeholder | Co oznacza | Przykład prawdziwej wartości |
|------------|-----------|---------------------------|
| `<VPS_PUBLIC_IP>` | Publiczny IP serwera VPS | 57.128.XXX.XXX |
| `<VPS_HOSTNAME>` | Hostname serwera | vps-XXXXX.vps.ovh.net |
| `<USER>` | Nazwa użytkownika SSH | ubuntu, root, etc. |
| `<ADMIN_EMAIL>` | Email kontaktowy admina | admin@example.com |
| `<USER_1>`, `<USER_2>` | Loginy członków zespołu | Konkretne nazwy użytkowników |

## Dla Contributors i Nowych Członków

### Jeśli chcesz uruchomić projekt lokalnie:

1. **Sklonuj to repozytorium:**
   ```bash
   git clone https://github.com/chatbot-dla-studentow/chatbot-project.git
   ```

2. **Otrzymaj dostęp do wrażliwych danych:**
   - Poproś team leadera o dostęp do prywatnego folderu OneDrive
   - Lub otrzymaj zaszyfrowane archiwum z wrażliwymi plikami

3. **Skopiuj private/ do lokalnego repo:**
   ```powershell
   # Windows
   Copy-Item -Recurse "$env:OneDrive\Praca inżynierska\chatbot-private" ".\private"
   ```

4. **Sprawdź czy .gitignore działa:**
   ```bash
   git status  # NIE powinno pokazać folderu private/
   ```

### Jeśli znalazłeś wrażliwe dane w repo:

1. **NIE commituj i NIE push'uj**
2. **Zgłoś natychmiast team leaderowi**
3. **Usuń wrażliwe dane lokalnie**
4. **Poczekaj na instrukcje jak bezpiecznie to naprawić**

## Template Pliki

Przykładowe pliki konfiguracyjne (bez wrażliwych danych):

- ✅ `.env.example` - przykład zmiennych środowiskowych
- ✅ `wg-client.conf.example` - przykład konfiguracji WireGuard
- ✅ `crontab.example` - przykład zadań cron

**Aby użyć:**
```bash
cp .env.example .env
# Następnie edytuj .env i wstaw rzeczywiste wartości
```

## Bezpieczeństwo Repo

### Co jest zabezpieczone:

- ✅ `.gitignore` ignoruje folder `private/`
- ✅ `.gitignore` ignoruje pliki `*.conf` (WireGuard configs)
- ✅ `.gitignore` ignoruje pliki `*_secret*` i `*_private.md`
- ✅ Wszystkie IP i credentials zastąpione placeholderami
- ✅ GitHub Actions używa GitHub Secrets (nie są w repo)

### Commit Guidelines dla Contributors:

```bash
# ZAWSZE przed commit sprawdź:
git status
git diff --staged

# Upewnij się że NIE commituje:
# - Folderu private/
# - Plików *.conf (poza *.example)
# - Prawdziwych IP, kluczy, haseł
```

## Rotacja Kluczy

Dla bezpieczeństwa, zespół rotuje klucze co **3-6 miesięcy**:

- 🔑 Klucze WireGuard
- 🔑 Klucze SSH
- 🔑 API Keys
- 🔑 GitHub Secrets

**Po rotacji:**
- Stare klucze są unieważniane
- Aktualizowane są tylko prywatne pliki (OneDrive)
- Publiczne repo pozostaje bez zmian

## Kontakt

W przypadku pytań dotyczących bezpieczeństwa lub dostępu do wrażliwych danych:

- 📧 Team Lead: (sprawdź `private/README.md` po otrzymaniu dostępu)
- 🔒 Zgłoszenia bezpieczeństwa: poprzez GitHub Issues (tylko dla publicznych problemów)
- ⚠️ Krytyczne problemy: bezpośrednio do team leadera (email w prywatnym folderze)

---

**Ostatnia aktualizacja:** 16 lutego 2026  
**Status:** ✅ Repo bezpieczne dla publikacji
