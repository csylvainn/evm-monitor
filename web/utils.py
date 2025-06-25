"""
Utilitaires optimisés pour l'interface web HyperEVM
Version professionnelle avec gestion d'erreurs et documentation complète
"""

import math
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from flask import request

# Configuration du logger
logger = logging.getLogger(__name__)


class PaginationHelper:
    """
    Helper optimisé pour la gestion de la pagination
    Fournit des méthodes statiques pour extraire, valider et construire 
    les paramètres de pagination
    """
    
    DEFAULT_PAGE = 1
    DEFAULT_WINDOW = 5
    
    @staticmethod
    def get_pagination_params() -> Tuple[int, str]:
        """
        Extrait et valide les paramètres de pagination depuis la requête Flask
        
        Returns:
            Tuple[int, str]: (page_number, search_term) validés
        """
        try:
            page = max(
                PaginationHelper.DEFAULT_PAGE, 
                request.args.get('page', PaginationHelper.DEFAULT_PAGE, type=int)
            )
            search = request.args.get('search', '', type=str).strip()
            return page, search
        except Exception as e:
            logger.warning(f"Erreur lors de l'extraction des paramètres de pagination: {e}")
            return PaginationHelper.DEFAULT_PAGE, ""
    
    @staticmethod
    def build_page_numbers(
        current_page: int, 
        total_pages: int, 
        window: int = DEFAULT_WINDOW
    ) -> List[int]:
        """
        Génère la liste des numéros de page pour l'affichage de la pagination
        
        Args:
            current_page: Page actuelle
            total_pages: Nombre total de pages
            window: Fenêtre de pages à afficher autour de la page actuelle
            
        Returns:
            List[int]: Liste des numéros de page à afficher
        """
        if total_pages <= 0:
            return [1]
            
        start_page = max(1, current_page - window)
        end_page = min(total_pages, current_page + window)
        
        return list(range(start_page, end_page + 1))
    
    @staticmethod
    def build_context(page: int, total_items: int, per_page: int) -> Dict[str, Any]:
        """
        Construit le contexte de pagination complet pour les templates
        
        Args:
            page: Numéro de page actuel
            total_items: Nombre total d'éléments
            per_page: Nombre d'éléments par page
            
        Returns:
            Dict[str, Any]: Contexte de pagination complet
        """
        if total_items <= 0 or per_page <= 0:
            return {
                'current_page': 1,
                'total_pages': 1,
                'page_numbers': [1],
                'has_prev': False,
                'has_next': False,
                'prev_page': 1,
                'next_page': 1,
            }
        
        total_pages = math.ceil(total_items / per_page)
        safe_page = max(1, min(page, total_pages))
        
        return {
            'current_page': safe_page,
            'total_pages': total_pages,
            'page_numbers': PaginationHelper.build_page_numbers(safe_page, total_pages),
            'has_prev': safe_page > 1,
            'has_next': safe_page < total_pages,
            'prev_page': max(1, safe_page - 1),
            'next_page': min(total_pages, safe_page + 1),
        }


class URLBuilder:
    """
    Helper pour construire les URLs de navigation et pagination
    Centralise la logique de construction des paramètres URL
    """
    
    @staticmethod
    def build_pagination_url(
        search_term: Optional[str] = None, 
        filter_param: Optional[str] = None, 
        is_tokens: bool = False
    ) -> str:
        """
        Construit l'URL de base pour la pagination avec paramètres
        
        Args:
            search_term: Terme de recherche à inclure
            filter_param: Paramètre de filtre (type ou status)
            is_tokens: True si c'est pour la page tokens (utilise 'status' au lieu de 'type')
            
        Returns:
            str: Base URL avec paramètres pour la pagination
        """
        params = []
        
        if search_term and search_term.strip():
            params.append(f"search={search_term.strip()}")
        
        if filter_param and filter_param.strip():
            param_name = "status" if is_tokens else "type"
            params.append(f"{param_name}={filter_param.strip()}")
        
        if params:
            return f"?{'&'.join(params)}&"
        else:
            return "?"
    
    @staticmethod
    def build_filter_url(base_path: str, **filters) -> str:
        """
        Construit une URL avec filtres pour navigation
        
        Args:
            base_path: Chemin de base (ex: '/tokens')
            **filters: Filtres à appliquer
            
        Returns:
            str: URL complète avec filtres
        """
        if not filters:
            return base_path
        
        params = [f"{k}={v}" for k, v in filters.items() if v]
        return f"{base_path}?{'&'.join(params)}" if params else base_path


class DataFormatter:
    """
    Helper pour le formatage des données d'affichage
    Fournit des méthodes de formatage cohérentes et réutilisables
    """
    
    @staticmethod
    def format_number(value: Union[str, int, float]) -> str:
        """
        Formate un nombre avec des séparateurs de milliers
        
        Args:
            value: Valeur numérique à formater
            
        Returns:
            str: Nombre formaté avec séparateurs
        """
        try:
            if isinstance(value, str):
                # Tentative de conversion string vers nombre
                if '.' in value:
                    num = float(value)
                else:
                    num = int(value)
            else:
                num = value
            
            if isinstance(num, float):
                return f"{num:,.2f}"
            else:
                return f"{num:,}"
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Impossible de formater le nombre '{value}': {e}")
            return str(value)
    
    @staticmethod
    def format_supply(supply_str: str, decimals: int) -> str:
        """
        Formate le totalSupply d'un token avec les décimales appropriées
        
        Args:
            supply_str: Supply total en string
            decimals: Nombre de décimales du token
            
        Returns:
            str: Supply formaté de manière lisible (K, M, B)
        """
        try:
            supply = int(supply_str)
            
            if decimals > 0:
                # Ajustement pour les décimales
                formatted = supply / (10 ** decimals)
                
                # Formatage en unités lisibles
                if formatted >= 1_000_000_000:
                    return f"{formatted/1_000_000_000:.1f}B"
                elif formatted >= 1_000_000:
                    return f"{formatted/1_000_000:.1f}M"
                elif formatted >= 1_000:
                    return f"{formatted/1_000:.1f}K"
                else:
                    return f"{formatted:.2f}"
            else:
                # Pas de décimales, formatage direct
                return DataFormatter.format_number(supply)
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Impossible de formater le supply '{supply_str}': {e}")
            return supply_str
    
    @staticmethod
    def format_address(address: str, start: int = 6, end: int = 4) -> str:
        """
        Formate une adresse pour l'affichage mobile en la tronquant
        
        Args:
            address: Adresse complète
            start: Nombre de caractères à garder au début
            end: Nombre de caractères à garder à la fin
            
        Returns:
            str: Adresse formatée (ex: 0x1234...abcd)
        """
        if not address or len(address) <= start + end:
            return address
        
        return f"{address[:start]}...{address[-end:]}"
    
    @staticmethod
    def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
        """
        Calcule un pourcentage avec gestion des erreurs
        
        Args:
            part: Partie du total
            total: Total de référence
            
        Returns:
            float: Pourcentage calculé, arrondi à 1 décimale
        """
        try:
            if total <= 0:
                return 0.0
            return round((part / total) * 100, 1)
        except (TypeError, ZeroDivisionError):
            return 0.0
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Formate une taille de fichier en unités lisibles
        
        Args:
            size_bytes: Taille en bytes
            
        Returns:
            str: Taille formatée (ex: 1.5 MB)
        """
        try:
            if size_bytes <= 0:
                return "0 B"
            
            units = ['B', 'KB', 'MB', 'GB', 'TB']
            index = min(int(math.log(size_bytes, 1024)), len(units) - 1)
            size = size_bytes / (1024 ** index)
            
            return f"{size:.1f} {units[index]}"
        except (ValueError, TypeError):
            return str(size_bytes)


class ValidationHelper:
    """
    Helper pour la validation des paramètres de requête
    Centralise la logique de validation et nettoyage des entrées
    """
    
    # Constantes de validation
    VALID_ADDRESS_TYPES = ['', 'wallet', 'contract', 'unknown']
    VALID_TOKEN_STATUSES = ['', 'detected', 'failed']
    MAX_SEARCH_LENGTH = 255
    MIN_PAGE_SIZE = 1
    MAX_PAGE_SIZE = 1000
    
    @staticmethod
    def validate_address_type(address_type: str) -> str:
        """
        Valide et nettoie le type d'adresse
        
        Args:
            address_type: Type d'adresse depuis la requête
            
        Returns:
            str: Type d'adresse validé ou chaîne vide si invalide
        """
        if not isinstance(address_type, str):
            return ''
        
        cleaned = address_type.strip().lower()
        return cleaned if cleaned in ValidationHelper.VALID_ADDRESS_TYPES else ''
    
    @staticmethod
    def validate_token_status(status: str) -> str:
        """
        Valide et nettoie le statut de token
        
        Args:
            status: Statut depuis la requête
            
        Returns:
            str: Statut validé ou chaîne vide si invalide
        """
        if not isinstance(status, str):
            return ''
        
        cleaned = status.strip().lower()
        return cleaned if cleaned in ValidationHelper.VALID_TOKEN_STATUSES else ''
    
    @staticmethod
    def validate_page(page: Any) -> int:
        """
        Valide et nettoie le numéro de page
        
        Args:
            page: Numéro de page depuis la requête
            
        Returns:
            int: Numéro de page validé (minimum 1)
        """
        try:
            return max(ValidationHelper.MIN_PAGE_SIZE, int(page))
        except (ValueError, TypeError):
            return ValidationHelper.MIN_PAGE_SIZE
    
    @staticmethod
    def validate_search_term(search: str) -> str:
        """
        Valide et nettoie un terme de recherche
        
        Args:
            search: Terme de recherche depuis la requête
            
        Returns:
            str: Terme de recherche nettoyé et tronqué si nécessaire
        """
        if not isinstance(search, str):
            return ''
        
        # Nettoyage et troncature
        cleaned = search.strip()
        if len(cleaned) > ValidationHelper.MAX_SEARCH_LENGTH:
            cleaned = cleaned[:ValidationHelper.MAX_SEARCH_LENGTH]
            logger.info(f"Terme de recherche tronqué à {ValidationHelper.MAX_SEARCH_LENGTH} caractères")
        
        return cleaned
    
    @staticmethod
    def validate_page_size(per_page: Any) -> int:
        """
        Valide la taille de page pour la pagination
        
        Args:
            per_page: Nombre d'éléments par page
            
        Returns:
            int: Taille de page validée dans les limites acceptables
        """
        try:
            size = int(per_page)
            return max(
                ValidationHelper.MIN_PAGE_SIZE, 
                min(ValidationHelper.MAX_PAGE_SIZE, size)
            )
        except (ValueError, TypeError):
            return 25  # Valeur par défaut raisonnable


class TemplateContextBuilder:
    """
    Helper pour construire les contextes de template de manière cohérente
    Centralise la logique de préparation des données pour l'affichage
    """
    
    @staticmethod
    def build_base_context(type_stats: Dict, token_stats: Dict) -> Dict[str, Any]:
        """
        Construit le contexte de base pour toutes les pages
        
        Args:
            type_stats: Statistiques par type d'adresse
            token_stats: Statistiques des tokens
            
        Returns:
            Dict[str, Any]: Contexte de base avec helpers de formatage
        """
        return {
            'type_stats': type_stats or {},
            'token_stats': token_stats or {},
            'format_number': DataFormatter.format_number,
            'format_supply': DataFormatter.format_supply,
            'format_address': DataFormatter.format_address,
            'calculate_percentage': DataFormatter.calculate_percentage,
        }
    
    @staticmethod
    def build_wallets_context(
        wallets: List, 
        total_wallets: int, 
        page: int, 
        per_page: int, 
        search: str, 
        address_type: str
    ) -> Dict[str, Any]:
        """
        Construit le contexte pour la page des wallets
        
        Args:
            wallets: Liste des wallets à afficher
            total_wallets: Nombre total de wallets
            page: Page actuelle
            per_page: Éléments par page
            search: Terme de recherche
            address_type: Type d'adresse filtré
            
        Returns:
            Dict[str, Any]: Contexte complet pour la template wallets
        """
        context = {
            'wallets': wallets or [],
            'total_wallets': total_wallets,
            'search_term': search,
            'current_type': address_type,
        }
        
        # Ajout de la pagination
        pagination_context = PaginationHelper.build_context(page, total_wallets, per_page)
        context.update(pagination_context)
        
        return context
    
    @staticmethod
    def build_tokens_context(
        tokens: List, 
        total_tokens: int, 
        page: int, 
        per_page: int, 
        search: str, 
        status: str
    ) -> Dict[str, Any]:
        """
        Construit le contexte pour la page des tokens avec formatage automatique
        
        Args:
            tokens: Liste des tokens à afficher
            total_tokens: Nombre total de tokens
            page: Page actuelle
            per_page: Éléments par page
            search: Terme de recherche
            status: Statut filtré
            
        Returns:
            Dict[str, Any]: Contexte complet pour la template tokens
        """
        # Formatage automatique des tokens
        formatted_tokens = []
        for token in (tokens or []):
            token_copy = token.copy() if hasattr(token, 'copy') else dict(token)
            token_copy['total_supply_formatted'] = DataFormatter.format_supply(
                str(token_copy.get('total_supply', '0')), 
                int(token_copy.get('decimals', 0))
            )
            formatted_tokens.append(token_copy)
        
        context = {
            'tokens': formatted_tokens,
            'total_tokens': total_tokens,
            'search_term': search,
            'current_status': status,
        }
        
        # Ajout de la pagination
        pagination_context = PaginationHelper.build_context(page, total_tokens, per_page)
        context.update(pagination_context)
        
        return context


class ResponseHelper:
    """
    Helper pour les réponses HTTP et gestion d'erreurs
    Fournit des méthodes pour créer des réponses cohérentes
    """
    
    @staticmethod
    def render_error(error_code: int, title: str, message: str) -> str:
        """
        Génère une page d'erreur stylée et cohérente
        
        Args:
            error_code: Code d'erreur HTTP
            title: Titre de l'erreur
            message: Message descriptif
            
        Returns:
            str: HTML de la page d'erreur
        """
        return f'''
        <div class="no-data">
            <h3>{title}</h3>
            <p>{message}</p>
            <div style="margin-top: 16px;">
                <a href="/" class="btn btn-primary">← Back to Home</a>
                <a href="javascript:history.back()" class="btn btn-secondary" style="margin-left: 8px;">↶ Go Back</a>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: var(--text-muted);">
                Error Code: {error_code}
            </div>
        </div>
        '''
    
    @staticmethod
    def build_api_response(
        success: bool, 
        data: Any = None, 
        error: str = None,
        message: str = None
    ) -> Dict[str, Any]:
        """
        Construit une réponse API standardisée
        
        Args:
            success: Indicateur de succès
            data: Données à retourner en cas de succès
            error: Message d'erreur en cas d'échec
            message: Message informatif optionnel
            
        Returns:
            Dict[str, Any]: Réponse API structurée
        """
        response = {
            'success': success,
            'timestamp': DataFormatter.format_number(int(__import__('time').time()))
        }
        
        if success:
            if data is not None:
                response['data'] = data
            if message:
                response['message'] = message
        else:
            if error:
                response['error'] = error
                logger.error(f"API Error: {error}")
        
        return response


# === CLASSES DE CONFIGURATION === #

class StyleConfig:
    """Configuration du style et des couleurs pour l'interface"""
    
    # Couleurs du dark mode
    COLORS = {
        'primary': '#58a6ff',
        'success': '#3fb950',
        'warning': '#d29922',
        'danger': '#f85149',
        'info': '#a5a5f5',
        'secondary': '#8b949e',
    }
    
    # Tailles et dimensions
    SIZES = {
        'container_max_width': '1400px',
        'mobile_breakpoint': '768px',
        'pagination_window': 5,
        'max_items_per_page': 100,
    }
    
    # Animations et transitions
    ANIMATIONS = {
        'transition_fast': '0.15s',
        'transition_normal': '0.2s',
        'transition_slow': '0.3s',
    }


class WebHelperFactory:
    """
    Factory pour créer et configurer les helpers web
    Permet une instanciation centralisée et cohérente
    """
    
    _instances = {}
    
    @classmethod
    def get_pagination_helper(cls) -> PaginationHelper:
        """Retourne une instance singleton de PaginationHelper"""
        if 'pagination' not in cls._instances:
            cls._instances['pagination'] = PaginationHelper()
        return cls._instances['pagination']
    
    @classmethod
    def get_url_builder(cls) -> URLBuilder:
        """Retourne une instance singleton de URLBuilder"""
        if 'url_builder' not in cls._instances:
            cls._instances['url_builder'] = URLBuilder()
        return cls._instances['url_builder']
    
    @classmethod
    def get_data_formatter(cls) -> DataFormatter:
        """Retourne une instance singleton de DataFormatter"""
        if 'formatter' not in cls._instances:
            cls._instances['formatter'] = DataFormatter()
        return cls._instances['formatter']
    
    @classmethod
    def get_validator(cls) -> ValidationHelper:
        """Retourne une instance singleton de ValidationHelper"""
        if 'validator' not in cls._instances:
            cls._instances['validator'] = ValidationHelper()
        return cls._instances['validator']
    
    @classmethod
    def get_context_builder(cls) -> TemplateContextBuilder:
        """Retourne une instance singleton de TemplateContextBuilder"""
        if 'context_builder' not in cls._instances:
            cls._instances['context_builder'] = TemplateContextBuilder()
        return cls._instances['context_builder']
    
    @classmethod
    def get_response_helper(cls) -> ResponseHelper:
        """Retourne une instance singleton de ResponseHelper"""
        if 'response_helper' not in cls._instances:
            cls._instances['response_helper'] = ResponseHelper()
        return cls._instances['response_helper']


# === INSTANCES PUBLIQUES POUR RÉTROCOMPATIBILITÉ === #

# Instances globales pour utilisation directe (pattern singleton léger)
pagination_helper = PaginationHelper()
url_builder = URLBuilder()
data_formatter = DataFormatter()
validator = ValidationHelper()
context_builder = TemplateContextBuilder()
response_helper = ResponseHelper()

# Export des classes et instances principales
__all__ = [
    'PaginationHelper',
    'URLBuilder', 
    'DataFormatter',
    'ValidationHelper',
    'TemplateContextBuilder',
    'ResponseHelper',
    'StyleConfig',
    'WebHelperFactory',
    'pagination_helper',
    'url_builder',
    'data_formatter', 
    'validator',
    'context_builder',
    'response_helper'
]