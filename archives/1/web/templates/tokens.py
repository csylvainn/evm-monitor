"""
Template pour les tokens ERC-20
web/templates/tokens.py
"""

from .base import BASE_TEMPLATE

# Template pour les tokens
TOKENS_TEMPLATE = BASE_TEMPLATE.replace(
    '{% block content %}{% endblock %}',
    '''{% block content %}
    <!-- Stats -->
    <div class="stats-bar">
        <span class="stats-highlight">🪙 {{ "{:,}".format(total_tokens) }} Tokens</span>
        <span class="stats-muted">
            • Page {{ current_page }} of {{ total_pages }}
            • Showing {{ tokens|length }} items
            {% if token_stats.get('detected', 0) > 0 %}
                • {{ "{:,}".format(token_stats.get('detected', 0)) }} detected
            {% endif %}
            {% if token_stats.get('failed', 0) > 0 %}
                • {{ "{:,}".format(token_stats.get('failed', 0)) }} failed
            {% endif %}
            {% if search_term %}• Filtered by search{% endif %}
        </span>
    </div>
    
    <!-- Search -->
    <div class="search-section">
        <form method="GET" class="search-form">
            <input type="text" 
                   name="search" 
                   value="{{ search_term or '' }}" 
                   placeholder="Search tokens by name, symbol or address..." 
                   class="search-input">
            {% if current_status %}
                <input type="hidden" name="status" value="{{ current_status }}">
            {% endif %}
            <button type="submit" class="btn btn-primary">🔍 Search</button>
            {% if search_term %}
                <a href="{{ '?status=' + current_status if current_status else '/tokens' }}" class="btn btn-secondary">✖ Clear</a>
            {% endif %}
        </form>
    </div>
    
    <!-- Search info -->
    {% if search_term %}
    <div class="search-info">
        🔍 Results for <span class="search-term">"{{ search_term }}"</span> 
        — {{ "{:,}".format(total_tokens) }} matching token(s)
    </div>
    {% endif %}
    
    <!-- Table -->
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Token</th>
                    <th>Symbol</th>
                    <th>Supply</th>
                    <th>Contract</th>
                    <th>Discovered</th>
                </tr>
            </thead>
            <tbody>
                {% for token in tokens %}
                <tr>
                    <td>
                        <strong>{{ token.name }}</strong>
                        <div class="mono" style="font-size: 11px; color: var(--text-muted);">
                            {{ token.decimals }} decimals
                        </div>
                    </td>
                    <td>
                        <span class="token-symbol">{{ token.symbol }}</span>
                    </td>
                    <td>
                        <div style="font-weight: 600;">{{ token.total_supply_formatted }}</div>
                        <div class="mono" style="font-size: 11px; color: var(--text-muted);">
                            {{ format_number(token.total_supply) }}
                        </div>
                    </td>
                    <td class="mono">{{ token.address }}</td>
                    <td class="mono">{{ token.discovered_at }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    {% if total_pages > 1 %}
    <div class="pagination">
        {% set base_params = build_pagination_url(search_term, current_status, is_tokens=True) %}
        
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
{% endblock %}'''
).replace('{% block refresh_url %}/{% endblock %}', '/tokens')