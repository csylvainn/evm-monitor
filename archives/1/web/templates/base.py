"""
Template de base optimisé avec dark mode minimaliste
web/templates/base.py
"""

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}HyperEVM Monitor{% endblock %}</title>
    <style>
        /* Variables CSS pour le dark mode */
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --bg-hover: #30363d;
            --text-primary: #f0f6fc;
            --text-secondary: #8b949e;
            --text-muted: #656d76;
            --border-primary: #30363d;
            --border-secondary: #21262d;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-orange: #f85149;
            --accent-purple: #a5a5f5;
            --accent-yellow: #d29922;
            --shadow: rgba(0, 0, 0, 0.4);
        }
        
        /* Reset et base */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        /* Layout principal */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* Header */
        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-primary);
            padding: 20px 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(12px);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent-blue);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .refresh-btn {
            background: var(--accent-green);
            color: var(--bg-primary);
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .refresh-btn:hover {
            background: #2ea043;
            transform: translateY(-1px);
        }
        
        /* Navigation tabs */
        .nav-tabs {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-primary);
        }
        
        .nav-container {
            display: flex;
            overflow-x: auto;
            scrollbar-width: none;
        }
        
        .nav-container::-webkit-scrollbar { display: none; }
        
        .nav-tab {
            padding: 16px 24px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            white-space: nowrap;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            position: relative;
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
            font-size: 12px;
            margin-left: 8px;
            font-weight: 600;
        }
        
        .nav-tab.active .nav-badge {
            background: var(--accent-blue);
            color: var(--bg-primary);
        }
        
        /* Main content */
        .main {
            padding: 32px 0;
            min-height: calc(100vh - 200px);
        }
        
        /* Stats bar */
        .stats-bar {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 32px;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .stats-highlight {
            color: var(--accent-blue);
            font-weight: 600;
        }
        
        .stats-muted {
            color: var(--text-muted);
            font-style: italic;
        }
        
        /* Search */
        .search-section {
            margin-bottom: 32px;
        }
        
        .search-form {
            display: flex;
            gap: 12px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .search-input {
            flex: 1;
            min-width: 300px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            padding: 12px 16px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.2s ease;
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(88, 166, 255, 0.1);
        }
        
        .search-input::placeholder {
            color: var(--text-muted);
        }
        
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 14px;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: var(--accent-blue);
            color: var(--bg-primary);
        }
        
        .btn-primary:hover {
            background: #4493f8;
            transform: translateY(-1px);
        }
        
        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            border: 1px solid var(--border-primary);
        }
        
        .btn-secondary:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }
        
        /* Search info */
        .search-info {
            background: rgba(210, 153, 34, 0.1);
            border: 1px solid var(--accent-yellow);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
            font-size: 14px;
        }
        
        .search-term {
            color: var(--accent-yellow);
            font-weight: 600;
        }
        
        /* Table */
        .table-container {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 32px;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            padding: 16px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            border-bottom: 1px solid var(--border-primary);
        }
        
        td {
            padding: 16px;
            border-bottom: 1px solid var(--border-secondary);
            font-size: 14px;
        }
        
        tr:hover {
            background: var(--bg-hover);
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        .mono {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 12px;
            color: var(--text-secondary);
            word-break: break-all;
        }
        
        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-wallet { background: rgba(63, 185, 80, 0.1); color: var(--accent-green); }
        .badge-contract { background: rgba(248, 81, 73, 0.1); color: var(--accent-orange); }
        .badge-unknown { background: rgba(139, 148, 158, 0.1); color: var(--text-secondary); }
        .badge-detected { background: rgba(63, 185, 80, 0.1); color: var(--accent-green); }
        .badge-failed { background: rgba(248, 81, 73, 0.1); color: var(--accent-orange); }
        
        .token-symbol {
            background: var(--bg-tertiary);
            color: var(--accent-purple);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 11px;
        }
        
        /* Pagination */
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin: 32px 0;
        }
        
        .page-link {
            padding: 10px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .page-link:hover {
            background: var(--bg-hover);
            color: var(--text-primary);
        }
        
        .page-link.current {
            background: var(--accent-blue);
            color: var(--bg-primary);
            border-color: var(--accent-blue);
        }
        
        .page-link.disabled {
            opacity: 0.5;
            pointer-events: none;
        }
        
        /* Charts et grids */
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 32px;
        }
        
        .overview-card {
            background: linear-gradient(135deg, var(--accent-blue), #4493f8);
            padding: 24px;
            border-radius: 12px;
            text-align: center;
            color: var(--bg-primary);
        }
        
        .overview-card h3 {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 8px;
            font-weight: 500;
        }
        
        .overview-card .value {
            font-size: 28px;
            font-weight: 700;
        }
        
        .chart-container {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 32px;
        }
        
        .chart-container h3 {
            margin-bottom: 20px;
            color: var(--text-primary);
        }
        
        /* Controls */
        .controls {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 32px;
            display: flex;
            gap: 16px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .form-select {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-primary);
            border-radius: 8px;
            padding: 10px 12px;
            color: var(--text-primary);
            font-size: 14px;
        }
        
        /* Footer */
        .footer {
            border-top: 1px solid var(--border-primary);
            padding: 24px 0;
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 48px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container { padding: 0 16px; }
            .header-content { flex-direction: column; gap: 16px; }
            .search-form { flex-direction: column; }
            .search-input { min-width: 100%; }
            .overview-grid { grid-template-columns: 1fr; }
            table { font-size: 12px; }
            th, td { padding: 12px 8px; }
        }
        
        /* Loading states */
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
        
        /* No data */
        .no-data {
            text-align: center;
            padding: 64px 32px;
            color: var(--text-muted);
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: 12px;
        }
        
        .no-data h3 {
            margin-bottom: 12px;
            color: var(--text-secondary);
        }
    </style>
    {% block extra_styles %}{% endblock %}
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="header-content">
                <a href="/" class="logo">
                    🔗 HyperEVM Monitor
                </a>
                <a href="{% block refresh_url %}/{% endblock %}" class="refresh-btn">
                    🔄 Refresh
                </a>
            </div>
        </div>
    </header>
    
    <!-- Navigation -->
    <nav class="nav-tabs">
        <div class="container">
            <div class="nav-container">
                {% set nav_items = [
                    ('/', 'All Addresses', type_stats.get('total', 0), 'current_type' not in request.args or not current_type),
                    ('/?type=wallet', 'Wallets', type_stats.get('wallet', {}).get('count', 0), current_type == 'wallet'),
                    ('/?type=contract', 'Contracts', type_stats.get('contract', {}).get('count', 0), current_type == 'contract'),
                    ('/?type=unknown', 'Unknown', type_stats.get('unknown', {}).get('count', 0), current_type == 'unknown'),
                    ('/tokens', 'Tokens', token_stats.get('total', 0), request.endpoint == 'tokens'),
                    ('/activity', 'Activity', '', request.endpoint == 'activity_stats')
                ] %}
                
                {% for url, label, count, is_active in nav_items %}
                <a href="{{ url }}" class="nav-tab {{ 'active' if is_active else '' }}">
                    {{ label }}
                    {% if count != '' %}
                        <span class="nav-badge">{{ "{:,}".format(count) }}</span>
                    {% endif %}
                </a>
                {% endfor %}
            </div>
        </div>
    </nav>
    
    <!-- Main content -->
    <main class="main">
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            {% block footer_text %}
            Real-time HyperEVM blockchain monitoring | Auto-discovery & classification
            {% endblock %}
        </div>
    </footer>
    
    {% block scripts %}{% endblock %}
</body>
</html>
'''