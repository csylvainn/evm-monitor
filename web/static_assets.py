"""
Assets statiques pour l'interface web
CSS et JavaScript optimisés pour le dark mode
"""

# CSS principal avec dark mode
DARK_MODE_CSS = '''
/* Variables CSS pour le dark mode GitHub-inspired */
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #21262d;
    --bg-hover: #30363d;
    --bg-overlay: rgba(13, 17, 23, 0.8);
    
    --text-primary: #f0f6fc;
    --text-secondary: #8b949e;
    --text-muted: #656d76;
    --text-inverse: #24292f;
    
    --border-primary: #30363d;
    --border-secondary: #21262d;
    --border-muted: #484f58;
    
    --accent-blue: #58a6ff;
    --accent-blue-hover: #4493f8;
    --accent-green: #3fb950;
    --accent-green-hover: #2ea043;
    --accent-orange: #f85149;
    --accent-purple: #a5a5f5;
    --accent-yellow: #d29922;
    
    --shadow-small: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
    --shadow-medium: 0 4px 6px rgba(0, 0, 0, 0.16), 0 4px 6px rgba(0, 0, 0, 0.23);
    --shadow-large: 0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23);
    
    --radius-small: 6px;
    --radius-medium: 8px;
    --radius-large: 12px;
    
    --transition-fast: 0.15s ease;
    --transition-normal: 0.2s ease;
    --transition-slow: 0.3s ease;
}

/* Reset optimisé */
*, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* Base */
html {
    scroll-behavior: smooth;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
    overflow-x: hidden;
    min-height: 100vh;
}

/* Typographie */
h1, h2, h3, h4, h5, h6 {
    line-height: 1.25;
    font-weight: 600;
}

/* Layout principal */
.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header moderne */
.header {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
    padding: 16px 0;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 22px;
    font-weight: 700;
    color: var(--accent-blue);
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: var(--transition-fast);
}

.logo:hover {
    color: var(--accent-blue-hover);
    transform: translateY(-1px);
}

/* Navigation moderne */
.nav-tabs {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
}

.nav-container {
    display: flex;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.nav-container::-webkit-scrollbar {
    display: none;
}

.nav-tab {
    padding: 14px 20px;
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    white-space: nowrap;
    border-bottom: 3px solid transparent;
    transition: var(--transition-normal);
    position: relative;
    display: flex;
    align-items: center;
    gap: 8px;
}

.nav-tab:hover {
    color: var(--text-primary);
    background: var(--bg-hover);
}

.nav-tab.active {
    color: var(--accent-blue);
    border-bottom-color: var(--accent-blue);
    background: var(--bg-tertiary);
}

.nav-badge {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    line-height: 1;
}

.nav-tab.active .nav-badge {
    background: var(--accent-blue);
    color: var(--bg-primary);
}

/* Composants principaux */
.main {
    padding: 24px 0;
    min-height: calc(100vh - 200px);
}

/* Stats bar moderne */
.stats-bar {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-large);
    padding: 18px 24px;
    margin-bottom: 24px;
    font-size: 14px;
    line-height: 1.5;
    box-shadow: var(--shadow-small);
}

.stats-highlight {
    color: var(--accent-blue);
    font-weight: 600;
}

.stats-muted {
    color: var(--text-muted);
}

/* Recherche optimisée */
.search-section {
    margin-bottom: 24px;
}

.search-form {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.search-input {
    flex: 1;
    min-width: 280px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-medium);
    padding: 12px 16px;
    color: var(--text-primary);
    font-size: 14px;
    transition: var(--transition-normal);
}

.search-input:focus {
    outline: none;
    border-color: var(--accent-blue);
    box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
}

.search-input::placeholder {
    color: var(--text-muted);
}

/* Boutons modernes */
.btn {
    padding: 12px 20px;
    border: none;
    border-radius: var(--radius-medium);
    font-weight: 600;
    font-size: 14px;
    text-decoration: none;
    cursor: pointer;
    transition: var(--transition-normal);
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    user-select: none;
}

.btn-primary {
    background: var(--accent-blue);
    color: var(--bg-primary);
}

.btn-primary:hover {
    background: var(--accent-blue-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);
}

.btn-secondary {
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    border: 1px solid var(--border-primary);
}

.btn-secondary:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    border-color: var(--border-muted);
}

.refresh-btn {
    background: var(--accent-green);
    color: var(--bg-primary);
    padding: 10px 18px;
    border: none;
    border-radius: var(--radius-medium);
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
    transition: var(--transition-normal);
}

.refresh-btn:hover {
    background: var(--accent-green-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow-medium);
}

/* Tables élégantes */
.table-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-large);
    overflow: hidden;
    margin-bottom: 24px;
    box-shadow: var(--shadow-small);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    background: var(--bg-tertiary);
    color: var(--text-primary);
    padding: 16px 20px;
    text-align: left;
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid var(--border-primary);
}

td {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-secondary);
    font-size: 14px;
    vertical-align: middle;
}

tr:hover {
    background: var(--bg-hover);
}

tr:last-child td {
    border-bottom: none;
}

.mono {
    font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, monospace;
    font-size: 12px;
    color: var(--text-secondary);
    word-break: break-all;
}

/* Badges stylés */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: var(--radius-small);
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1;
}

.badge-wallet { 
    background: rgba(63, 185, 80, 0.15); 
    color: var(--accent-green);
    border: 1px solid rgba(63, 185, 80, 0.2);
}

.badge-contract { 
    background: rgba(248, 81, 73, 0.15); 
    color: var(--accent-orange);
    border: 1px solid rgba(248, 81, 73, 0.2);
}

.badge-unknown { 
    background: rgba(139, 148, 158, 0.15); 
    color: var(--text-secondary);
    border: 1px solid rgba(139, 148, 158, 0.2);
}

.badge-detected { 
    background: rgba(63, 185, 80, 0.15); 
    color: var(--accent-green);
    border: 1px solid rgba(63, 185, 80, 0.2);
}

.badge-failed { 
    background: rgba(248, 81, 73, 0.15); 
    color: var(--accent-orange);
    border: 1px solid rgba(248, 81, 73, 0.2);
}

.token-symbol {
    background: var(--bg-tertiary);
    color: var(--accent-purple);
    padding: 4px 10px;
    border-radius: var(--radius-small);
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Pagination moderne */
.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    margin: 24px 0;
}

.page-link {
    padding: 10px 14px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-medium);
    color: var(--text-secondary);
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition-normal);
    font-size: 14px;
}

.page-link:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
    transform: translateY(-1px);
}

.page-link.current {
    background: var(--accent-blue);
    color: var(--bg-primary);
    border-color: var(--accent-blue);
    box-shadow: var(--shadow-small);
}

.page-link.disabled {
    opacity: 0.4;
    pointer-events: none;
}

/* Grilles et cartes */
.overview-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
}

.overview-card {
    background: linear-gradient(135deg, var(--accent-blue), var(--accent-blue-hover));
    padding: 20px;
    border-radius: var(--radius-large);
    text-align: center;
    color: var(--bg-primary);
    box-shadow: var(--shadow-medium);
    transition: var(--transition-normal);
}

.overview-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-large);
}

.overview-card h3 {
    font-size: 13px;
    opacity: 0.9;
    margin-bottom: 8px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.overview-card .value {
    font-size: 24px;
    font-weight: 700;
    line-height: 1;
}

/* États spéciaux */
.no-data {
    text-align: center;
    padding: 48px 32px;
    color: var(--text-muted);
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-large);
    box-shadow: var(--shadow-small);
}

.no-data h3 {
    margin-bottom: 12px;
    color: var(--text-secondary);
    font-size: 18px;
}

.search-info {
    background: rgba(210, 153, 34, 0.1);
    border: 1px solid var(--accent-yellow);
    border-radius: var(--radius-medium);
    padding: 14px 18px;
    margin-bottom: 20px;
    font-size: 14px;
}

.search-term {
    color: var(--accent-yellow);
    font-weight: 600;
}

/* Charts et contrôles */
.chart-container {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-large);
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: var(--shadow-small);
}

.chart-container h3 {
    margin-bottom: 16px;
    color: var(--text-primary);
    font-size: 16px;
}

.controls {
    background: var(--bg-secondary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-large);
    padding: 18px 24px;
    margin-bottom: 24px;
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
    box-shadow: var(--shadow-small);
}

.form-select {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-primary);
    border-radius: var(--radius-medium);
    padding: 10px 12px;
    color: var(--text-primary);
    font-size: 14px;
    min-width: 140px;
}

/* Footer */
.footer {
    border-top: 1px solid var(--border-primary);
    padding: 20px 0;
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 32px;
    background: var(--bg-secondary);
}

/* Responsive optimisé */
@media (max-width: 768px) {
    .container { 
        padding: 0 16px; 
    }
    
    .header-content { 
        flex-direction: column; 
        gap: 12px; 
    }
    
    .search-form { 
        flex-direction: column; 
    }
    
    .search-input { 
        min-width: 100%; 
    }
    
    .overview-grid { 
        grid-template-columns: 1fr; 
    }
    
    table { 
        font-size: 12px; 
    }
    
    th, td { 
        padding: 12px 8px; 
    }
    
    .nav-tab {
        padding: 12px 16px;
        font-size: 14px;
    }
    
    .controls {
        flex-direction: column;
        align-items: stretch;
    }
}

/* Animations et micro-interactions */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.main {
    animation: fadeIn 0.3s ease;
}

/* États de focus améliorés */
button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible {
    outline: 2px solid var(--accent-blue);
    outline-offset: 2px;
}

/* Sélection de texte */
::selection {
    background: var(--accent-blue);
    color: var(--bg-primary);
}

/* Scrollbars stylées (WebKit) */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--border-muted);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text-muted);
}
'''

# JavaScript pour les interactions
CHART_JS = '''
// Configuration globale pour Chart.js avec dark mode
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = '#30363d';
Chart.defaults.backgroundColor = 'rgba(88, 166, 255, 0.1)';

// Fonction pour initialiser les graphiques
function initActivityChart(chartData) {
    if (!chartData || chartData.length === 0) return null;
    
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    const labels = chartData.map(item => item.time_slot);
    const walletsData = chartData.map(item => item.active_wallets);
    const transactionsData = chartData.map(item => item.total_transactions);
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Active Wallets',
                data: walletsData,
                backgroundColor: 'rgba(88, 166, 255, 0.6)',
                borderColor: '#58a6ff',
                borderWidth: 1,
                borderRadius: 4,
                yAxisID: 'y'
            }, {
                label: 'Transactions',
                data: transactionsData,
                type: 'line',
                backgroundColor: 'rgba(63, 185, 80, 0.1)',
                borderColor: '#3fb950',
                borderWidth: 2,
                fill: false,
                tension: 0.1,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                    }
                },
                tooltip: {
                    backgroundColor: '#21262d',
                    titleColor: '#f0f6fc',
                    bodyColor: '#8b949e',
                    borderColor: '#30363d',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toLocaleString();
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time (5-minute slots)',
                        color: '#8b949e'
                    },
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    },
                    ticks: {
                        color: '#8b949e'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Active Wallets',
                        color: '#58a6ff'
                    },
                    grid: {
                        color: 'rgba(48, 54, 61, 0.5)'
                    },
                    ticks: {
                        color: '#8b949e',
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Transactions',
                        color: '#3fb950'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        color: '#8b949e',
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Utilitaires pour les interactions
function changeDateChart() {
    const selectedDate = document.getElementById('dateSelect').value;
    if (selectedDate) {
        window.location.href = '/activity?date=' + selectedDate;
    }
}

// Animation d'apparition des éléments
function animateElements() {
    const elements = document.querySelectorAll('.table-container, .overview-card, .chart-container');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// Initialisation au chargement
document.addEventListener('DOMContentLoaded', function() {
    animateElements();
    
    // Auto-focus sur la recherche
    const searchInput = document.querySelector('.search-input');
    if (searchInput && !searchInput.value) {
        searchInput.focus();
    }
});
'''