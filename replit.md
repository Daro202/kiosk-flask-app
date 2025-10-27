# Firmowy Kiosk - Dashboard Inspiracji i Wyników

## Opis Projektu
Aplikacja webowa Flask działająca jako firmowy kiosk do wyświetlania dashboardów z inspiracjami, wykresami i wynikami. Zaprojektowana do uruchomienia na serwerze korporacyjnym i wyświetlania w trybie kiosk na Raspberry Pi oraz terminalach Wyse.

## Stan Projektu
✅ **Wersja 1.0** - Aplikacja w pełni funkcjonalna i gotowa do użycia

### Data utworzenia
27 października 2025

### Ostatnie zmiany
- [2025-10-27] Implementacja kompletnej aplikacji kiosku z wszystkimi funkcjami
- Backend Flask z bazą danych SQLite
- Panel administracyjny chroniony PIN-em (7456)
- Responsywny frontend z Tailwind CSS
- Automatyczna rotacja sekcji co 30 sekund
- Tryb ciemny/jasny
- Animowany leniwiec jako maskotka

## Architektura Projektu

### Technologie
- **Backend**: Python 3.11, Flask, Waitress, Pandas
- **Frontend**: HTML5, Tailwind CSS, Chart.js, Vanilla JavaScript
- **Baza danych**: SQLite3
- **Serwer produkcyjny**: Waitress

### Struktura katalogów
```
.
├── app.py                  # Główna aplikacja Flask
├── config.json             # Konfiguracja (PIN, interwały)
├── data.csv                # Dane do wykresów
├── kiosk.db                # Baza danych SQLite (tworzona automatycznie)
├── templates/
│   ├── index.html          # Dashboard główny
│   └── admin.html          # Panel administracyjny
├── static/
│   ├── css/
│   │   └── style.css       # Style CSS
│   ├── js/
│   │   └── main.js         # Logika JavaScript
│   └── images/             # Zdjęcia do pokazu slajdów
└── README_install.txt      # Instrukcje instalacji
```

## Funkcje Aplikacji

### 1. Dashboard Główny (/)
- **Wykresy interaktywne**: Produkcja, innowacje, efektywność (Chart.js)
- **Sekcja inspiracji**: Karty z tytułem, opisem i zdjęciem
- **Pokaz slajdów**: Automatyczna rotacja zdjęć z folderu /static/images
- **Sekcja "O nas"**: Informacje o firmie i zespole
- **Automatyczna rotacja**: Sekcje zmieniają się co 30 sekund
- **Auto-refresh**: Treść odświeża się co 5 minut
- **Tryb ciemny/jasny**: Przełącznik w menu bocznym
- **Animowany leniwiec**: SVG w prawym dolnym rogu

### 2. Panel Administracyjny (/admin)
- **Logowanie PIN**: Domyślny PIN 7456
- **Edycja ustawień**: Nagłówek, stopka, tekst "O nas"
- **Zarządzanie inspiracjami**: Dodawanie, edycja, usuwanie
- **Upload zdjęć**: Wysyłanie obrazów do pokazu slajdów
- **Natychmiastowa aktualizacja**: Zmiany widoczne od razu na dashboardzie

### 3. API Endpoints
- `GET /` - Strona główna
- `GET /admin` - Panel administracyjny
- `POST /admin` - Logowanie PIN
- `POST /api/settings` - Aktualizacja ustawień
- `POST /api/inspiration` - Dodanie inspiracji
- `DELETE /api/inspiration/<id>` - Usunięcie inspiracji
- `POST /api/upload` - Upload pliku
- `GET /api/chart-data` - Dane do wykresów
- `GET /api/slides` - Lista zdjęć
- `GET /api/inspirations` - Lista inspiracji
- `GET /api/content` - Cała treść (dla auto-refresh)

## Konfiguracja

### config.json
```json
{
  "admin_pin": "7456",           // Zmień przed wdrożeniem!
  "rotation_interval": 30,       // Sekundy między rotacją sekcji
  "refresh_interval": 300,       // Sekundy między auto-refresh
  "app_name": "Firmowy Kiosk",
  "company": "Stora Enso"
}
```

### Baza danych SQLite
Tabele tworzone automatycznie przy pierwszym uruchomieniu:
- `settings` - Ustawienia ogólne (nagłówek, stopka, tekst "O nas")
- `inspirations` - Karty inspiracji (tytuł, opis, URL zdjęcia)
- `slides` - Metadane slajdów (nazwa pliku, podpis)

## Uruchomienie

### Lokalnie (Development)
```bash
python app.py
```
Aplikacja dostępna pod: http://localhost:5000

### Produkcja (Replit)
Aplikacja automatycznie uruchamia się na porcie 5000 przez serwer Waitress.

### Tryb Kiosk (Raspberry Pi / Wyse)
Zobacz szczegółowe instrukcje w pliku `README_install.txt`

## Bezpieczeństwo

### Implementowane zabezpieczenia
- ✅ Panel admina chroniony PIN-em
- ✅ Sesje Flask z SECRET_KEY
- ✅ Walidacja plików (tylko obrazy)
- ✅ Secure_filename dla uploadów
- ✅ Wyłączony tryb debug w produkcji
- ✅ Sanityzacja danych wejściowych

### Zalecenia
- ⚠️ **ZMIEŃ PIN** w config.json przed wdrożeniem
- ⚠️ **Ustaw SESSION_SECRET** jako zmienną środowiskową
- ⚠️ Aplikacja działa tylko w sieci LAN
- ⚠️ Dla HTTPS użyj lokalnego certyfikatu IT

## Stylizacja

### Paleta kolorów Stora Enso
- Pomarańcz (primary): `#FF6B35`
- Granatowy (secondary): `#004E89`
- Tło jasne: `#F7F7F7`
- Tło ciemne: `#1A1A1A`

### Czcionki
- Google Fonts: Roboto (300, 400, 500, 700)

## Troubleshooting

### Aplikacja nie startuje
```bash
# Sprawdź czy Python jest zainstalowany
python --version

# Sprawdź czy zależności są zainstalowane
pip list | grep flask
pip list | grep waitress
pip list | grep pandas
```

### Port zajęty
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Baza danych uszkodzona
```bash
# Usuń bazę danych (zostanie odtworzona)
rm kiosk.db
python app.py
```

## Następne kroki (Future Enhancements)
- [ ] HTTPS z lokalnym certyfikatem
- [ ] Harmonogram wyświetlania (różne treści w różnych porach)
- [ ] Statystyki wyświetleń
- [ ] Integracja z API firmowym
- [ ] Wsparcie dla wielu języków

## Preferencje użytkownika
- Wszystkie komentarze w kodzie po polsku
- Styl Stora Enso (pomarańcz, biel, szarość)
- Duże, czytelne czcionki dla trybu kiosk
- Automatyzacja (rotacja, refresh)
- Brak pasków przewijania (Full HD optimized)

## Kontakt
Projekt przygotowany dla wdrożenia w środowisku korporacyjnym Stora Enso.
