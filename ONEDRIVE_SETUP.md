# 📦 Instrukcje Przeniesienia Wrażliwych Danych na OneDrive

## ✅ Co zostało zrobione?

### 1. Utworzona struktura `private/`
```
private/
├── README.md              # Dokumentacja folderu private
├── configs/               # Wrażliwe pliki konfiguracyjne
│   └── wg-client.conf    # Oryginalna konfiguracja WireGuard (kopia)
├── docs/                  # Wrażliwa dokumentacja (stare kopie - można usunąć)
│   ├── GITHUB_ACTIONS_SETUP.md
│   └── SSH_ACCESS.md
└── deployment-vps/        # 🆕 GŁÓWNY FOLDER - VPS deployment
    ├── README.md          # Pełna dokumentacja deployment
    ├── wg-client.conf     # Prawdziwa konfiguracja WireGuard
    ├── server/            # Skrypty konfiguracji serwera
    │   ├── wireguard-setup.sh
    │   ├── secure.sh
    │   ├── ssh-secure-setup.sh
    │   ├── geo-blocking.sh
    │   └── monitoring-alerts.sh
    └── docs/              # Dokumentacja VPS
        ├── GITHUB_ACTIONS_SETUP.md
        ├── SSH_ACCESS.md
        └── SSH_SECURE_SETUP.md
```

### 2. Zaktualizowano `.gitignore`
Dodano:
- `private/` - cały folder
- `wg-client.conf` - wszystkie konfiguracje WireGuard
- `**/wg-*.conf` - dowolne pliki WireGuard
- `**/*_private.md` - pliki oznaczone jako prywatne
- `**/*_secret*` - pliki z secretami

### 3. Utworzono template pliki w publicznym repo
- `wg-client.conf.example` - przykład konfiguracji WireGuard (bez prawdziwych kluczy)

### 4. Zastąpiono wrażliwe dane placeholderami

**Pliki zaktualizowane:**
- ✅ `README.md` - IP i hostname serwera
- ✅ `DEPLOYMENT.md` - IP, usernames, emaile członków zespołu
- ✅ `deployment/docs/GITHUB_ACTIONS_SETUP.md` - IP, klucze, credentials
- ✅ `deployment/docs/SSH_ACCESS.md` - IP, usernames, ścieżki
- ✅ `deployment/docs/README.md` - email alertów, IP
- ✅ `docs_agent1/INDEX.md` - IP serwera produkcyjnego

**Placeholdery użyte:**
- `<VPS_PUBLIC_IP>` - zamiast 57.128.212.194
- `<VPS_HOSTNAME>` - zamiast vps-5f2a574b.vps.ovh.net
- `<USER>` - zamiast konkretnych usernames (ubuntu, asiehen)
- `<ADMIN_EMAIL>` - zamiast adam.siehen@outlook.com
- `<USER_1>`, `<USER_2>`, etc. - zamiast loginów członków zespołu
- `<PROJECT_OWNER>` - zamiast konkretnego właściciela

---

## 🚀 Kroki do Wykonania - Przeniesienie na OneDrive

### Krok 1: Przygotuj folder na OneDrive

```powershell
# Przejdź do OneDrive
cd "$env:OneDrive"

# Utwórz strukturę dla projektu
New-Item -ItemType Directory -Force -Path "Praca inżynierska\chatbot-private"
```

### Krok 2: Skopiuj folder private/ na OneDrive

```powershell
# Skopiuj cały folder private/
Copy-Item -Recurse -Force `
    "d:\Inżynierka Informatyka\Praca inżynierska\chatbot-project\private" `
    "$env:OneDrive\Praca inżynierska\chatbot-private"
```

### Krok 3: Weryfikuj przeniesienie

```powershell
# Sprawdź czy wszystkie pliki są na OneDrive
Get-ChildItem -Recurse "$env:OneDrive\Praca inżynierska\chatbot-private"

# Powinno pokazać:
# - README.md
# - configs/wg-client.conf
# - docs/ (można później usunąć)
# - deployment-vps/README.md
# - deployment-vps/wg-client.conf
# - deployment-vps/server/*.sh (5 skryptów)
# - deployment-vps/docs/*.md (3 pliki)
```

### Krok 4: Zweryfikuj synchronizację OneDrive

1. Otwórz OneDrive w przeglądarce: https://onedrive.live.com
2. Przejdź do `Praca inżynierska/chatbot-private`
3. Sprawdź czy wszystkie pliki są zsynchronizowane (zielony checkmark)

### Krok 5: Commituj zmiany do Git (bez private/)

```powershell
cd "d:\Inżynierka Informatyka\Praca inżynierska\chatbot-project"

# Sprawdź status - private/ NIE powinno być widoczne
git status

# Dodaj zmiany (zaktualizowane pliki z placeholderami)
git add .gitignore
git add README.md DEPLOYMENT.md
git add deployment/docs/
git add docs_agent1/INDEX.md
git add wg-client.conf.example
git add private/  # To tylko dodaje README do pokazania struktury

# Commit
git commit -m "security: Move sensitive data to private folder (OneDrive backup)"

# Push do GitHub
git push origin main
```

### Krok 6: Zweryfikuj że wrażliwe dane NIE są w repo

```powershell
# Sprawdź co jest w staging/committed
git ls-files | Select-String "private"  # Nie powinno nic pokazać poza .gitignore

# Sprawdź czy wg-client.conf został usunięty z repo
git ls-files | Select-String "wg-client.conf"  # Powinno pokazać tylko .example

# Sprawdź history czy nie ma wrażliwych danych
git log --all --full-history --oneline -- wg-client.conf
```

---

## 🔄 Synchronizacja (na nowym komputerze lub po zmianach)

### Z OneDrive → Lokalne repo

```powershell
# Na nowym komputerze po sklonowaniu repo
cd chatbot-project

# Skopiuj private/ z OneDrive
Copy-Item -Recurse -Force `
    "$env:OneDrive\Praca inżynierska\chatbot-private\*" `
    ".\private\"

# Sprawdź
Test-Path ".\private\deployment-vps\wg-client.conf"  # Should return True
Test-Path ".\private\deployment-vps\server\secure.sh"  # Should return True
```

### Z lokalnego repo → OneDrive (po edycji)

```powershell
# Po zmianach w private/ lokalnie
robocopy ".\private" `
         "$env:OneDrive\Praca inżynierska\chatbot-private" `
         /MIR /R:3 /W:5

# /MIR - mirror (usuwa pliki które nie istnieją w source)
# /R:3 - retry 3 times
# /W:5 - wait 5 seconds between retries
```

---

## 🔒 Najlepsze Praktyki Bezpieczeństwa

### ✅ DO:

1. **Zawsze sprawdzaj przed commit:**
   ```powershell
   git status
   git diff --staged
   # Upewnij się że NIE ma private/ ani wrażliwych danych
   ```

2. **Regularnie backupuj private/ na OneDrive:**
   - Automatycznie synchronizowane przez OneDrive
   - Ale możesz też ręcznie zrobić kopię na USB/zewnętrzny dysk

3. **Używaj 2FA dla Microsoft/OneDrive account**

4. **Rotuj klucze co 3-6 miesięcy:**
   - WireGuard keys
   - SSH keys
   - API keys

### ❌ NIE:

1. **NIGDY nie commit plików z private/ do Git**
2. **NIGDY nie udostępniaj publicznie linków OneDrive do chatbot-private**
3. **NIGDY nie wysyłaj kluczy prywatnych emailem**
4. **NIGDY nie pushuj bez sprawdzenia `git status`**

---

## 🆘 Co zrobić jeśli przypadkowo push'owałeś wrażliwe dane?

### Natychmiastowe kroki:

1. **STOP - Nie panikuj, ale działaj szybko!**

2. **Usuń z historii Git (BFG Repo-Cleaner - najłatwiejsze):**
   ```powershell
   # Pobierz BFG Repo-Cleaner
   # https://rtyley.github.io/bfg-repo-cleaner/
   
   # Usuń plik z całej historii
   java -jar bfg.jar --delete-files "wg-client.conf" chatbot-project.git
   
   # Wyczyść repo
   cd chatbot-project
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Force push
   git push --force
   ```

3. **Rotuj WSZYSTKIE klucze i credentials:**
   - Wygeneruj nowe klucze WireGuard
   - Wygeneruj nowe klucze SSH
   - Zmień IP serwera (jeśli możliwe) lub wzmocnij firewall
   - Zaktualizuj GitHub Secrets

4. **Sprawdź logi dostępu:**
   ```bash
   # Na VPS
   sudo tail -f /var/log/auth.log
   sudo fail2ban-client status sshd
   ```

---

## 📝 Checklist przed publikacją repo

- [ ] Folder `private/` jest w `.gitignore`
- [ ] `git status` NIE pokazuje plików z `private/`
- [ ] Wszystkie IP zastąpione placeholderami w publicznych plikach
- [ ] Wszystkie usernames/emaile zastąpione placeholderami
- [ ] Klucze WireGuard są w `private/deployment-vps/`, nie w głównym repo
- [ ] Skrypty VPS są w `private/deployment-vps/server/`, nie w `deployment/server/`
- [ ] Template pliki utworzone (*.example, README.md w deployment/server/)
- [ ] OneDrive synchronizacja działa
- [ ] README w `private/` i `private/deployment-vps/` zawierają instrukcje
- [ ] Przetestowano: `git clone` + skopiowanie `private/` = działa

---

## 👥 Dla Nowych Członków Zespołu

**Jeśli jesteś nowym członkiem:**

1. Sklonuj publiczne repo
2. Poproś team leadera o dostęp do OneDrive folder `chatbot-private`
3. Skopiuj zawartość do `private/` w sklonowanym repo
4. Skonfiguruj WireGuard używając `private/deployment-vps/wg-client.conf`
5. Przeczytaj dokumentację:
   - `private/README.md` - ogólny przegląd
   - `private/deployment-vps/README.md` - deployment VPS
6. Nigdy nie commituj zmian z folderu `private/`

**Weryfikacja:**
```powershell
# Sprawdź czy masz wszystko
Test-Path ".\private\deployment-vps\wg-client.conf"  # True
Test-Path ".\private\deployment-vps\server\secure.sh"  # True
Test-Path ".\private\deployment-vps\docs\GITHUB_ACTIONS_SETUP.md"  # True
git status  # nie powinno pokazać private/
```

---

**Data utworzenia:** 16 lutego 2026  
**Ostatnia aktualizacja:** 17 lutego 2026  
**Autor:** GitHub Copilot + Team Lead
