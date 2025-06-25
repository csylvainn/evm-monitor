"""
Template pour les wallets/adresses
web/templates/wallets.py
"""

from .base import BASE_TEMPLATE

# Template pour les wallets/adresses
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
                    <td class="mono">{{ wallet.address }}</td>
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
{% endblock %}'''
).replace('{% block refresh_url %}/{% endblock %}', '/')