#!/usr/bin/env python3
"""
HyperEVM Wallet Viewer - Version complète avec scanner de wallets
Interface web moderne et minimaliste avec architecture clean
Version 4.0 - Code optimisé avec détails des wallets
"""

import sys
import os
import json
import time
from pathlib import Path

# Configuration des chemins
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports Flask
from flask import Flask, render_template_string, request, g, jsonify

# Imports configuration et base de données
from config.settings import WEB_HOST, WEB_PORT, WALLETS_PER_PAGE, MESSAGES
from core.database import Database
from core.utils import format_number, format_supply

# Imports templates modulaires
from web.templates import WALLETS_TEMPLATE, TOKENS_TEMPLATE, ACTIVITY_TEMPLATE

# Imports helpers refactorisés
from web.utils import (
    PaginationHelper, 
    ValidationHelper, 
    DataFormatter, 
    TemplateContextBuilder,
    ResponseHelper
)

# Configuration de l'application
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Instance globale de la base de données
db = Database()

# Helper instances pour réutilisation
pagination_helper = PaginationHelper()
validator = ValidationHelper()
formatter = DataFormatter()
context_builder = TemplateContextBuilder()
response_helper = ResponseHelper()


class WebConstants:
    """Constantes pour l'interface web"""
    DEFAULT_PAGE = 1
    VALID_ENDPOINTS = ['tokens', 'activity_stats', 'wallet']
    ERROR_MESSAGES = {
        'not_found': "🚫 Page Not Found",
        'server_error': "⚠️ Server Error", 
        'not_found_desc': "The page you're looking for doesn't exist.",
        'server_error_desc': "Something went wrong. Please try again later.",
        'wallet_not_found': "Wallet not found in database.",
        'invalid_address': "Invalid wallet address format."
    }


# Template pour les détails du wallet
WALLET_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Wallet {{ wallet.address[:8] }}... - HyperEVM</title>
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
            --radius-small: 6px;
            --radius-medium: 8px;
            --radius-large: 12px;
            --transition-fast: 0.15s ease;
            --transition-normal: 0.2s ease;
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
        
        /* Layout */
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
        
        /* Main content */
        .main {
            padding: 32px 0;
            min-height: calc(100vh - 200px);
        }
        
        /* Breadcrumb */
        .breadcrumb {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-medium);
            padding: 12px 20px;
            margin-bottom: 24px;
            font-size: 14px;
        }
        
        .breadcrumb a {
            color: var(--accent-blue);
            text-decoration: none;
        }
        
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        
        .breadcrumb-separator {
            color: var(--text-muted);
            margin: 0 8px;
        }
        
        /* Wallet header */
        .wallet-header {
            background: linear-gradient(135deg, var(--bg-secondary), var(--bg-tertiary));
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-large);
            padding: 24px;
            margin-bottom: 24px;
            position: relative;
            overflow: hidden;
        }
        
        .wallet-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-blue), var(--accent-green));
        }
        
        .wallet-address {
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
            font-size: 18px;
            font-weight: 600;
            color: var(--accent-blue);
            word-break: break-all;
            margin-bottom: 16px;
        }
        
        .wallet-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border-secondary);
            border-radius: var(--radius-medium);
            padding: 16px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: 700;
            color: var(--accent-blue);
            display: block;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Badges */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: var(--radius-small);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-wallet { 
            background: rgba(63, 185, 80, 0.1); 
            color: var(--accent-green);
            border: 1px solid rgba(63, 185, 80, 0.2);
        }
        
        /* Tokens section */
        .tokens-section {
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-large);
            overflow: hidden;
        }
        
        .section-header {
            background: var(--bg-tertiary);
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-primary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }
        
        .rescan-btn {
            background: var(--accent-green);
            color: var(--bg-primary);
            padding: 8px 16px;
            border: none;
            border-radius: var(--radius-medium);
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: var(--transition-normal);
        }
        
        .rescan-btn:hover {
            background: #2ea043;
            transform: translateY(-1px);
        }
        
        /* Table */
        .tokens-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .tokens-table th {
            background: var(--bg-tertiary);
            padding: 16px 20px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-align: left;
        }
        
        .tokens-table td {
            padding: 16px 20px;
            vertical-align: middle;
            border-bottom: 1px solid var(--border-secondary);
        }
        
        .tokens-table tr:hover {
            background: var(--bg-hover);
        }
        
        .tokens-table tr:last-child td {
            border-bottom: none;
        }
        
        .token-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .token-symbol {
            background: var(--accent-purple);
            color: var(--bg-primary);
            padding: 4px 8px;
            border-radius: var(--radius-small);
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
        }
        
        .token-name {
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .token-address {
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 11px;
            color: var(--text-muted);
        }
        
        .balance-main {
            font-size: 16px;
            font-weight: 600;
            color: var(--accent-green);
        }
        
        .balance-raw {
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 11px;
            color: var(--text-muted);
            margin-top: 2px;
        }
        
        /* No data */
        .no-tokens {
            text-align: center;
            padding: 64px 32px;
            color: var(--text-muted);
        }
        
        .no-tokens h3 {
            margin-bottom: 12px;
            color: var(--text-secondary);
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
            .wallet-address { font-size: 14px; }
            .wallet-stats { grid-template-columns: 1fr 1fr; }
            .tokens-table { font-size: 12px; }
            .tokens-table th, .tokens-table td { padding: 12px 8px; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="header-content">
                <a href="/" class="logo">
                    🔗 HyperEVM Monitor
                </a>
                <a href="/wallet/{{ wallet.address }}" class="refresh-btn">
                    🔄 Refresh
                </a>
            </div>
        </div>
    </header>
    
    <!-- Main content -->
    <main class="main">
        <div class="container">
            <!-- Breadcrumb -->
            <div class="breadcrumb">
                <a href="/">🏠 All Addresses</a>
                <span class="breadcrumb-separator">›</span>
                <a href="/?type=wallet">👤 Wallets</a>
                <span class="breadcrumb-separator">›</span>
                <span>{{ wallet.address[:8] }}...{{ wallet.address[-6:] }}</span>
            </div>

            <!-- Wallet Header -->
            <div class="wallet-header">
                <div style="display: flex; justify-content: between; align-items: flex-start; margin-bottom: 16px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <span class="badge badge-wallet">👤 Wallet</span>
                            {% if wallet.last_token_scan %}
                                <span style="font-size: 12px; color: var(--accent-green);">
                                    ✅ Scanned
                                </span>
                            {% else %}
                                <span style="font-size: 12px; color: var(--text-muted);">
                                    ⏳ Not scanned yet
                                </span>
                            {% endif %}
                        </div>
                        <div class="wallet-address">{{ wallet.address }}</div>
                    </div>
                </div>
                
                <div class="wallet-stats">
                    <div class="stat-card">
                        <span class="stat-value">{{ "{:,}".format(wallet.token_count) }}</span>
                        <span class="stat-label">Tokens Held</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{{ "{:,}".format(wallet.last_activity_block or 0) }}</span>
                        <span class="stat-label">Last Block</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">{{ wallet.last_activity_formatted }}</span>
                        <span class="stat-label">Last Activity</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">
                            {% if wallet.last_token_scan %}
                                {{ wallet.last_token_scan[:10] }}
                            {% else %}
                                Never
                            {% endif %}
                        </span>
                        <span class="stat-label">Token Scan</span>
                    </div>
                </div>
            </div>

            <!-- Tokens Section -->
            <div class="tokens-section">
                <div class="section-header">
                    <h2 class="section-title">🪙 Token Holdings</h2>
                    <a href="#" class="rescan-btn" onclick="showRescanInfo()">
                        🔄 Rescan Tokens
                    </a>
                </div>
                
                {% if tokens %}
                <table class="tokens-table">
                    <thead>
                        <tr>
                            <th>Token</th>
                            <th>Balance</th>
                            <th>Contract Address</th>
                            <th>Last Updated</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for token in tokens %}
                        <tr>
                            <td>
                                <div class="token-info">
                                    <span class="token-symbol">{{ token.symbol }}</span>
                                    <div>
                                        <div class="token-name">{{ token.name }}</div>
                                        <div style="font-size: 11px; color: var(--text-muted);">
                                            {{ token.decimals }} decimals
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="balance-main">{{ token.balance_formatted }}</div>
                                <div class="balance-raw">{{ format_number(token.balance) }} raw</div>
                            </td>
                            <td>
                                <div class="token-address">{{ token.token_address }}</div>
                            </td>
                            <td style="font-family: 'SF Mono', Monaco, monospace; font-size: 12px;">
                                {{ token.last_updated[:16] if token.last_updated else 'N/A' }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <div class="no-tokens">
                    {% if wallet.last_token_scan %}
                        <h3>💰 No Tokens Found</h3>
                        <p>This wallet doesn't hold any ERC-20 tokens, or all balances are zero.</p>
                    {% else %}
                        <h3>🔍 Wallet Not Scanned Yet</h3>
                        <p>Run the wallet scanner to detect token holdings for this address.</p>
                        <div style="margin-top: 16px;">
                            <code style="background: var(--bg-tertiary); padding: 8px 12px; border-radius: 4px; font-size: 12px;">
                                python simple_scan_wallets.py
                            </code>
                        </div>
                    {% endif %}
                </div>
                {% endif %}
            </div>

            {% if tokens %}
            <!-- Summary -->
            <div style="margin-top: 24px; padding: 16px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: var(--radius-medium); font-size: 14px; color: var(--text-muted);">
                📊 Summary: {{ tokens|length }} token holdings found
                {% if wallet.last_token_scan %}
                    • Last scan: {{ wallet.last_token_scan[:16] }}
                {% endif %}
            </div>
            {% endif %}
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            Real-time HyperEVM blockchain monitoring | Auto-discovery & classification
        </div>
    </footer>
    
    <script>
        function showRescanInfo() {
            alert('To rescan this wallet, run:\\n\\npython simple_scan_wallets.py --test-wallet {{ wallet.address }}\\n\\nOr wait for the next full scan.');
        }
    </script>
</body>
</html>
'''


# === MIDDLEWARE ET HELPERS === #

@app.before_request
def inject_common_data():
    """Injecte les données communes dans toutes les templates"""
    g.type_stats = db.get_type_statistics()
    g.token_stats = db.get_token_statistics()


@app.template_global()
def build_pagination_url(search_term=None, filter_param=None, is_tokens=False):
    """Helper global pour construire les URLs de pagination"""
    from web.utils import URLBuilder
    return URLBuilder.build_pagination_url(search_term, filter_param, is_tokens)


def render_with_common_context(template: str, **kwargs) -> str:
    """
    Rend une template avec le contexte commun injecté
    
    Args:
        template: Template HTML à rendre
        **kwargs: Contexte supplémentaire à passer à la template
        
    Returns:
        str: HTML rendu avec le contexte complet
    """
    base_context = context_builder.build_base_context(
        g.type_stats, 
        g.token_stats
    )
    
    # Ajouter les fonctions de formatage pour rétrocompatibilité
    base_context.update({
        'format_number': format_number,
        'format_supply': format_supply,
        **kwargs
    })
    
    return render_template_string(template, **base_context)


def get_request_params() -> tuple:
    """
    Extrait et valide les paramètres de requête communs
    
    Returns:
        tuple: (page, search_term)
    """
    return pagination_helper.get_pagination_params()


# === ROUTES PRINCIPALES === #

@app.route('/')
def index():
    """
    Page principale des wallets/adresses
    Route optimisée avec validation et gestion d'erreurs
    """
    try:
        # Extraction et validation des paramètres
        page, search = get_request_params()
        address_type = validator.validate_address_type(
            request.args.get('type', '', type=str)
        )
        
        # Récupération des données depuis la base
        total_wallets = db.get_wallet_count(
            search or None, 
            address_type or None
        )
        
        wallets = db.get_wallets_page(
            page, 
            WALLETS_PER_PAGE, 
            search or None, 
            address_type or None
        )
        
        # Construction du contexte avec helper
        context = context_builder.build_wallets_context(
            wallets=wallets,
            total_wallets=total_wallets,
            page=page,
            per_page=WALLETS_PER_PAGE,
            search=search,
            address_type=address_type
        )
        
        return render_with_common_context(WALLETS_TEMPLATE, **context)
        
    except Exception as e:
        app.logger.error(f"Erreur dans index(): {e}")
        return handle_server_error(e)


@app.route('/tokens')
def tokens():
    """
    Page des tokens ERC-20
    Route optimisée avec validation et formatage automatique
    """
    try:
        # Extraction et validation des paramètres
        page, search = get_request_params()
        status = validator.validate_token_status(
            request.args.get('status', '', type=str)
        )
        
        # Récupération des données depuis la base
        total_tokens = db.get_token_count(
            search or None, 
            status or None
        )
        
        tokens_list = db.get_tokens_page(
            page, 
            WALLETS_PER_PAGE, 
            search or None, 
            status or None
        )
        
        # Construction du contexte avec helper (inclut le formatage automatique)
        context = context_builder.build_tokens_context(
            tokens=tokens_list,
            total_tokens=total_tokens,
            page=page,
            per_page=WALLETS_PER_PAGE,
            search=search,
            status=status
        )
        
        return render_with_common_context(TOKENS_TEMPLATE, **context)
        
    except Exception as e:
        app.logger.error(f"Erreur dans tokens(): {e}")
        return handle_server_error(e)


@app.route('/activity')
def activity_stats():
    """
    Page des statistiques d'activité
    Route optimisée avec gestion des données de graphiques
    """
    try:
        # Extraction des paramètres spécifiques à l'activité
        selected_date = request.args.get('date', '', type=str).strip()
        
        # Récupération des données d'activité
        available_dates = db.get_available_dates()
        
        # Sélection automatique de la première date si aucune spécifiée
        if not selected_date and available_dates:
            selected_date = available_dates[0]
        
        # Récupération des statistiques
        stats_data = []
        if selected_date:
            stats_data = db.get_activity_stats_for_date(selected_date)
        
        daily_summary = db.get_daily_summary()
        overview = db.get_activity_overview()
        
        # Construction du contexte optimisé
        context = {
            'selected_date': selected_date,
            'available_dates': available_dates,
            'stats_data': stats_data,
            'stats_data_json': json.dumps(stats_data, separators=(',', ':')),
            'daily_summary': daily_summary,
            'overview': overview
        }
        
        return render_with_common_context(ACTIVITY_TEMPLATE, **context)
        
    except Exception as e:
        app.logger.error(f"Erreur dans activity_stats(): {e}")
        return handle_server_error(e)


@app.route('/wallet/<address>')
def wallet_detail(address):
    """Page de détails d'un wallet avec ses tokens"""
    try:
        # Validation de l'adresse
        if not address or len(address) != 42 or not address.startswith('0x'):
            return render_with_common_context(
                response_helper.render_error(404, "Invalid Address", "The wallet address is not valid.")
            ), 404
        
        # Récupérer les détails du wallet
        wallet = db.get_wallet_details(address.lower())
        if not wallet:
            return render_with_common_context(
                response_helper.render_error(404, "Wallet Not Found", "This wallet address was not found in the database.")
            ), 404
        
        # Récupérer les tokens du wallet
        tokens = db.get_wallet_tokens(address.lower())
        
        # Contexte pour le template
        context = {
            'wallet': wallet,
            'tokens': tokens,
            'format_number': format_number
        }
        
        return render_template_string(WALLET_DETAIL_TEMPLATE, **context)
        
    except Exception as e:
        app.logger.error(f"Erreur dans wallet_detail({address}): {e}")
        return handle_server_error(e)


# === API ENDPOINTS === #

@app.route('/api/stats')
def api_stats():
    """
    API endpoint pour les statistiques
    Retourne un JSON optimisé des statistiques principales
    """
    try:
        stats_response = response_helper.build_api_response(
            success=True,
            data={
                'type_stats': g.type_stats,
                'token_stats': g.token_stats,
                'overview': db.get_activity_overview(),
                'timestamp': formatter.format_number(
                    int(time.time())
                )
            }
        )
        return jsonify(stats_response)
        
    except Exception as e:
        app.logger.error(f"Erreur dans api_stats(): {e}")
        error_response = response_helper.build_api_response(
            success=False,
            error=str(e)
        )
        return jsonify(error_response), 500


@app.route('/api/scan-stats')
def api_scan_stats():
    """API endpoint pour les statistiques de scan"""
    try:
        stats = db.get_wallet_scan_stats()
        return jsonify({
            'success': True,
            'data': stats,
            'timestamp': int(time.time())
        })
    except Exception as e:
        app.logger.error(f"Erreur dans api_scan_stats(): {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/wallet/<address>')
def api_wallet_detail(address):
    """API endpoint pour les détails d'un wallet"""
    try:
        # Validation de l'adresse
        if not address or len(address) != 42 or not address.startswith('0x'):
            return jsonify({
                'success': False,
                'error': 'Invalid wallet address format'
            }), 400
        
        # Récupérer les détails du wallet
        wallet = db.get_wallet_details(address.lower())
        if not wallet:
            return jsonify({
                'success': False,
                'error': 'Wallet not found'
            }), 404
        
        # Récupérer les tokens du wallet
        tokens = db.get_wallet_tokens(address.lower())
        
        return jsonify({
            'success': True,
            'data': {
                'wallet': wallet,
                'tokens': tokens,
                'token_count': len(tokens)
            },
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        app.logger.error(f"Erreur dans api_wallet_detail({address}): {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/debug/templates')
def debug_templates():
    """
    Route de debug pour vérifier le chargement des templates
    Utile pour le développement et le diagnostic
    """
    try:
        from web.templates import get_template_info
        
        debug_info = {
            'status': 'Templates loaded successfully',
            'template_info': get_template_info(),
            'available_templates': [
                'WALLETS_TEMPLATE',
                'TOKENS_TEMPLATE', 
                'ACTIVITY_TEMPLATE',
                'WALLET_DETAIL_TEMPLATE'
            ],
            'helpers_loaded': [
                'PaginationHelper',
                'ValidationHelper',
                'DataFormatter',
                'TemplateContextBuilder',
                'ResponseHelper'
            ],
            'new_features': [
                'Wallet detail pages',
                'Token holdings display',
                'Scanner integration',
                'API endpoints for wallets'
            ],
            'routes_available': [
                '/ - Main wallet list',
                '/tokens - Token list',
                '/activity - Activity stats',
                '/wallet/<address> - Wallet details',
                '/api/stats - General stats API',
                '/api/scan-stats - Scanner stats API',
                '/api/wallet/<address> - Wallet API'
            ]
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        app.logger.error(f"Erreur dans debug_templates(): {e}")
        return jsonify({'error': str(e)}), 500


# === GESTION D'ERREURS === #

def handle_server_error(error):
    """Gestionnaire d'erreur serveur centralisé"""
    error_html = response_helper.render_error(
        500,
        WebConstants.ERROR_MESSAGES['server_error'],
        WebConstants.ERROR_MESSAGES['server_error_desc']
    )
    return render_with_common_context(error_html), 500


@app.errorhandler(404)
def not_found(error):
    """Page d'erreur 404 personnalisée"""
    error_html = response_helper.render_error(
        404,
        WebConstants.ERROR_MESSAGES['not_found'],
        WebConstants.ERROR_MESSAGES['not_found_desc']
    )
    return render_with_common_context(error_html), 404


@app.errorhandler(500) 
def server_error(error):
    """Page d'erreur 500 personnalisée"""
    app.logger.error(f"Erreur serveur 500: {error}")
    return handle_server_error(error)


# === FACTORY ET CONFIGURATION === #

def create_app() -> Flask:
    """
    Factory pour créer l'application Flask
    Utile pour les tests et le déploiement
    
    Returns:
        Flask: Instance configurée de l'application
    """
    return app


def configure_logging():
    """Configure le logging pour l'application"""
    import logging
    
    if not app.debug:
        # Configuration pour la production
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s'
        )
        app.logger.setLevel(logging.INFO)
        app.logger.info('HyperEVM Viewer startup')


# === POINT D'ENTRÉE PRINCIPAL === #

def main():
    """
    Lance le serveur web avec configuration optimisée
    Point d'entrée principal de l'application
    """
    configure_logging()
    
    # Messages de démarrage optimisés
    print("🚀 " + MESSAGES['web_start'])
    print("✅ Templates modulaires chargés")
    print("🔧 Code refactorisé avec helpers")
    print("📊 Gestion d'erreurs améliorée")
    print("🔗 Scanner de wallets intégré")
    print()
    print(f"🌙 Interface: http://{WEB_HOST}:{WEB_PORT}")
    print(f"📖 Wallets: http://{WEB_HOST}:{WEB_PORT}")
    print(f"🪙 Tokens: http://{WEB_HOST}:{WEB_PORT}/tokens")
    print(f"📈 Activity: http://{WEB_HOST}:{WEB_PORT}/activity")
    print(f"👤 Wallet details: http://{WEB_HOST}:{WEB_PORT}/wallet/<address>")
    print(f"🔧 API Stats: http://{WEB_HOST}:{WEB_PORT}/api/stats")
    print(f"📊 Scan Stats: http://{WEB_HOST}:{WEB_PORT}/api/scan-stats")
    print(f"🔍 Debug: http://{WEB_HOST}:{WEB_PORT}/debug/templates")
    print("🛑 Stop: Ctrl+C")
    
    try:
        # Configuration optimisée pour production
        app.run(
            debug=False,
            host=WEB_HOST,
            port=WEB_PORT,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print(f"\n✅ {MESSAGES['web_stop']}")
        app.logger.info('HyperEVM Viewer stopped gracefully')
    except Exception as e:
        print(f"❌ Erreur serveur: {e}")
        app.logger.error(f"Erreur critique: {e}")


if __name__ == '__main__':
    main()
