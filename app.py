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
    """Wczytaj dane z pliku Export.xlsx i przygotuj dla wykresów Chart.js"""
    try:
        # Wczytaj dane z Export.xlsx
        df_long = load_long()
        
        if df_long.empty:
            # Jeśli Export.xlsx nie istnieje, użyj starych danych
            if os.path.exists('data.xlsx'):
                df = pd.read_excel('data.xlsx', engine='openpyxl')
                return df.to_dict('records')
            elif os.path.exists('data.csv'):
                df = pd.read_csv('data.csv')
                return df.to_dict('records')
            else:
                raise FileNotFoundError
        
        # Agreguj dane dzienne dla wszystkich maszyn i brygad
        # Zsumuj wartości dzienne dla każdego dnia (1-31)
        df_dzienne = df_long[df_long['Typ'] == 'Dzienne'].copy()
        
        # Grupuj po dniu i sumuj wartości
        dzienne_suma = df_dzienne.groupby('Dzien')['Wartosc'].sum().reset_index()
        
        # Podziel dni na tygodnie (4 tygodnie w miesiącu)
        tygodnie = ['Tydzień 1', 'Tydzień 2', 'Tydzień 3', 'Tydzień 4']
        tygodnie_data = []
        
        for i in range(4):
            start_day = i * 7 + 1
            end_day = min((i + 1) * 7, 31)
            
            # Filtruj dane dla tego tygodnia
            mask = (dzienne_suma['Dzien'] >= start_day) & (dzienne_suma['Dzien'] <= end_day)
            tydzien_suma = dzienne_suma[mask]['Wartosc'].sum()
            
            # Przykładowe wartości innowacji i efektywności
            tygodnie_data.append({
                'miesiąc': tygodnie[i],
                'produkcja': int(tydzien_suma) if tydzien_suma > 0 else 0,
                'innowacje': 5 + i * 2,  # Przykładowe wartości
                'efektywność': 85 + i * 2  # Przykładowe wartości
            })
        
        return tygodnie_data
        
    except Exception as e:
        print(f"Błąd wczytywania danych wykresu: {e}")
        # Zwróć przykładowe dane jeśli coś pójdzie nie tak
        return [
            {'miesiąc': 'Styczeń', 'produkcja': 120, 'innowacje': 5, 'efektywność': 85},
            {'miesiąc': 'Luty', 'produkcja': 135, 'innowacje': 7, 'efektywność': 88},
            {'miesiąc': 'Marzec', 'produkcja': 150, 'innowacje': 6, 'efektywność': 90},
            {'miesiąc': 'Kwiecień', 'produkcja': 145, 'innowacje': 8, 'efektywność': 87}
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
    Format: Typ, Kod, Nazwa, Brygada, Dzien (1-31), Wartosc
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
        
        # Sprawdź czy istnieje kolumna Nazwa
        has_nazwa = 'Nazwa' in df.columns or len(df.columns) >= 4
        
        if has_nazwa and len(df.columns) >= 4:
            # Standaryzuj nazwy pierwszych czterech kolumn
            df.columns = ['Typ', 'Kod', 'Nazwa', 'Brygada'] + list(df.columns[4:])
            first_day_col = 4
            id_vars = ['Typ', 'Kod', 'Nazwa', 'Brygada']
        else:
            # Stary format bez nazwy
            df.columns = ['Typ', 'Kod', 'Brygada'] + list(df.columns[3:])
            df['Nazwa'] = ''  # Dodaj pustą kolumnę Nazwa
            first_day_col = 3
            id_vars = ['Typ', 'Kod', 'Nazwa', 'Brygada']
        
        # Przekształć nagłówki dni (kolumny od first_day_col+) na int
        day_cols = []
        for col in df.columns[first_day_col:]:
            try:
                day_cols.append(int(col))
            except (ValueError, TypeError):
                # Jeśli nie można przekonwertować na int, pomiń kolumnę
                pass
        
        # Wybierz tylko kolumny podstawowe + dni jako int
        valid_cols = id_vars + [c for c in df.columns[first_day_col:] if c in day_cols or str(c).isdigit()]
        df = df[valid_cols]
        
        # Zmień nazwy kolumn dni na int
        col_rename = {}
        for col in df.columns[first_day_col:]:
            try:
                col_rename[col] = int(col)
            except (ValueError, TypeError):
                pass
        df.rename(columns=col_rename, inplace=True)
        
        # Przekształć do formy długiej (melt)
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
        df_long['Nazwa'] = df_long['Nazwa'].astype(str)
        df_long['Brygada'] = df_long['Brygada'].astype(str)
        df_long['Dzien'] = df_long['Dzien'].astype(int)
        df_long['Wartosc'] = df_long['Wartosc'].astype(float)
        
        return df_long
    
    except FileNotFoundError:
        # Jeśli plik nie istnieje, zwróć pusty DataFrame
        return pd.DataFrame(columns=['Typ', 'Kod', 'Nazwa', 'Brygada', 'Dzien', 'Wartosc'])
    except Exception as e:
        print(f"Błąd wczytywania danych z Export.xlsx: {e}")
        return pd.DataFrame(columns=['Typ', 'Kod', 'Nazwa', 'Brygada', 'Dzien', 'Wartosc'])

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
    """Strona z interaktywnym wykresem Plotly - wykres kombinowany (słupki + linie)"""
    import plotly.graph_objects as go
    from plotly.offline import plot
    
    df_long = load_long()
    
    # Pobierz unikalne wartości dla dropdown maszyn
    if not df_long.empty:
        # Utwórz listę maszyn (kod + nazwa)
        maszyny_df = df_long[['Kod', 'Nazwa']].drop_duplicates().sort_values('Kod')
        maszyny = []
        for _, row in maszyny_df.iterrows():
            kod = row['Kod']
            nazwa = row['Nazwa']
            if nazwa and nazwa.strip():
                maszyny.append({'kod': kod, 'label': f"{kod} {nazwa}"})
            else:
                maszyny.append({'kod': kod, 'label': kod})
        
        # Domyślna maszyna
        default_kod = maszyny[0]['kod'] if maszyny else ''
        default_nazwa = maszyny[0]['label'] if maszyny else ''
        
        # Wygeneruj początkowy wykres kombinowany
        fig = go.Figure()
        
        # Kolory dla brygad (słupki)
        kolory_slupki = {'A': '#0ea5e9', 'B': '#FF6B35', 'C': '#6b7280'}  # niebieski, pomarańczowy, szary
        kolory_linie = {'A': '#0284c7', 'B': '#f97316', 'C': '#4b5563'}  # ciemniejsze odcienie
        
        # Dodaj słupki dla wartości dziennych (brygady A, B, C) - oś Y lewa
        for brygada in ['A', 'B', 'C']:
            mask = (df_long['Typ'] == 'Dzienne') & (df_long['Kod'] == default_kod) & (df_long['Brygada'] == brygada)
            filtered = df_long[mask].copy().sort_values('Dzien')
            
            if not filtered.empty:
                fig.add_trace(go.Bar(
                    x=filtered['Dzien'].tolist(),
                    y=filtered['Wartosc'].tolist(),
                    name=brygada,
                    marker_color=kolory_slupki.get(brygada, '#999999'),
                    text=filtered['Wartosc'].tolist(),
                    textposition='outside',
                    texttemplate='%{text:.0f}',
                    yaxis='y'
                ))
        
        # Dodaj linie dla wartości narastających (brygady A, B, C) - oś Y prawa
        for brygada in ['A', 'B', 'C']:
            mask = (df_long['Typ'] == 'Narastające') & (df_long['Kod'] == default_kod) & (df_long['Brygada'] == brygada)
            filtered = df_long[mask].copy().sort_values('Dzien')
            
            if not filtered.empty:
                fig.add_trace(go.Scatter(
                    x=filtered['Dzien'].tolist(),
                    y=filtered['Wartosc'].tolist(),
                    mode='lines+markers',
                    name=f'Narastająco {brygada}',
                    line=dict(color=kolory_linie.get(brygada, '#666666'), width=2),
                    marker=dict(color=kolory_linie.get(brygada, '#666666'), size=6),
                    yaxis='y2'
                ))
        
        # Dodaj linie Cel 0 i Cel 100 (opcjonalnie)
        # Na razie pominięte - można dodać później jeśli potrzebne
        
        fig.update_layout(
            title=default_nazwa,
            xaxis_title='',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            barmode='group',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#e5e7eb',
                dtick=1
            ),
            yaxis=dict(
                title='',
                showgrid=True,
                gridcolor='#e5e7eb',
                side='left'
            ),
            yaxis2=dict(
                title='',
                showgrid=False,
                overlaying='y',
                side='right'
            )
        )
        
        # Generuj HTML wykresu z w pełni osadzoną biblioteką Plotly (inline)
        plot_html = plot(fig, output_type='div', include_plotlyjs=True)
        
    else:
        maszyny = []
        default_kod = ''
        default_nazwa = ''
        plot_html = '<div class="text-center text-gray-600 p-8">Brak danych - proszę dodać plik Export.xlsx</div>'
    
    return render_template('wykres.html',
                         maszyny=maszyny,
                         default_kod=default_kod,
                         default_nazwa=default_nazwa,
                         plot_html=plot_html)

@app.route('/api/series')
def api_series():
    """Zwróć dane wszystkich serii dla wykresu kombinowanego w formacie JSON"""
    # Pobierz kod maszyny z query string
    kod = request.args.get('kod', '')
    
    df_long = load_long()
    
    if df_long.empty or not kod:
        return jsonify({
            'series': [],
            'kod': kod,
            'nazwa': ''
        })
    
    # Pobierz nazwę maszyny
    maszyna_df = df_long[df_long['Kod'] == kod][['Nazwa']].drop_duplicates()
    nazwa = maszyna_df.iloc[0]['Nazwa'] if not maszyna_df.empty else ''
    
    # Przygotuj dane dla wszystkich serii
    series_data = []
    
    # Kolory dla brygad
    kolory_slupki = {'A': '#0ea5e9', 'B': '#FF6B35', 'C': '#6b7280'}
    kolory_linie = {'A': '#0284c7', 'B': '#f97316', 'C': '#4b5563'}
    
    # Słupki dla wartości dziennych (brygady A, B, C) - oś Y lewa
    for brygada in ['A', 'B', 'C']:
        mask = (df_long['Typ'] == 'Dzienne') & (df_long['Kod'] == kod) & (df_long['Brygada'] == brygada)
        filtered = df_long[mask].copy().sort_values('Dzien')
        
        if not filtered.empty:
            series_data.append({
                'type': 'bar',
                'name': brygada,
                'x': filtered['Dzien'].tolist(),
                'y': filtered['Wartosc'].tolist(),
                'color': kolory_slupki.get(brygada, '#999999'),
                'yaxis': 'y'
            })
    
    # Linie dla wartości narastających (brygady A, B, C) - oś Y prawa
    for brygada in ['A', 'B', 'C']:
        mask = (df_long['Typ'] == 'Narastające') & (df_long['Kod'] == kod) & (df_long['Brygada'] == brygada)
        filtered = df_long[mask].copy().sort_values('Dzien')
        
        if not filtered.empty:
            series_data.append({
                'type': 'line',
                'name': f'Narastająco {brygada}',
                'x': filtered['Dzien'].tolist(),
                'y': filtered['Wartosc'].tolist(),
                'color': kolory_linie.get(brygada, '#666666'),
                'yaxis': 'y2'
            })
    
    return jsonify({
        'series': series_data,
        'kod': kod,
        'nazwa': nazwa
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
