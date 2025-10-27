# -*- coding: utf-8 -*-
"""
Firmowy Kiosk - Aplikacja Flask do wyświetlania dashboardów
Autor: Replit Agent
Data: 2025-10-27
"""

import os
import json
import sqlite3
import secrets
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from waitress import serve

# Konfiguracja aplikacji Flask
app = Flask(__name__)

# Bezpieczny sekret sesji - WYMAGANE dla produkcji
if 'SESSION_SECRET' in os.environ:
    app.secret_key = os.environ['SESSION_SECRET']
else:
    # Generuj bezpieczny losowy klucz dla developmentu
    # W produkcji ZAWSZE ustaw zmienną środowiskową SESSION_SECRET
    app.secret_key = secrets.token_hex(32)
    print("⚠️  UWAGA: Używany jest tymczasowy klucz sesji!")
    print("⚠️  W produkcji ustaw zmienną środowiskową SESSION_SECRET")
    print("⚠️  Przykład: export SESSION_SECRET=$(python -c 'import secrets; print(secrets.token_hex(32))')")
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB upload

# Dozwolone rozszerzenia plików
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp'}

# ==================== BAZA DANYCH ====================

def init_db():
    """Inicjalizacja bazy danych SQLite"""
    conn = sqlite3.connect('kiosk.db')
    c = conn.cursor()
    
    # Tabela z ustawieniami ogólnymi
    c.execute('''CREATE TABLE IF NOT EXISTS settings
                 (key TEXT PRIMARY KEY, value TEXT)''')
    
    # Tabela z inspiracjami
    c.execute('''CREATE TABLE IF NOT EXISTS inspirations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  description TEXT,
                  image_url TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Tabela ze zdjęciami (dla pokazu slajdów)
    c.execute('''CREATE TABLE IF NOT EXISTS slides
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  filename TEXT,
                  caption TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Wstaw domyślne ustawienia jeśli nie istnieją
    c.execute("SELECT COUNT(*) FROM settings")
    if c.fetchone()[0] == 0:
        default_settings = [
            ('header_title', 'Dashboard Inspiracji i Wyników'),
            ('footer_note', 'Stora Enso - Innowacje dla Przyszłości'),
            ('about_text', 'Nasz zespół stale poszukuje nowych rozwiązań i inspiracji.')
        ]
        c.executemany("INSERT INTO settings (key, value) VALUES (?, ?)", default_settings)
        
        # Dodaj przykładowe inspiracje
        example_inspirations = [
            ('Zielona Energia', 'Inwestujemy w odnawialne źródła energii, aby zmniejszyć nasz ślad węglowy.', '/static/images/placeholder1.jpg'),
            ('Cyfrowa Transformacja', 'Automatyzacja procesów i wykorzystanie AI w produkcji.', '/static/images/placeholder2.jpg'),
            ('Ekologiczne Opakowania', 'Rozwój biodegradowalnych materiałów opakowaniowych.', '/static/images/placeholder3.jpg')
        ]
        c.executemany("INSERT INTO inspirations (title, description, image_url) VALUES (?, ?, ?)", 
                     example_inspirations)
    
    conn.commit()
    conn.close()

def get_setting(key):
    """Pobierz ustawienie z bazy danych"""
    conn = sqlite3.connect('kiosk.db')
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def update_setting(key, value):
    """Aktualizuj ustawienie w bazie danych"""
    conn = sqlite3.connect('kiosk.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_inspirations():
    """Pobierz wszystkie inspiracje"""
    conn = sqlite3.connect('kiosk.db')
    c = conn.cursor()
    c.execute("SELECT id, title, description, image_url FROM inspirations ORDER BY created_at DESC")
    inspirations = [{'id': row[0], 'title': row[1], 'description': row[2], 'image_url': row[3]} 
                   for row in c.fetchall()]
    conn.close()
    return inspirations

# ==================== POMOCNICZE FUNKCJE ====================

def allowed_file(filename):
    """Sprawdź czy plik ma dozwolone rozszerzenie"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    """Wczytaj konfigurację z pliku config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Zwróć domyślną konfigurację jeśli plik nie istnieje
        return {'admin_pin': '7456', 'rotation_interval': 30, 'refresh_interval': 300}

def get_chart_data():
    """Wczytaj dane z pliku Excel (.xlsx) lub CSV dla wykresów"""
    try:
        # Najpierw spróbuj wczytać plik Excel
        if os.path.exists('data.xlsx'):
            df = pd.read_excel('data.xlsx', engine='openpyxl')
            return df.to_dict('records')
        # Jeśli nie ma Excela, spróbuj CSV
        elif os.path.exists('data.csv'):
            df = pd.read_csv('data.csv')
            return df.to_dict('records')
        else:
            raise FileNotFoundError
    except FileNotFoundError:
        # Zwróć przykładowe dane jeśli żaden plik nie istnieje
        return [
            {'miesiąc': 'Styczeń', 'produkcja': 120, 'innowacje': 5, 'efektywność': 85},
            {'miesiąc': 'Luty', 'produkcja': 135, 'innowacje': 7, 'efektywność': 88},
            {'miesiąc': 'Marzec', 'produkcja': 150, 'innowacje': 6, 'efektywność': 90},
            {'miesiąc': 'Kwiecień', 'produkcja': 145, 'innowacje': 8, 'efektywność': 87},
            {'miesiąc': 'Maj', 'produkcja': 160, 'innowacje': 10, 'efektywność': 92}
        ]

def get_slide_images():
    """Pobierz listę zdjęć do pokazu slajdów"""
    images_path = os.path.join(app.config['UPLOAD_FOLDER'])
    if not os.path.exists(images_path):
        return []
    
    images = []
    for filename in os.listdir(images_path):
        if allowed_file(filename):
            images.append({
                'url': f'/static/images/{filename}',
                'name': filename
            })
    return images

def load_long():
    """
    Wczytaj dane z pliku Export.xlsx i przekształć do formy długiej (long format)
    Format: Typ, Kod, Brygada, Dzien (1-31), Wartosc
    """
    try:
        # Spróbuj wczytać arkusz 'Eksport', 'Export' lub pierwszy dostępny
        try:
            df = pd.read_excel('Export.xlsx', sheet_name='Eksport', engine='openpyxl')
        except ValueError:
            try:
                df = pd.read_excel('Export.xlsx', sheet_name='Export', engine='openpyxl')
            except ValueError:
                # Jeśli żaden nie istnieje, wczytaj pierwszy arkusz
                df = pd.read_excel('Export.xlsx', sheet_name=0, engine='openpyxl')
        
        # Standaryzuj nazwy pierwszych trzech kolumn
        df.columns = ['Typ', 'Kod', 'Brygada'] + list(df.columns[3:])
        
        # Przekształć nagłówki dni (kolumny 4+) na int
        day_cols = []
        for col in df.columns[3:]:
            try:
                day_cols.append(int(col))
            except (ValueError, TypeError):
                # Jeśli nie można przekonwertować na int, pomiń kolumnę
                pass
        
        # Wybierz tylko kolumny podstawowe + dni jako int
        valid_cols = ['Typ', 'Kod', 'Brygada'] + [c for c in df.columns[3:] if c in day_cols or str(c).isdigit()]
        df = df[valid_cols]
        
        # Zmień nazwy kolumn dni na int
        col_rename = {}
        for col in df.columns[3:]:
            try:
                col_rename[col] = int(col)
            except (ValueError, TypeError):
                pass
        df.rename(columns=col_rename, inplace=True)
        
        # Przekształć do formy długiej (melt)
        id_vars = ['Typ', 'Kod', 'Brygada']
        value_vars = [col for col in df.columns if isinstance(col, int) and 1 <= col <= 31]
        
        df_long = pd.melt(
            df,
            id_vars=id_vars,
            value_vars=value_vars,
            var_name='Dzien',
            value_name='Wartosc'
        )
        
        # Usuń wiersze z NaN w kolumnie Wartosc
        df_long = df_long.dropna(subset=['Wartosc'])
        
        # Konwertuj typy
        df_long['Typ'] = df_long['Typ'].astype(str)
        df_long['Kod'] = df_long['Kod'].astype(str)
        df_long['Brygada'] = df_long['Brygada'].astype(str)
        df_long['Dzien'] = df_long['Dzien'].astype(int)
        df_long['Wartosc'] = df_long['Wartosc'].astype(float)
        
        return df_long
    
    except FileNotFoundError:
        # Jeśli plik nie istnieje, zwróć pusty DataFrame
        return pd.DataFrame(columns=['Typ', 'Kod', 'Brygada', 'Dzien', 'Wartosc'])
    except Exception as e:
        print(f"Błąd wczytywania danych z Export.xlsx: {e}")
        return pd.DataFrame(columns=['Typ', 'Kod', 'Brygada', 'Dzien', 'Wartosc'])

# ==================== TRASY (ROUTES) ====================

@app.route('/')
def index():
    """Strona główna - Dashboard"""
    header_title = get_setting('header_title')
    footer_note = get_setting('footer_note')
    inspirations = get_inspirations()
    
    return render_template('index.html',
                         header_title=header_title,
                         footer_note=footer_note,
                         inspirations=inspirations)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Panel administracyjny"""
    config = load_config()
    
    if request.method == 'POST':
        # Sprawdź PIN
        pin = request.form.get('pin')
        if pin == config['admin_pin']:
            session['authenticated'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', error='Nieprawidłowy PIN!')
    
    # Sprawdź czy użytkownik jest zalogowany
    if not session.get('authenticated'):
        return render_template('admin.html', authenticated=False)
    
    # Użytkownik zalogowany - pokaż panel
    header_title = get_setting('header_title')
    footer_note = get_setting('footer_note')
    about_text = get_setting('about_text')
    inspirations = get_inspirations()
    
    return render_template('admin.html',
                         authenticated=True,
                         header_title=header_title,
                         footer_note=footer_note,
                         about_text=about_text,
                         inspirations=inspirations)

@app.route('/admin/logout')
def admin_logout():
    """Wylogowanie z panelu admina"""
    session.pop('authenticated', None)
    return redirect(url_for('admin'))

# ==================== API ENDPOINTS ====================

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Aktualizuj ustawienia aplikacji"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Brak autoryzacji'}), 401
    
    data = request.json
    if data and 'header_title' in data:
        update_setting('header_title', data['header_title'])
    if data and 'footer_note' in data:
        update_setting('footer_note', data['footer_note'])
    if data and 'about_text' in data:
        update_setting('about_text', data['about_text'])
    
    return jsonify({'success': True})

@app.route('/api/inspiration', methods=['POST'])
def add_inspiration():
    """Dodaj nową inspirację"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Brak autoryzacji'}), 401
    
    data = request.json or {}
    conn = sqlite3.connect('kiosk.db')
    c = conn.cursor()
    c.execute("INSERT INTO inspirations (title, description, image_url) VALUES (?, ?, ?)",
             (data.get('title', ''), data.get('description', ''), data.get('image_url', '')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/inspiration/<int:inspiration_id>', methods=['DELETE'])
def delete_inspiration(inspiration_id):
    """Usuń inspirację"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Brak autoryzacji'}), 401
    
    conn = sqlite3.connect('kiosk.db')
    c = conn.cursor()
    c.execute("DELETE FROM inspirations WHERE id=?", (inspiration_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload pliku zdjęcia"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Brak autoryzacji'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'Brak pliku'}), 400
    
    file = request.files['file']
    if file.filename == '' or file.filename is None:
        return jsonify({'error': 'Nie wybrano pliku'}), 400
    
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Dodaj timestamp do nazwy aby uniknąć konfliktów
        name, ext = os.path.splitext(filename)
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'success': True,
            'url': f'/static/images/{filename}',
            'filename': filename
        })
    
    return jsonify({'error': 'Niedozwolony typ pliku'}), 400

@app.route('/api/chart-data')
def chart_data():
    """Zwróć dane do wykresów"""
    data = get_chart_data()
    return jsonify(data)

@app.route('/api/slides')
def slides():
    """Zwróć listę zdjęć do pokazu slajdów"""
    images = get_slide_images()
    return jsonify(images)

@app.route('/api/inspirations')
def api_inspirations():
    """Zwróć listę inspiracji"""
    inspirations = get_inspirations()
    return jsonify(inspirations)

@app.route('/api/content')
def get_content():
    """Zwróć całą treść dla strony głównej (dla auto-refresh)"""
    return jsonify({
        'header_title': get_setting('header_title'),
        'footer_note': get_setting('footer_note'),
        'about_text': get_setting('about_text'),
        'inspirations': get_inspirations(),
        'chart_data': get_chart_data(),
        'slides': get_slide_images()
    })

# ==================== WYKRESY PLOTLY ====================

@app.route('/wykres')
def wykres():
    """Strona z interaktywnym wykresem Plotly"""
    import plotly.graph_objects as go
    from plotly.offline import plot
    
    df_long = load_long()
    
    # Pobierz unikalne wartości dla dropdownów
    if not df_long.empty:
        typy = sorted(df_long['Typ'].unique().tolist())
        kody = sorted(df_long['Kod'].unique().tolist(), key=lambda x: int(x) if x.isdigit() else x)
        brygady = sorted(df_long['Brygada'].unique().tolist())
        
        # Domyślne wartości
        default_typ = typy[0] if typy else 'Dzienne'
        default_kod = kody[0] if kody else ''
        default_brygada = 'A' if 'A' in brygady else (brygady[0] if brygady else 'A')
        
        # Wygeneruj początkowy wykres
        mask = (df_long['Typ'] == default_typ) & (df_long['Kod'] == default_kod) & (df_long['Brygada'] == default_brygada)
        filtered = df_long[mask].copy().sort_values('Dzien')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered['Dzien'].tolist(),
            y=filtered['Wartosc'].tolist(),
            mode='lines+markers',
            name=f'{default_typ} - {default_kod} - {default_brygada}',
            line=dict(color='#FF6B35', width=3),
            marker=dict(color='#FF6B35', size=8)
        ))
        
        fig.update_layout(
            title=f'Średnia prędkość – {default_typ}, Kod {default_kod}, Brygada {default_brygada}',
            xaxis_title='Dzień miesiąca',
            yaxis_title='Wartość [m2/wh]',
            hovermode='closest',
            plot_bgcolor='#f9fafb',
            paper_bgcolor='white'
        )
        
        # Generuj HTML wykresu z w pełni osadzoną biblioteką Plotly (inline)
        plot_html = plot(fig, output_type='div', include_plotlyjs=True)
        
    else:
        typy = ['Dzienne', 'Narastające']
        kody = []
        brygady = ['A', 'B', 'C']
        default_typ = 'Dzienne'
        default_kod = ''
        default_brygada = 'A'
        plot_html = '<div class="text-center text-gray-600 p-8">Brak danych - proszę dodać plik Export.xlsx</div>'
    
    return render_template('wykres.html',
                         typy=typy,
                         kody=kody,
                         brygady=brygady,
                         default_typ=default_typ,
                         default_kod=default_kod,
                         default_brygada=default_brygada,
                         plot_html=plot_html)

@app.route('/api/series')
def api_series():
    """Zwróć dane serii dla wykresu w formacie JSON"""
    # Pobierz parametry z query string
    typ = request.args.get('typ', 'Dzienne')
    kod = request.args.get('kod', '')
    brig = request.args.get('brig', 'A')
    
    df_long = load_long()
    
    if df_long.empty:
        return jsonify({
            'x': [],
            'y': [],
            'typ': typ,
            'kod': kod,
            'brig': brig
        })
    
    # Filtruj dane
    mask = (df_long['Typ'] == typ) & (df_long['Kod'] == kod) & (df_long['Brygada'] == brig)
    filtered = df_long[mask].copy()
    
    # Sortuj po dniu
    filtered = filtered.sort_values('Dzien')
    
    # Przygotuj dane do zwrócenia
    x = filtered['Dzien'].tolist()
    y = filtered['Wartosc'].tolist()
    
    return jsonify({
        'x': x,
        'y': y,
        'typ': typ,
        'kod': kod,
        'brig': brig
    })

# ==================== URUCHOMIENIE APLIKACJI ====================

if __name__ == '__main__':
    # Inicjalizuj bazę danych
    init_db()
    
    # Utwórz folder na zdjęcia jeśli nie istnieje
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Uruchom serwer produkcyjny Waitress
    print("=" * 60)
    print("🚀 Firmowy Kiosk - Aplikacja uruchomiona!")
    print("=" * 60)
    print("📍 Adres lokalny: http://0.0.0.0:5000")
    print("🔐 Panel admina: http://0.0.0.0:5000/admin")
    print("🔑 PIN administracyjny: 7456")
    print("=" * 60)
    
    # Bind do 0.0.0.0:5000 dla Replit
    serve(app, host='0.0.0.0', port=5000, threads=4)
