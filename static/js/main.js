// Firmowy Kiosk - Główny plik JavaScript

// Stan aplikacji
let currentSection = 'wykresy';
let rotationTimer = 30;
let rotationInterval = null;
let timerInterval = null;
let charts = {};
let slides = [];
let currentSlide = 0;
let slideInterval = null;

// ==================== INICJALIZACJA ====================

document.addEventListener('DOMContentLoaded', () => {
    // Inicjalizuj aplikację
    initializeApp();
    
    // Sprawdź zapisany tryb ciemny
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark');
        updateThemeButton(true);
    }
    
    // Ukryj kursor w trybie kiosk po 5 sekundach bezczynności
    let cursorTimeout;
    document.addEventListener('mousemove', () => {
        document.body.classList.remove('kiosk-mode');
        clearTimeout(cursorTimeout);
        cursorTimeout = setTimeout(() => {
            document.body.classList.add('kiosk-mode');
        }, 5000);
    });
});

// ==================== FUNKCJE GŁÓWNE ====================

async function initializeApp() {
    // Wyświetl aktualny czas
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
    // Załaduj dane
    await loadChartData();
    await loadInspirationsData();
    await loadSlidesData();
    
    // Załaduj dodatkową treść
    await loadContent();
    
    // Rozpocznij automatyczną rotację
    startAutoRotation();
    
    // Ustaw pierwszą sekcję jako aktywną
    showSection('wykresy');
    
    // Auto-refresh co 5 minut
    setInterval(refreshContent, 5 * 60 * 1000);
}

function updateCurrentTime() {
    const now = new Date();
    const timeStr = now.toLocaleString('pl-PL', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('current-time').textContent = timeStr;
}

// ==================== NAWIGACJA SEKCJI ====================

function showSection(sectionName) {
    // Usuń aktywność ze wszystkich sekcji i przycisków
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
        section.classList.add('hidden');
    });
    
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Aktywuj wybraną sekcję
    const section = document.getElementById(`section-${sectionName}`);
    if (section) {
        section.classList.remove('hidden');
        setTimeout(() => section.classList.add('active'), 10);
    }
    
    // Aktywuj przycisk
    const btn = document.querySelector(`[data-section="${sectionName}"]`);
    if (btn) {
        btn.classList.add('active');
    }
    
    currentSection = sectionName;
    
    // Specjalne akcje dla różnych sekcji
    if (sectionName === 'zdjecia') {
        startSlideshow();
    } else {
        stopSlideshow();
    }
    
    // Resetuj timer rotacji
    resetRotationTimer();
}

// ==================== AUTOMATYCZNA ROTACJA ====================

function startAutoRotation() {
    const sections = ['wykresy', 'inspiracje', 'zdjecia', 'o-nas'];
    let currentIndex = 0;
    
    rotationInterval = setInterval(() => {
        currentIndex = (currentIndex + 1) % sections.length;
        showSection(sections[currentIndex]);
    }, 30000); // 30 sekund
    
    // Timer wizualny
    rotationTimer = 30;
    timerInterval = setInterval(() => {
        rotationTimer--;
        document.getElementById('rotation-timer').textContent = rotationTimer;
        
        if (rotationTimer <= 0) {
            rotationTimer = 30;
        }
    }, 1000);
}

function resetRotationTimer() {
    rotationTimer = 30;
    document.getElementById('rotation-timer').textContent = rotationTimer;
}

// ==================== WYKRESY ====================

async function loadChartData() {
    try {
        const response = await fetch('/api/chart-data');
        const data = await response.json();
        
        if (data && data.length > 0) {
            createCharts(data);
        }
    } catch (error) {
        console.error('Błąd ładowania danych wykresów:', error);
    }
}

function createCharts(data) {
    // Przygotuj dane
    const labels = data.map(item => item.miesiąc || item.miesiac || '');
    const productionData = data.map(item => item.produkcja || 0);
    const innovationData = data.map(item => item.innowacje || 0);
    const efficiencyData = data.map(item => item.efektywność || item.efektywnosc || 0);
    
    // Wspólne opcje dla wykresów
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                }
            },
            x: {
                grid: {
                    display: false
                }
            }
        }
    };
    
    // Wykres produkcji (słupkowy)
    const ctxProduction = document.getElementById('productionChart');
    if (ctxProduction) {
        charts.production = new Chart(ctxProduction, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Produkcja',
                    data: productionData,
                    backgroundColor: 'rgba(255, 107, 53, 0.8)',
                    borderColor: 'rgba(255, 107, 53, 1)',
                    borderWidth: 2
                }]
            },
            options: commonOptions
        });
    }
    
    // Wykres innowacji (liniowy)
    const ctxInnovation = document.getElementById('innovationChart');
    if (ctxInnovation) {
        charts.innovation = new Chart(ctxInnovation, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Innowacje',
                    data: innovationData,
                    backgroundColor: 'rgba(0, 78, 137, 0.2)',
                    borderColor: 'rgba(0, 78, 137, 1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: commonOptions
        });
    }
    
    // Wykres efektywności (obszarowy)
    const ctxEfficiency = document.getElementById('efficiencyChart');
    if (ctxEfficiency) {
        charts.efficiency = new Chart(ctxEfficiency, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Efektywność (%)',
                    data: efficiencyData,
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                ...commonOptions,
                scales: {
                    ...commonOptions.scales,
                    y: {
                        ...commonOptions.scales.y,
                        min: 0,
                        max: 100
                    }
                }
            }
        });
    }
}

// ==================== INSPIRACJE ====================

async function loadInspirationsData() {
    try {
        const response = await fetch('/api/inspirations');
        const inspirations = await response.json();
        
        displayInspirations(inspirations);
    } catch (error) {
        console.error('Błąd ładowania inspiracji:', error);
    }
}

function displayInspirations(inspirations) {
    const container = document.getElementById('inspirations-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    inspirations.forEach((insp, index) => {
        const card = document.createElement('div');
        card.className = 'inspiration-card bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden fade-in';
        card.style.animationDelay = `${index * 0.1}s`;
        
        card.innerHTML = `
            <img src="${insp.image_url}" alt="${insp.title}" class="w-full h-64 object-cover">
            <div class="p-6">
                <h3 class="text-2xl font-bold text-gray-800 dark:text-white mb-3">${insp.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-lg leading-relaxed">${insp.description}</p>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// ==================== POKAZ SLAJDÓW ====================

async function loadSlidesData() {
    try {
        const response = await fetch('/api/slides');
        slides = await response.json();
        
        if (slides.length === 0) {
            // Dodaj domyślne obrazy zastępcze jeśli brak
            slides = [
                { url: 'https://picsum.photos/1920/1080?random=1', name: 'Slajd 1' },
                { url: 'https://picsum.photos/1920/1080?random=2', name: 'Slajd 2' },
                { url: 'https://picsum.photos/1920/1080?random=3', name: 'Slajd 3' }
            ];
        }
        
        createSlideshowDots();
    } catch (error) {
        console.error('Błąd ładowania slajdów:', error);
    }
}

function createSlideshowDots() {
    const dotsContainer = document.getElementById('slideshow-dots');
    if (!dotsContainer) return;
    
    dotsContainer.innerHTML = '';
    
    slides.forEach((_, index) => {
        const dot = document.createElement('div');
        dot.className = 'slide-dot';
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });
}

function startSlideshow() {
    if (slides.length === 0) return;
    
    currentSlide = 0;
    showSlide(currentSlide);
    
    slideInterval = setInterval(() => {
        currentSlide = (currentSlide + 1) % slides.length;
        showSlide(currentSlide);
    }, 5000); // Zmiana co 5 sekund
}

function stopSlideshow() {
    if (slideInterval) {
        clearInterval(slideInterval);
        slideInterval = null;
    }
}

function showSlide(index) {
    const img = document.getElementById('slideshow-image');
    if (!img || !slides[index]) return;
    
    // Fade out
    img.style.opacity = '0';
    
    setTimeout(() => {
        img.src = slides[index].url;
        img.style.opacity = '1';
        
        // Aktualizuj kropki
        document.querySelectorAll('.slide-dot').forEach((dot, i) => {
            dot.classList.toggle('active', i === index);
        });
    }, 400);
}

function goToSlide(index) {
    stopSlideshow();
    currentSlide = index;
    showSlide(currentSlide);
    startSlideshow();
}

// ==================== TRYB CIEMNY ====================

function toggleDarkMode() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', isDark);
    updateThemeButton(isDark);
    
    // Odśwież wykresy dla nowego motywu
    updateChartsTheme(isDark);
}

function updateThemeButton(isDark) {
    document.getElementById('theme-icon').textContent = isDark ? '☀️' : '🌙';
    document.getElementById('theme-text').textContent = isDark ? 'Tryb jasny' : 'Tryb ciemny';
}

function updateChartsTheme(isDark) {
    const textColor = isDark ? '#FFFFFF' : '#333333';
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';
    
    Object.values(charts).forEach(chart => {
        if (chart && chart.options) {
            chart.options.scales.x.ticks = { color: textColor };
            chart.options.scales.y.ticks = { color: textColor };
            chart.options.scales.y.grid = { color: gridColor };
            chart.update();
        }
    });
}

// ==================== AUTO-REFRESH ====================

async function loadContent() {
    try {
        const response = await fetch('/api/content');
        const content = await response.json();
        
        // Aktualizuj teksty
        if (content.about_text) {
            const aboutEl = document.getElementById('about-text');
            if (aboutEl) aboutEl.textContent = content.about_text;
        }
    } catch (error) {
        console.error('Błąd ładowania treści:', error);
    }
}

async function refreshContent() {
    console.log('🔄 Automatyczne odświeżanie treści...');
    
    // Przeładuj wszystkie dane
    await loadChartData();
    await loadInspirationsData();
    await loadSlidesData();
    await loadContent();
}

// ==================== EKSPORTOWANE FUNKCJE ====================

// Funkcje dostępne globalnie dla HTML
window.showSection = showSection;
window.toggleDarkMode = toggleDarkMode;
window.goToSlide = goToSlide;
