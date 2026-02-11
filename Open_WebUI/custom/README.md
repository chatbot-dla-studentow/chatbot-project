# Custom Branding - WSB Merito

## Logo
Skopiuj logo WSB Merito do tego katalogu jako `logo.png`

Format logo powinien być:
- PNG z przezroczystym tłem
- Preferowane wymiary: 200x60px lub podobne proporcje
- Nazwa pliku: `logo.png`

## Kolory WSB Merito

Użyte w `custom.css`:
- Główny niebieski: `#0066CC`
- Ciemny niebieski: `#003D99`
- Jasny niebieski (tło): `#E6F2FF`

## Zastosowanie

Pliki są montowane w kontenerze Open WebUI przez docker-compose.yml:
- `custom.css` -> `/app/backend/data/custom.css`
- `logo.png` -> `/app/backend/data/uploads/logo.png`
