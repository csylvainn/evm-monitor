"""
Configuration globale pour HyperEVM Monitor
"""

# Configuration des RPC (par ordre de priorité)
RPC_ENDPOINTS = [
    {"name": "dRPC", "url": "https://hyperliquid.drpc.org", "priority": 1},
    {"name": "1RPC", "url": "https://1rpc.io/hyperliquid", "priority": 2},
    {"name": "Hyperliquid Official", "url": "https://rpc.hyperliquid.xyz/evm", "priority": 3},
]

# Configuration du monitoring
CHECK_INTERVAL = 15  # secondes
BATCH_SIZE = 25      # blocs par batch
TOKEN_TIMEOUT = 10   # timeout pour les appels token en secondes

# Configuration de la base de données
DB_PATH = "wallets.db"

# Configuration web
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
WALLETS_PER_PAGE = 50

# Configuration des timeouts
RPC_TIMEOUT = 15     # timeout standard pour les appels RPC
RPC_TEST_TIMEOUT = 10  # timeout pour les tests de RPC

# Configuration retry
RPC_MAX_FAILURES = 3  # nombre max d'échecs avant switch RPC
RPC_RETEST_INTERVAL = 300  # 5 minutes entre les retests
UPDATE_UNKNOWN_INTERVAL = 20  # cycles entre les mises à jour des types inconnus

# ERC-20 Token Detection
ERC20_FUNCTIONS = {
    'name': '0x06fdde03',
    'symbol': '0x95d89b41', 
    'decimals': '0x313ce567',
    'totalSupply': '0x18160ddd'
}

# Configuration de recherche du créateur
CREATOR_SEARCH_BLOCKS = 1000  # nombre de blocs à chercher en arrière
CREATOR_SEARCH_STEP = 10      # pas de recherche

# Messages d'interface
MESSAGES = {
    'monitor_start': "🤖 HYPEREVM SMART MONITOR",
    'monitor_desc': "🔄 Auto-switch RPC + détection wallet/contrat + tokens ERC-20 + stats d'activité",
    'web_start': "🌐 Starting HyperEVM wallet viewer...",
    'web_stop': "🛑 Server stopped"
}