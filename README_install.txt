═══════════════════════════════════════════════════════════════════════════════
                    FIRMOWY KIOSK - INSTRUKCJA INSTALACJI
═══════════════════════════════════════════════════════════════════════════════

📋 SPIS TREŚCI:
1. Wymagania systemowe
2. Instalacja na serwerze Windows
3. Instalacja na Raspberry Pi / Linux
4. Konfiguracja i uruchomienie
5. Tryb kiosk na Raspberry Pi i Wyse
6. Rozwiązywanie problemów

═══════════════════════════════════════════════════════════════════════════════
1. WYMAGANIA SYSTEMOWE
═══════════════════════════════════════════════════════════════════════════════

✅ Python 3.8 lub nowszy
✅ Minimum 512 MB RAM
✅ 100 MB wolnego miejsca na dysku
✅ Przeglądarka: Chrome, Firefox, Edge (najnowsza wersja)
✅ Rozdzielczość ekranu: Full HD (1920x1080) lub wyższa

═══════════════════════════════════════════════════════════════════════════════
2. INSTALACJA NA SERWERZE WINDOWS
═══════════════════════════════════════════════════════════════════════════════

KROK 1: Instalacja Pythona
---------------------------
a) Pobierz Python z https://www.python.org/downloads/
b) Uruchom instalator
c) ✅ ZAZNACZ "Add Python to PATH"
d) Kliknij "Install Now"
e) Sprawdź instalację w CMD:
   > python --version

KROK 2: Rozpakowanie aplikacji
-------------------------------
a) Rozpakuj archiwum firmowy-kiosk.zip do katalogu, np:
   C:\firmowy-kiosk\

KROK 3: Instalacja zależności
------------------------------
a) Otwórz wiersz poleceń (CMD) jako Administrator
b) Przejdź do katalogu aplikacji:
   > cd C:\firmowy-kiosk
   
c) Zainstaluj wymagane biblioteki:
   > pip install flask waitress pandas openpyxl

KROK 4: Konfiguracja zmiennych środowiskowych (WAŻNE!)
------------------------------------------------------
⚠️ KRYTYCZNE DLA BEZPIECZEŃSTWA! ⚠️

Przed pierwszym uruchomieniem ustaw zmienną SESSION_SECRET:

a) Wygeneruj bezpieczny klucz:
   > python -c "import secrets; print(secrets.token_hex(32))"
   
b) Skopiuj wygenerowany klucz (64 znaki)

c) Ustaw zmienną środowiskową:
   - Windows (CMD):
     > set SESSION_SECRET=<twój_wygenerowany_klucz>
   
   - Windows (PowerShell):
     > $env:SESSION_SECRET="<twój_wygenerowany_klucz>"
   
   - Aby klucz był stały, dodaj do zmiennych systemowych:
     Panel Sterowania → System → Zaawansowane ustawienia systemu 
     → Zmienne środowiskowe → Nowa...

KROK 5: Pierwsze uruchomienie
------------------------------
a) W CMD uruchom aplikację:
   > python app.py
   
b) Aplikacja uruchomi się na porcie 5000
c) Otwórz przeglądarkę i wejdź na:
   http://localhost:5000

KROK 5: Uruchomienie jako usługa Windows (opcjonalnie)
-------------------------------------------------------
Aby aplikacja uruchamiała się automatycznie przy starcie systemu:

a) Zainstaluj NSSM (Non-Sucking Service Manager):
   - Pobierz z: https://nssm.cc/download
   
b) Zainstaluj usługę:
   > nssm install FirmowyKiosk
   
c) W oknie NSSM ustaw:
   - Path: C:\Python\python.exe (ścieżka do Pythona)
   - Startup directory: C:\firmowy-kiosk
   - Arguments: app.py
   
d) Uruchom usługę:
   > nssm start FirmowyKiosk

═══════════════════════════════════════════════════════════════════════════════
3. INSTALACJA NA RASPBERRY PI / LINUX
═══════════════════════════════════════════════════════════════════════════════

KROK 1: Aktualizacja systemu
-----------------------------
$ sudo apt update
$ sudo apt upgrade -y

KROK 2: Instalacja Pythona i pip
---------------------------------
$ sudo apt install python3 python3-pip -y

KROK 3: Instalacja zależności
------------------------------
$ cd /home/pi/firmowy-kiosk
$ pip3 install flask waitress pandas openpyxl

KROK 4: Konfiguracja zmiennych środowiskowych (WAŻNE!)
-------------------------------------------------------
⚠️ KRYTYCZNE DLA BEZPIECZEŃSTWA! ⚠️

a) Wygeneruj bezpieczny klucz sesji:
   $ python3 -c "import secrets; print(secrets.token_hex(32))"

b) Ustaw zmienną środowiskową (tymczasowo):
   $ export SESSION_SECRET="<wygenerowany_klucz>"

c) Aby klucz był stały, dodaj do ~/.bashrc:
   $ echo 'export SESSION_SECRET="<wygenerowany_klucz>"' >> ~/.bashrc
   $ source ~/.bashrc

KROK 5: Uruchomienie aplikacji
-------------------------------
$ python3 app.py

KROK 5: Automatyczne uruchomienie przy starcie (systemd)
---------------------------------------------------------
a) Utwórz plik usługi:
   $ sudo nano /etc/systemd/system/kiosk.service

b) Wklej następującą zawartość:

[Unit]
Description=Firmowy Kiosk
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/firmowy-kiosk
Environment="SESSION_SECRET=<WPISZ_TUTAJ_WYGENEROWANY_KLUCZ>"
ExecStart=/usr/bin/python3 /home/pi/firmowy-kiosk/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

UWAGA: Zamień <WPISZ_TUTAJ_WYGENEROWANY_KLUCZ> na prawdziwy klucz!

c) Włącz i uruchom usługę:
   $ sudo systemctl daemon-reload
   $ sudo systemctl enable kiosk.service
   $ sudo systemctl start kiosk.service

d) Sprawdź status:
   $ sudo systemctl status kiosk.service

═══════════════════════════════════════════════════════════════════════════════
4. KONFIGURACJA I URUCHOMIENIE
═══════════════════════════════════════════════════════════════════════════════

📝 Edycja pliku config.json
----------------------------
Plik config.json zawiera podstawowe ustawienia:

{
  "admin_pin": "7456",              // PIN do panelu admina (zmień!)
  "rotation_interval": 30,          // Czas rotacji sekcji (sekundy)
  "refresh_interval": 300,          // Czas auto-refresh (sekundy)
  "app_name": "Firmowy Kiosk",
  "company": "Stora Enso"
}

🔐 Panel administracyjny
-------------------------
URL: http://adres-serwera:5000/admin
Domyślny PIN: 7456

⚠️ WAŻNE: Zmień PIN przed wdrożeniem produkcyjnym!

📊 Dodawanie danych do wykresów
--------------------------------
Aplikacja obsługuje dwa formaty danych:

OPCJA 1: Plik Excel (.xlsx) - ZALECANE
---------------------------------------
Umieść plik data.xlsx w głównym katalogu aplikacji.
Format arkusza:

| miesiąc  | produkcja | innowacje | efektywność |
|----------|-----------|-----------|-------------|
| Styczeń  | 120       | 5         | 85          |
| Luty     | 135       | 7         | 88          |
| ...      | ...       | ...       | ...         |

⚠️ Aplikacja automatycznie wczyta pierwszy arkusz z pliku Excel.

OPCJA 2: Plik CSV (data.csv)
-----------------------------
Jeśli nie ma pliku Excel, aplikacja użyje pliku CSV:

miesiąc,produkcja,innowacje,efektywność
Styczeń,120,5,85
Luty,135,7,88
...

PRIORYTET: Excel (data.xlsx) > CSV (data.csv) > Dane przykładowe

📸 Dodawanie zdjęć
------------------
1. Skopiuj zdjęcia do folderu: static/images/
2. Zdjęcia zostaną automatycznie dodane do pokazu slajdów
3. Lub użyj panelu admina (Upload zdjęć)

═══════════════════════════════════════════════════════════════════════════════
5. TRYB KIOSK NA RASPBERRY PI I WYSE
═══════════════════════════════════════════════════════════════════════════════

🖥️ Konfiguracja trybu pełnoekranowego (Raspberry Pi)
-----------------------------------------------------

METODA 1: Chromium w trybie kiosk
----------------------------------
a) Zainstaluj Chromium:
   $ sudo apt install chromium-browser unclutter -y

b) Utwórz skrypt startowy:
   $ nano ~/start-kiosk.sh

c) Wklej:
   #!/bin/bash
   
   # Wyłącz wygaszacz ekranu
   xset s off
   xset -dpms
   xset s noblank
   
   # Ukryj kursor
   unclutter -idle 0.5 -root &
   
   # Uruchom Chromium w trybie kiosk
   chromium-browser --noerrdialogs --disable-infobars --kiosk \
     http://localhost:5000

d) Nadaj uprawnienia:
   $ chmod +x ~/start-kiosk.sh

e) Dodaj do autostartu:
   $ nano ~/.config/lxsession/LXDE-pi/autostart
   
   Dodaj linię:
   @/home/pi/start-kiosk.sh

METODA 2: Firefox ESR w trybie kiosk
-------------------------------------
$ firefox --kiosk http://localhost:5000

🖥️ Terminal Wyse
-----------------
1. Zaloguj się do terminala Wyse
2. Otwórz przeglądarkę
3. Wejdź na: http://adres-serwera:5000
4. Naciśnij F11 dla trybu pełnoekranowego

═══════════════════════════════════════════════════════════════════════════════
6. ROZWIĄZYWANIE PROBLEMÓW
═══════════════════════════════════════════════════════════════════════════════

❌ Problem: Aplikacja nie startuje
----------------------------------
Sprawdź czy:
✓ Python jest zainstalowany (python --version)
✓ Wszystkie zależności są zainstalowane (pip list)
✓ Port 5000 nie jest zajęty (netstat -an | findstr :5000)

❌ Problem: Nie mogę się połączyć z kiosku
------------------------------------------
✓ Sprawdź firewall - port 5000 musi być otwarty
✓ Sprawdź adres IP serwera (ipconfig / ifconfig)
✓ Użyj adresu IP zamiast "localhost" na klientach

Windows Firewall:
> netsh advfirewall firewall add rule name="Kiosk" dir=in action=allow protocol=TCP localport=5000

Linux Firewall (ufw):
$ sudo ufw allow 5000/tcp

❌ Problem: Wykresy się nie wyświetlają
---------------------------------------
✓ Sprawdź czy istnieje plik data.xlsx lub data.csv - poprawny format?
✓ Otwórz konsolę przeglądarki (F12) i szukaj błędów
✓ Sprawdź połączenie internetowe (Chart.js z CDN)
✓ Upewnij się, że biblioteka openpyxl jest zainstalowana (pip list | grep openpyxl)

❌ Problem: Zdjęcia nie się ładują
----------------------------------
✓ Sprawdź czy pliki są w folderze static/images/
✓ Dozwolone formaty: PNG, JPG, GIF, SVG, WEBP
✓ Sprawdź uprawnienia do plików (chmod 644)

❌ Problem: Panel admina - błędny PIN
--------------------------------------
✓ Sprawdź plik config.json
✓ Domyślny PIN to: 7456
✓ Upewnij się że brak dodatkowych spacji

═══════════════════════════════════════════════════════════════════════════════
📞 WSPARCIE TECHNICZNE
═══════════════════════════════════════════════════════════════════════════════

W razie problemów:
1. Sprawdź logi aplikacji
2. Otwórz konsolę przeglądarki (F12)
3. Skontaktuj się z działem IT

═══════════════════════════════════════════════════════════════════════════════
✅ CHECKLIST - WDROŻENIE PRODUKCYJNE
═══════════════════════════════════════════════════════════════════════════════

🔴 KRYTYCZNE (przed uruchomieniem):
□ Wygenerowany i ustawiony SESSION_SECRET (zmienna środowiskowa)
□ Zmieniony PIN w config.json (domyślny: 7456)

🟡 WAŻNE (konfiguracja):
□ Dodane własne zdjęcia do /static/images
□ Zaktualizowany plik data.csv z prawdziwymi danymi
□ Aplikacja uruchamia się automatycznie przy starcie
□ Firewall skonfigurowany (port 5000 otwarty)

🟢 FUNKCJONALNE (testy):
□ Tryb kiosk skonfigurowany na Raspberry Pi / Wyse
□ Przetestowano wszystkie sekcje (Wykresy, Inspiracje, Zdjęcia, O nas)
□ Przetestowano panel administracyjny
□ Przetestowano tryb ciemny/jasny
□ Sprawdzono automatyczną rotację sekcji

═══════════════════════════════════════════════════════════════════════════════

Dziękujemy za korzystanie z Firmowego Kiosku!
Wersja: 1.0 | Data: 2025-10-27

═══════════════════════════════════════════════════════════════════════════════
