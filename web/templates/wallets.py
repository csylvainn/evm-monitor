# web/templates/wallets.py - VERSION MODIFIÉE avec liens vers détails wallets

"""
Template pour les wallets/adresses - Version avec liens cliquables
web/templates/wallets.py
"""

from .base import BASE_TEMPLATE

# Template pour les wallets/adresses avec liens vers les détails
WALLETS_TEMPLATE = BASE_TEMPLATE.replace(
    '{% block content %}{% endblock %}',
    '''{% block content %}
    <!-- Stats -->
    <div class="stats-bar">
        {% if current_type == 'wallet' %}
            <span class="stats-highlight">👤 {{ "{:,}".format(total_wallets) }} Wallets</span>
        {% elif current_type == 'contract' %}
            <span class="stats-highlight">📜 {{ "{:,}".format(total_wallets) }} Contracts</span>
        {% elif current_type == 'unknown' %}
            <span class="stats-highlight">❓ {{ "{:,}".format(total_wallets) }} Unknown</span>
        {% else %}
            <span class="stats-highlight">📊 {{ "{:,}".format(total_wallets) }} Total Addresses</span>
        {% endif %}
        
        <span class="stats-muted">
            • Page {{ current_page }} of {{ total_pages }}
            • Showing {{ wallets|length }} items
            {% if search_term %}• Filtered by search{% endif %}
            {% if current_type == 'wallet' %}• Click address for token details{% endif %}
        </span>
    </div>
    
    <!-- Search -->
    <div class="search-section">
        <form method="GET" class="search-form">
            <input type="text" 
                   name="search" 
                   value="{{ search_term or '' }}" 
                   placeholder="Search addresses..." 
                   class="search-input">
            {% if current_type %}
                <input type="hidden" name="type" value="{{ current_type }}">
            {% endif %}
            <button type="submit" class="btn btn-primary">🔍 Search</button>
            {% if search_term %}
                <a href="{{ '?type=' + current_type if current_type else '/' }}" class="btn btn-secondary">✖ Clear</a>
            {% endif %}
        </form>
    </div>
    
    <!-- Search info -->
    {% if search_term %}
    <div class="search-info">
        🔍 Results for <span class="search-term">"{{ search_term }}"</span> 
        — {{ "{:,}".format(total_wallets) }} matching address(es)
    </div>
    {% endif %}
    
    <!-- Table -->
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Address</th>
                    <th>Type</th>
                    <th>Last Block</th>
                    <th>Last Activity</th>
                    <th>Updated</th>
                </tr>
            </thead>
            <tbody>
                {% for wallet in wallets %}
                <tr>
                    <td class="mono">
                        {% if wallet.type == 'wallet' %}
                            <a href="/wallet/{{ wallet.address }}" 
                               style="color: var(--accent-blue); text-decoration: none; transition: var(--transition-fast);"
                               onmouseover="this.style.textDecoration='underline'"
                               onmouseout="this.style.textDecoration='none'"
                               title="View wallet details and token holdings">
                                {{ wallet.address }}
                            </a>
                        {% else %}
                            {{ wallet.address }}
                        {% endif %}
                    </td>
                    <td>
                        {% if wallet.type == 'wallet' %}
                            <span class="badge badge-wallet">👤 Wallet</span>
                        {% elif wallet.type == 'contract' %}
                            <span class="badge badge-contract">📜 Contract</span>
                        {% else %}
                            <span class="badge badge-unknown">❓ Unknown</span>
                        {% endif %}
                    </td>
                    <td>{{ wallet.last_block }}</td>
                    <td>{{ wallet.last_activity }}</td>
                    <td class="mono">{{ wallet.updated_at }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    {% if total_pages > 1 %}
    <div class="pagination">
        {% set base_params = build_pagination_url(search_term, current_type) %}
        
        {% if has_prev %}
            <a href="{{ base_params }}page=1" class="page-link">❮❮ First</a>
            <a href="{{ base_params }}page={{ prev_page }}" class="page-link">❮ Prev</a>
        {% else %}
            <span class="page-link disabled">❮❮ First</span>
            <span class="page-link disabled">❮ Prev</span>
        {% endif %}
        
        {% for page_num in page_numbers %}
            {% if page_num == current_page %}
                <span class="page-link current">{{ page_num }}</span>
            {% else %}
                <a href="{{ base_params }}page={{ page_num }}" class="page-link">{{ page_num }}</a>
            {% endif %}
        {% endfor %}
        
        {% if has_next %}
            <a href="{{ base_params }}page={{ next_page }}" class="page-link">Next ❯</a>
            <a href="{{ base_params }}page={{ total_pages }}" class="page-link">Last ❯❯</a>
        {% else %}
            <span class="page-link disabled">Next ❯</span>
            <span class="page-link disabled">Last ❯❯</span>
        {% endif %}
    </div>
    {% endif %}
    
    <!-- Info sur le scanner -->
    {% if current_type == 'wallet' %}
    <div style="margin-top: 24px; padding: 16px; background: rgba(88, 166, 255, 0.1); border: 1px solid var(--accent-blue); border-radius: var(--radius-medium); font-size: 14px;">
        💡 <strong>Tip:</strong> Click on any wallet address to view its token holdings. 
        Run <code style="background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px;">python simple_scan_wallets.py</code> to scan for tokens.
    </div>
    {% endif %}
{% endblock %}'''
).replace('{% block refresh_url %}/{% endblock %}', '/')

# ===== AJOUT DES SCANNERS STATS DANS LA NAVIGATION =====

# web/templates/base.py - MODIFICATION pour ajouter les stats de scan

# Dans le BASE_TEMPLATE, remplacer la section de navigation par :

ENHANCED_NAVIGATION = '''
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
                
                <!-- Scanner Stats -->
                <div style="margin-left: auto; padding: 12px 16px; color: var(--text-muted); font-size: 12px;">
                    {% try %}
                        {% set scan_stats = db.get_wallet_scan_stats() %}
                        {% if scan_stats.scanned_wallets > 0 %}
                            📊 Scanned: {{ "{:,}".format(scan_stats.scanned_wallets) }} wallets
                            • {{ "{:,}".format(scan_stats.total_holdings) }} holdings
                        {% endif %}
                    {% except %}
                        <!-- Stats non disponibles -->
                    {% endtry %}
                </div>
            </div>
        </div>
    </nav>
'''

# ===== STYLES SUPPLÉMENTAIRES POUR LES LIENS =====

WALLET_LINK_STYLES = '''
/* Styles pour les liens de wallets */
.wallet-link {
    color: var(--accent-blue);
    text-decoration: none;
    transition: var(--transition-fast);
    position: relative;
}

.wallet-link:hover {
    color: var(--accent-blue-hover);
    text-decoration: underline;
}

.wallet-link::before {
    content: '👁️';
    position: absolute;
    left: -20px;
    opacity: 0;
    transition: var(--transition-fast);
    font-size: 12px;
}

.wallet-link:hover::before {
    opacity: 0.7;
}

/* Badge pour les wallets scannés */
.scanned-badge {
    background: rgba(63, 185, 80, 0.1);
    color: var(--accent-green);
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 10px;
    margin-left: 8px;
    font-weight: 600;
}

/* Info box pour le scanner */
.scanner-info {
    background: rgba(88, 166, 255, 0.1);
    border: 1px solid var(--accent-blue);
    border-radius: var(--radius-medium);
    padding: 16px;
    margin-top: 24px;
    font-size: 14px;
}

.scanner-info code {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'SF Mono', Monaco, monospace;
}
'''

# ===== TEMPLATE D'ERREUR AMÉLIORÉ =====

ENHANCED_ERROR_TEMPLATE = '''
<div class="no-data">
    <h3>{{ title }}</h3>
    <p>{{ message }}</p>
    <div style="margin-top: 16px;">
        <a href="/" class="btn btn-primary">← Back to Home</a>
        <a href="javascript:history.back()" class="btn btn-secondary" style="margin-left: 8px;">↶ Go Back</a>
    </div>
    {% if error_code == 404 and 'wallet' in request.path %}
    <div style="margin-top: 12px; font-size: 12px; color: var(--text-muted);">
        💡 Make sure the wallet address is valid and has been discovered by the monitor.
    </div>
    {% endif %}
    <div style="margin-top: 12px; font-size: 12px; color: var(--text-muted);">
        Error Code: {{ error_code }}
    </div>
</div>
'''

# ===== JAVASCRIPT POUR LES INTERACTIONS =====

WALLET_INTERACTIONS_JS = '''
<script>
// JavaScript pour les interactions des wallets
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter des tooltips aux liens de wallets
    const walletLinks = document.querySelectorAll('a[href^="/wallet/"]');
    walletLinks.forEach(link => {
        link.addEventListener('mouseenter', function() {
            // Créer un tooltip simple
            const tooltip = document.createElement('div');
            tooltip.className = 'wallet-tooltip';
            tooltip.textContent = 'Click to view token holdings';
            tooltip.style.cssText = `
                position: absolute;
                background: var(--bg-tertiary);
                color: var(--text-primary);
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                z-index: 1000;
                pointer-events: none;
                border: 1px solid var(--border-primary);
            `;
            document.body.appendChild(tooltip);
            
            // Positionner le tooltip
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + 'px';
            tooltip.style.top = (rect.bottom + 5) + 'px';
            
            this._tooltip = tooltip;
        });
        
        link.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                document.body.removeChild(this._tooltip);
                this._tooltip = null;
            }
        });
    });
    
    // Animation d'apparition des éléments
    const elements = document.querySelectorAll('.table-container, .stats-bar, .search-section');
    elements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            el.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, index * 100);
    });
});

// Fonction pour copier l'adresse dans le presse-papiers
function copyAddress(address) {
    navigator.clipboard.writeText(address).then(function() {
        // Créer une notification temporaire
        const notification = document.createElement('div');
        notification.textContent = 'Address copied!';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--accent-green);
            color: var(--bg-primary);
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 2000);
    });
}

// CSS pour l'animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
`;
document.head.appendChild(style);
</script>
'''

# ===== RÉCAPITULATIF DES MODIFICATIONS =====

# MODIFICATION 1: web/templates/wallets.py
# - Ajouter des liens cliquables pour les wallets (type='wallet')
# - Ajouter un tooltip explicatif
# - Ajouter une info box sur le scanner

# MODIFICATION 2: web/templates/base.py (optionnel)
# - Ajouter les stats de scan dans la navigation
# - Améliorer les styles pour les liens

# MODIFICATION 3: viewer.py
# - Remplacer complètement par le fichier complet fourni
# - Nouvelles routes /wallet/<address> et API

# MODIFICATION 4: Styles CSS supplémentaires (optionnel)
# - Ajouter les styles pour les liens et interactions
# - Améliorer l'UX avec des animations

print("""
=== RÉSUMÉ DES MODIFICATIONS ===

1. **web/templates/wallets.py** - OBLIGATOIRE
   Remplacer le contenu par WALLETS_TEMPLATE ci-dessus
   
2. **viewer.py** - OBLIGATOIRE  
   Remplacer complètement par le fichier fourni dans l'artifact précédent
   
3. **Styles CSS** - OPTIONNEL
   Ajouter WALLET_LINK_STYLES dans base.py pour de meilleurs effets visuels
   
4. **JavaScript** - OPTIONNEL
   Ajouter WALLET_INTERACTIONS_JS pour les tooltips et animations

=== FONCTIONNALITÉS AJOUTÉES ===

✅ Liens cliquables sur les adresses de wallets
✅ Page de détails des wallets avec tokens
✅ API endpoints pour les données de wallets
✅ Intégration complète du scanner
✅ Gestion d'erreurs améliorée
✅ Interface utilisateur optimisée

=== UTILISATION ===

1. Après avoir scanné des wallets avec simple_scan_wallets.py
2. Aller sur l'interface web
3. Cliquer sur n'importe quelle adresse de wallet
4. Voir les détails et holdings de tokens

""")
