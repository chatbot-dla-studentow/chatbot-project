# 🚀 Quick Install Guide

⚠️ **UWAGA - v2.0 BREAKING CHANGE:** Stare pliki `agents/*/docker-compose.yml` zostały usunięte. Do wdrożenia używaj `/deployment/setup.sh` lub główny `docker-compose.yml`.

Szybki przewodnik instalacji systemu chatbot na nowej maszynie.

## 📋 Przed rozpoczęciem

**Wymagania:**
- Ubuntu 22.04+ / Debian 11+ (lub WSL2 na Windows)
- 8 GB RAM (16 GB zalecane)
- 30 GB wolnego miejsca
- Uprawnienia sudo

## ⚡ 3-krokowa instalacja

### Krok 1: Sklonuj repozytorium

```bash
git clone https://github.com/yourusername/chatbot-project.git
cd chatbot-project
```

### Krok 2: Zainstaluj zależności

```bash
sudo ./deployment/app/deploy.sh install_dependencies
```

To zainstaluje:
- ✅ Docker Engine
- ✅ Docker Compose V2
- ✅ Git, Python3, curl
- ✅ Inne wymagane pakiety

**UWAGA:** Po instalacji może być konieczne wylogowanie i ponowne zalogowanie, aby zmiany w grupie docker zaczęły działać.

### Krok 3: Wdróż system

```bash
./deployment/app/deploy.sh deploy
```

To automatycznie:
- ✅ Utworzy sieć Docker
- ✅ Uruchomi Qdrant (vector DB)
- ✅ Uruchomi Ollama (LLM)
- ✅ Pobierze model mistral:7b
- ✅ Uruchomi Node-RED
- ✅ Zainicjalizuje bazę wiedzy
- ✅ Uruchomi wszystkich agentów
- ✅ Uruchomi Open WebUI

**Czas wdrożenia:** ~10-15 minut

## ✅ Sprawdzenie instalacji

Po zakończeniu sprawdź status:

```bash
./deployment/app/deploy.sh status
```

Sprawdź dostępność serwisów:

```bash
curl http://localhost:8001/health  # Agent1 - Student Support
curl http://localhost:6333/health  # Qdrant
curl http://localhost:11434/api/tags  # Ollama
```

Otwórz w przeglądarce:
- **Agent1 API:** http://localhost:8001/docs
- **Qdrant Dashboard:** http://localhost:6333/dashboard
- **Node-RED:** http://localhost:1880
- **Open WebUI:** http://localhost:3000

## 🔧 Podstawowe komendy

```bash
# Status wszystkich serwisów
./deployment/app/deploy.sh status

# Uruchom serwisy
./deployment/app/deploy.sh start

# Zatrzymaj serwisy
./deployment/app/deploy.sh stop

# Restart serwisów
./deployment/app/deploy.sh restart

# Logi serwisu
./deployment/app/deploy.sh logs agent1_student

# Odśwież bazę wiedzy
./deployment/app/deploy.sh init-kb
```

## 📝 Konfiguracja (opcjonalna)

Jeśli chcesz zmienić domyślne ustawienia:

```bash
# Skopiuj przykładową konfigurację
cp .env.example .env

# Edytuj konfigurację
nano .env
```

Możesz zmienić:
- Porty serwisów
- Model Ollama
- Limity zasobów
- Klucze API

## 🎯 Test działania

Wyślij testowe zapytanie do Agent1:

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Jakie stypendia są dostępne dla studentów?",
    "conversation_id": "test123"
  }'
```

Odpowiedź powinna zawierać informacje o stypendiach.

## 🩺 Troubleshooting

### Problem: Port zajęty

```bash
# Sprawdź co używa portu
sudo netstat -tulpn | grep :8001

# Zmień port w .env
echo "AGENT1_PORT=8101" >> .env
./deployment/app/deploy.sh restart
```

### Problem: Brak pamięci

```bash
# Sprawdź użycie pamięci
free -h

# Dodaj swap (4GB)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Problem: Docker nie działa

```bash
# Sprawdź status Docker
sudo systemctl status docker

# Uruchom Docker
sudo systemctl start docker

# Dodaj siebie do grupy docker
sudo usermod -aG docker $USER

# Wyloguj się i zaloguj ponownie
```

### Problem: Baza wiedzy pusta

```bash
# Re-inicjalizuj bazę wiedzy
./init-knowledge.sh

# Sprawdź kolekcję
curl http://localhost:6333/collections/agent1_student
```

## 📚 Pełna dokumentacja

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Pełna dokumentacja wdrożenia
- **[README.md](README.md)** - Przegląd projektu
- **[docs_agent1/](docs_agent1/)** - Dokumentacja Agent1

## 🆘 Potrzebujesz pomocy?

```bash
# Pokaż wszystkie komendy
./deployment/app/deploy.sh help

# Sprawdź logi konkretnego serwisu
./deployment/app/deploy.sh logs <nazwa_serwisu>

# Przykłady:
./deployment/app/deploy.sh logs agent1_student
./deployment/app/deploy.sh logs qdrant
./deployment/app/deploy.sh logs ollama
```

## 🧹 Dezinstalacja

Jeśli chcesz usunąć wszystko (UWAGA: usunie dane!):

```bash
./deployment/app/deploy.sh cleanup
```

---

**Gotowe!** System chatbot jest teraz uruchomiony i gotowy do użycia. 🎉


## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
