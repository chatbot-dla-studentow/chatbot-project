# Customizacja Open WebUI - WSB Merito

## Co zostało dodane?

### 1. Custom CSS (`custom/custom.css`)
Plik ze stylami dostosowanymi do kolorystyki WSB Merito:
- Główny kolor: niebieski #0066CC
- Akcenty: #003D99 (ciemny niebieski)
- Tła: #E6F2FF (jasny niebieski)

Dostosowania:
- Przyciski i linki w kolorach uczelni
- Nawigacja i sidebar w odcieniach niebieskiego
- Wiadomości chatbota z subtelnym niebieskim tłem
- Scrollbary i akcenty w brandingu WSB

### 2. Konfiguracja branding (docker-compose.yml)
Dodano zmienne środowiskowe:
- `WEBUI_NAME`: "ChatBot WSB Merito"
- `DEFAULT_LOCALE`: "pl-PL" (polski interfejs)
- `ENABLE_SIGNUP`: false (wyłączona rejestracja)
- `CUSTOM_CSS`: montowanie custom.css

### 3. Logo WSB Merito

**WAŻNE:** Skopiuj logo WSB Merito do:
```
Open_WebUI/custom/logo.png
```

Format:
- PNG z przezroczystym tłem
- Wymiary: ~200x60px lub podobne proporcje
- Nazwa: dokładnie `logo.png`

## Uruchomienie

1. Skopiuj logo WSB Merito do `custom/logo.png`

2. Restart kontenera:
```bash
cd Open_WebUI
docker compose down
docker compose up -d
```

3. Otwórz http://localhost:3000 (lub http://10.0.0.1:3000 przez VPN)

## Struktura plików

```
Open_WebUI/
├── docker-compose.yml       # Zaktualizowany z brandingiem
├── custom/
│   ├── custom.css          # Style WSB Merito
│   ├── logo.png            # Logo (do dodania)
│   └── README.md           # Instrukcje
└── CUSTOMIZATION.md        # Ten plik
```

## Dalsze dostosowania

Jeśli chcesz zmienić kolory, edytuj `custom/custom.css`:
```css
:root {
  --primary-blue: #0066CC;      /* Główny kolor */
  --wsb-dark-blue: #003D99;      /* Ciemniejszy odcień */
  --wsb-light-blue: #E6F2FF;     /* Jasne tło */
}
```

## Troubleshooting

**Logo się nie wyświetla:**
- Sprawdź czy plik to dokładnie `logo.png` (małe litery)
- Sprawdź uprawnienia pliku
- Restart kontenera: `docker compose restart`

**Kolory się nie stosują:**
- Wyczyść cache przeglądarki (Ctrl+Shift+R)
- Sprawdź logi: `docker logs open-webui`
- Zweryfikuj montowanie: `docker exec open-webui ls -la /app/backend/data/custom/`

## Maintainers
- Adam Siehen (adamsiehen)
- Patryk Boguski (ptrBoguski)
- Miko�aj Sykucki (zybert)
- Oskar Jurgielaniec (oskarju1)
- Pawe� Ponikowski (pponikowski)
