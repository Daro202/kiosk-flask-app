# Firmowy Kiosk - Dashboard Inspiracji i Wyników

## Opis Projektu
Aplikacja webowa Flask działająca jako firmowy kiosk do wyświetlania dashboardów z inspiracjami, wykresami i wynikami. Zaprojektowana do uruchomienia na serwerze korporacyjnym i wyświetlania w trybie kiosk na Raspberry Pi oraz terminalach Wyse.

## Stan Projektu
✅ **Wersja 1.0** - Aplikacja w pełni funkcjonalna i gotowa do użycia

### Data utworzenia
27 października 2025

### Ostatnie zmiany
- [2025-10-27 13:15] Dodano nową stronę /wykres z interaktywnym wykresem Plotly
  - Wczytywanie danych z pliku Export.xlsx (arkusz Eksport/Export)
  - Przekształcanie danych do formy długiej (long format)
  - 3 dropdowny: Typ (Dzienne/Narastające), Kod Maszyny, Brygada (A/B/C)
  - Interaktywny wykres liniowy z markerami
  - API endpoint /api/series dla dynamicznej aktualizacji
  - Biblioteka plotly zainstalowana
- [2025-10-27 10:30] Dodano obsługę plików Excel (.xlsx) dla danych wykresów
  - Aplikacja priorytetowo wczytuje dane z data.xlsx
  - Fallback do data.csv jeśli Excel nie istnieje
  - Biblioteka openpyxl zainstalowana
  - Dokumentacja zaktualizowana
- [2025-10-27] Implementacja kompletnej aplikacji kiosku z wszystkimi funkcjami
- Backend Flask z bazą danych SQLite
- Panel administracyjny chroniony PIN-em (7456)
- Responsywny frontend z Tailwind CSS
- Automatyczna rotacja sekcji co 30 sekund
- Tryb ciemny/jasny
- Animowany leniwiec jako maskotka

## Architektura Projektu

### Technologie
- **Backend**: Python 3.11, Flask, Waitress, Pandas, openpyxl, Plotly
- **Frontend**: HTML5, Tailwind CSS, Chart.js, Plotly.js, Vanilla JavaScript
- **Baza danych**: SQLite3
- **Serwer produkcyjny**: Waitress
- **Format danych**: Excel (.xlsx) lub CSV

### Struktura katalogów
```
.
├── app.py                  # Główna aplikacja Flask
├── config.json             # Konfiguracja (PIN, interwały)
├── data.xlsx               # Dane wykresów Chart.js (Excel) - PRIORYTET
├── data.csv                # Dane wykresów Chart.js (CSV) - FALLBACK
├── Export.xlsx             # Dane dla wykresów Plotly (arkusz: Eksport)
├── kiosk.db                # Baza danych SQLite (tworzona automatycznie)
├── templates/
│   ├── index.html          # Dashboard główny
│   ├── admin.html          # Panel administracyjny
│   └── wykres.html         # Strona z wykresem Plotly
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

### 3. Wykres Średniej Prędkości (/wykres)
- **Interaktywny wykres Plotly**: Wykres liniowy z markerami
- **Dane z pliku Export.xlsx**: Arkusz 'Eksport', 'Export' lub pierwszy dostępny
- **3 dropdowny filtrów**:
  - Typ: Dzienne / Narastające
  - Kod Maszyny: np. 1310, 1329
  - Brygada: A, B, C
- **Dynamiczna aktualizacja**: Wykres aktualizuje się po zmianie filtrów
- **Oś X**: Dzień miesiąca (1-31)
- **Oś Y**: Wartość [m2/wh]
- **Format danych**: Typ, Kod, Brygada, kolumny 1-31 (dni miesiąca)

### 4. API Endpoints
- `GET /` - Strona główna
- `GET /admin` - Panel administracyjny
- `POST /admin` - Logowanie PIN
- `GET /wykres` - Strona z wykresem Plotly
- `POST /api/settings` - Aktualizacja ustawień
- `POST /api/inspiration` - Dodanie inspiracji
- `DELETE /api/inspiration/<id>` - Usunięcie inspiracji
- `POST /api/upload` - Upload pliku
- `GET /api/chart-data` - Dane do wykresów Chart.js
- `GET /api/series?typ=Dzienne&kod=1310&brig=A` - Dane do wykresu Plotly
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
