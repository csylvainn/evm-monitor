"""
Configuration centralisée pour l'interface web HyperEVM
Centralise toutes les constantes et paramètres de configuration
"""

import os
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PaginationConfig:
    """Configuration pour la pagination"""
    DEFAULT_PAGE: int = 1
    DEFAULT_WINDOW: int = 5
    MIN_PAGE_SIZE: int = 1
    MAX_PAGE_SIZE: int = 1000
    DEFAULT_PER_PAGE: int = 25


@dataclass 
class ValidationConfig:
    """Configuration pour la validation des entrées"""
    MAX_SEARCH_LENGTH: int = 255
    VALID_ADDRESS_TYPES: tuple = ('', 'wallet', 'contract', 'unknown')
    VALID_TOKEN_STATUSES: tuple = ('', 'detected', 'failed')
    VALID_ENDPOINTS: tuple = ('tokens', 'activity_stats')


@dataclass
class UIConfig:
    """Configuration de l'interface utilisateur"""
    CONTAINER_MAX_WIDTH: str = '1400px'
    MOBILE_BREAKPOINT: str = '768px'
    ANIMATION_FAST: str = '0.15s'
    ANIMATION_NORMAL: str = '0.2s'
    ANIMATION_SLOW: str = '0.3s'


class WebConstants:
    """Constantes principales pour l'interface web"""
    
    # Configuration de pagination
    PAGINATION = PaginationConfig()
    
    # Configuration de validation
    VALIDATION = ValidationConfig()
    
    # Configuration UI
    UI = UIConfig()
    
    # Messages d'erreur standardisés
    ERROR_MESSAGES = {
        'not_found': "🚫 Page Not Found",
        'server_error': "⚠️ Server Error",
        'database_error': "💾 Database Error",
        'validation_error': "⚠️ Validation Error",
        'not_found_desc': "The page you're looking for doesn't exist.",
        'server_error_desc': "Something went wrong. Please try again later.",
        'database_error_desc': "Unable to connect to the database.",
        'validation_error_desc': "Invalid parameters provided."
    }
    
    # Messages de succès
    SUCCESS_MESSAGES = {
        'data_loaded': "✅ Data loaded successfully",
        'operation_complete': "✅ Operation completed",
        'templates_loaded': "✅ Templates loaded successfully"
    }
    
    # Configuration des couleurs (dark mode GitHub-inspired)
    COLORS = {
        'primary': '#58a6ff',
        'primary_hover': '#4493f8', 
        'success': '#3fb950',
        'success_hover': '#2ea043',
        'warning': '#d29922',
        'danger': '#f85149',
        'info': '#a5a5f5',
        'secondary': '#8b949e',
        'muted': '#656d76',
        
        # Backgrounds
        'bg_primary': '#0d1117',
        'bg_secondary': '#161b22',
        'bg_tertiary': '#21262d',
        'bg_hover': '#30363d',
        
        # Borders
        'border_primary': '#30363d',
        'border_secondary': '#21262d',
        'border_muted': '#484f58',
        
        # Text
        'text_primary': '#f0f6fc',
        'text_secondary': '#8b949e',
        'text_muted': '#656d76',
    }
    
    # Configuration des endpoints et routes
    ROUTES = {
        'home': '/',
        'tokens': '/tokens',
        'activity': '/activity',
        'api_stats': '/api/stats',
        'debug_templates': '/debug/templates'
    }
    
    # Configuration des templates
    TEMPLATES = {
        'cache_timeout': 300,  # 5 minutes
        'enable_auto_reload': False,
        'strict_undefined': True
    }
    
    # Configuration de logging
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s %(name)s %(levelname)s: %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S'
    }


class EnvironmentConfig:
    """Configuration basée sur les variables d'environnement"""
    
    @staticmethod
    def get_debug_mode() -> bool:
        """Détermine si l'application est en mode debug"""
        return os.getenv('FLASK_ENV', 'production').lower() in ['development', 'debug']
    
    @staticmethod
    def get_log_level() -> str:
        """Détermine le niveau de logging"""
        return os.getenv('LOG_LEVEL', 'INFO').upper()
    
    @staticmethod
    def get_max_content_length() -> int:
        """Taille maximale du contenu des requêtes"""
        return int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB par défaut
    
    @staticmethod
    def get_secret_key() -> str:
        """Clé secrète pour Flask (si nécessaire)"""
        return os.getenv('SECRET_KEY', 'hyperevm-dev-key-change-in-prod')
    
    @staticmethod
    def get_database_pool_size() -> int:
        """Taille du pool de connexions DB"""
        return int(os.getenv('DB_POOL_SIZE', '10'))


class PerformanceConfig:
    """Configuration pour les optimisations de performance"""
    
    # Pagination optimisée
    MAX_ITEMS_PER_PAGE = 100
    DEFAULT_ITEMS_PER_PAGE = 25
    
    # Cache
    CACHE_TIMEOUT_SHORT = 60    # 1 minute
    CACHE_TIMEOUT_MEDIUM = 300  # 5 minutes
    CACHE_TIMEOUT_LONG = 3600   # 1 heure
    
    # Limites de requêtes
    MAX_SEARCH_RESULTS = 10000
    MAX_CONCURRENT_REQUESTS = 100
    
    # Timeouts
    DATABASE_TIMEOUT = 30       # 30 secondes
    REQUEST_TIMEOUT = 60        # 1 minute
    
    # Compression
    ENABLE_GZIP = True
    MIN_SIZE_FOR_GZIP = 1024    # 1KB


class SecurityConfig:
    """Configuration de sécurité"""
    
    # Headers de sécurité
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Validation des entrées
    ALLOWED_SEARCH_CHARS = r'^[a-zA-Z0-9\s\-_.@]+$'
    MAX_SEARCH_TERMS = 10
    
    # Rate limiting (si implémenté)
    RATE_LIMIT_PER_MINUTE = 60
    RATE_LIMIT_PER_HOUR = 1000


def get_app_config() -> Dict[str, Any]:
    """
    Retourne la configuration complète de l'application
    
    Returns:
        Dict[str, Any]: Configuration Flask complète
    """
    config = {
        # Configuration Flask de base
        'DEBUG': EnvironmentConfig.get_debug_mode(),
        'SECRET_KEY': EnvironmentConfig.get_secret_key(),
        'MAX_CONTENT_LENGTH': EnvironmentConfig.get_max_content_length(),
        
        # Configuration JSON
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': EnvironmentConfig.get_debug_mode(),
        
        # Configuration des templates
        'TEMPLATES_AUTO_RELOAD': EnvironmentConfig.get_debug_mode(),
        
        # Configuration custom
        'WEB_CONSTANTS': WebConstants,
        'PERFORMANCE': PerformanceConfig,
        'SECURITY': SecurityConfig,
    }
    
    return config


def get_startup_info() -> Dict[str, Any]:
    """
    Retourne les informations de démarrage pour le logging
    
    Returns:
        Dict[str, Any]: Informations de démarrage
    """
    return {
        'debug_mode': EnvironmentConfig.get_debug_mode(),
        'log_level': EnvironmentConfig.get_log_level(),
        'max_content_length': EnvironmentConfig.get_max_content_length(),
        'pagination_config': {
            'default_per_page': WebConstants.PAGINATION.DEFAULT_PER_PAGE,
            'max_per_page': WebConstants.PAGINATION.MAX_PAGE_SIZE
        },
        'performance_config': {
            'cache_timeout': PerformanceConfig.CACHE_TIMEOUT_MEDIUM,
            'max_search_results': PerformanceConfig.MAX_SEARCH_RESULTS
        }
    }


# Export des configurations principales
__all__ = [
    'WebConstants',
    'EnvironmentConfig', 
    'PerformanceConfig',
    'SecurityConfig',
    'PaginationConfig',
    'ValidationConfig',
    'UIConfig',
    'get_app_config',
    'get_startup_info'
]