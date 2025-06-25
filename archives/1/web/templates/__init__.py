"""
Module de templates HyperEVM - Version professionnelle et modulaire
Organisation centralisée des templates avec système de validation et debug
Version 3.0 - Architecture clean et maintenable
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

# Import des templates depuis leurs fichiers séparés
try:
    from .base import BASE_TEMPLATE
    from .wallets import WALLETS_TEMPLATE
    from .tokens import TOKENS_TEMPLATE
    from .activity import ACTIVITY_TEMPLATE
    
    _TEMPLATES_LOADED = True
    _IMPORT_ERRORS = []
    
except ImportError as e:
    _TEMPLATES_LOADED = False
    _IMPORT_ERRORS = [str(e)]
    
    # Templates par défaut en cas d'erreur
    BASE_TEMPLATE = "<!-- Template de base non disponible -->"
    WALLETS_TEMPLATE = "<!-- Template wallets non disponible -->"
    TOKENS_TEMPLATE = "<!-- Template tokens non disponible -->"
    ACTIVITY_TEMPLATE = "<!-- Template activity non disponible -->"

# Configuration du logger
logger = logging.getLogger(__name__)

# Métadonnées du module
__version__ = "3.0.0"
__description__ = "HyperEVM Monitor Templates - Modular & Professional Architecture"
__author__ = "HyperEVM Team"
__status__ = "Production"

# Export des templates
__all__ = [
    'BASE_TEMPLATE',
    'WALLETS_TEMPLATE',
    'TOKENS_TEMPLATE', 
    'ACTIVITY_TEMPLATE',
    'get_template_info',
    'validate_templates',
    'get_template_stats',
    'list_available_templates',
    'check_template_health'
]


class TemplateInfo:
    """Classe pour gérer les informations des templates"""
    
    TEMPLATE_METADATA = {
        'base': {
            'name': 'Base Template',
            'description': 'Template de base avec dark mode GitHub-inspired',
            'features': ['Dark mode', 'Responsive design', 'Navigation', 'CSS moderne'],
            'blocks': ['title', 'extra_styles', 'content', 'scripts', 'refresh_url', 'footer_text'],
            'dependencies': []
        },
        'wallets': {
            'name': 'Wallets Template', 
            'description': 'Template pour l\'affichage des adresses et wallets',
            'features': ['Pagination', 'Recherche', 'Filtrage par type', 'Tableaux responsives'],
            'blocks': ['content'],
            'dependencies': ['base']
        },
        'tokens': {
            'name': 'Tokens Template',
            'description': 'Template pour l\'affichage des tokens ERC-20',
            'features': ['Formatage automatique', 'Filtrage par statut', 'Supply formaté'],
            'blocks': ['content'], 
            'dependencies': ['base']
        },
        'activity': {
            'name': 'Activity Template',
            'description': 'Template pour les statistiques avec Chart.js',
            'features': ['Graphiques interactifs', 'Chart.js', 'Sélection de dates', 'Cartes overview'],
            'blocks': ['content', 'scripts'],
            'dependencies': ['base', 'Chart.js CDN']
        }
    }
    
    FIXES_APPLIED = [
        'Résolution du problème "block extra_styles defined twice"',
        'Séparation claire CSS (extra_styles) et JavaScript (scripts)', 
        'Organisation modulaire en fichiers séparés',
        'Architecture professionnelle avec helpers',
        'Gestion d\'erreurs et validation améliorées',
        'Code documentation et maintenabilité',
        'Optimisation des performances et du cache'
    ]
    
    ARCHITECTURE_BENEFITS = [
        'Maintenabilité: Chaque template dans son fichier',
        'Réutilisabilité: Helpers et composants modulaires',
        'Testabilité: Code organisé et découplé',
        'Évolutivité: Ajout facile de nouveaux templates',
        'Performance: Optimisations CSS et JavaScript',
        'Sécurité: Validation et sanitisation des entrées'
    ]


def get_template_info() -> Dict[str, Any]:
    """
    Retourne les informations complètes sur les templates chargés
    
    Returns:
        Dict[str, Any]: Informations détaillées des templates
    """
    return {
        'version': __version__,
        'description': __description__,
        'status': __status__,
        'templates_loaded': _TEMPLATES_LOADED,
        'import_errors': _IMPORT_ERRORS,
        'templates': TemplateInfo.TEMPLATE_METADATA,
        'fixes_applied': TemplateInfo.FIXES_APPLIED,
        'architecture_benefits': TemplateInfo.ARCHITECTURE_BENEFITS,
        'total_templates': len(TemplateInfo.TEMPLATE_METADATA),
        'file_structure': {
            'base.py': 'Template de base avec CSS et structure',
            'wallets.py': 'Template pour les wallets et adresses',
            'tokens.py': 'Template pour les tokens ERC-20', 
            'activity.py': 'Template pour les statistiques d\'activité',
            '__init__.py': 'Module principal avec exports et validation'
        }
    }


def validate_templates() -> Dict[str, Any]:
    """
    Valide la cohérence et l'intégrité des templates
    
    Returns:
        Dict[str, Any]: Résultats de validation
    """
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'template_checks': {}
    }
    
    # Vérification de l'import des templates
    if not _TEMPLATES_LOADED:
        validation_results['valid'] = False
        validation_results['errors'].extend(_IMPORT_ERRORS)
        return validation_results
    
    # Vérification de chaque template
    templates_to_check = {
        'BASE_TEMPLATE': BASE_TEMPLATE,
        'WALLETS_TEMPLATE': WALLETS_TEMPLATE, 
        'TOKENS_TEMPLATE': TOKENS_TEMPLATE,
        'ACTIVITY_TEMPLATE': ACTIVITY_TEMPLATE
    }
    
    for template_name, template_content in templates_to_check.items():
        checks = {
            'exists': bool(template_content and template_content.strip()),
            'min_length': len(template_content) > 100,
            'has_html': '<html' in template_content.lower(),
            'has_blocks': '{% block' in template_content,
        }
        
        # Vérifications spécifiques
        if template_name == 'BASE_TEMPLATE':
            checks.update({
                'has_doctype': '<!DOCTYPE html>' in template_content,
                'has_meta_charset': 'charset=' in template_content,
                'has_viewport': 'viewport' in template_content,
                'has_css_vars': '--bg-primary' in template_content
            })
        elif template_name == 'ACTIVITY_TEMPLATE':
            checks.update({
                'has_chart_js': 'Chart.js' in template_content,
                'has_scripts_block': '{% block scripts %}' in template_content,
                'no_extra_styles_conflict': template_content.count('{% block extra_styles %}') <= 1
            })
        
        # Vérification des erreurs
        template_valid = all(checks.values())
        if not template_valid:
            validation_results['valid'] = False
            failed_checks = [check for check, result in checks.items() if not result]
            validation_results['errors'].append(
                f"{template_name}: Échec des vérifications {failed_checks}"
            )
        
        validation_results['template_checks'][template_name] = checks
    
    # Vérifications globales
    try:
        # Vérification de la cohérence entre templates
        if 'BASE_TEMPLATE' in locals() and BASE_TEMPLATE:
            if '{% block content %}{% endblock %}' not in BASE_TEMPLATE:
                validation_results['warnings'].append(
                    "Le BASE_TEMPLATE ne contient pas le block content standard"
                )
    
    except Exception as e:
        validation_results['errors'].append(f"Erreur lors de la validation: {e}")
        validation_results['valid'] = False
    
    return validation_results


def get_template_stats() -> Dict[str, Any]:
    """
    Retourne les statistiques détaillées des templates
    
    Returns:
        Dict[str, Any]: Statistiques des templates
    """
    stats = {
        'templates_count': 0,
        'total_size_chars': 0,
        'average_size': 0,
        'templates_details': {},
        'blocks_summary': {},
        'dependencies_graph': {}
    }
    
    if not _TEMPLATES_LOADED:
        return stats
    
    templates = {
        'base': BASE_TEMPLATE,
        'wallets': WALLETS_TEMPLATE,
        'tokens': TOKENS_TEMPLATE,
        'activity': ACTIVITY_TEMPLATE
    }
    
    # Calcul des statistiques
    for name, template in templates.items():
        if template:
            size = len(template)
            stats['templates_count'] += 1
            stats['total_size_chars'] += size
            
            # Analyse des blocks
            blocks = []
            lines = template.split('\n')
            for line in lines:
                if '{% block' in line and 'endblock' not in line:
                    block_name = line.split('{% block')[1].split('%}')[0].strip()
                    blocks.append(block_name)
            
            stats['templates_details'][name] = {
                'size_chars': size,
                'size_kb': round(size / 1024, 2),
                'lines': len(lines),
                'blocks': blocks,
                'blocks_count': len(blocks),
                'metadata': TemplateInfo.TEMPLATE_METADATA.get(name, {})
            }
    
    # Calcul de la moyenne
    if stats['templates_count'] > 0:
        stats['average_size'] = round(stats['total_size_chars'] / stats['templates_count'])
        stats['total_size_kb'] = round(stats['total_size_chars'] / 1024, 2)
    
    # Résumé des blocks
    all_blocks = []
    for template_info in stats['templates_details'].values():
        all_blocks.extend(template_info['blocks'])
    
    for block in set(all_blocks):
        stats['blocks_summary'][block] = all_blocks.count(block)
    
    return stats


def list_available_templates() -> List[str]:
    """
    Retourne la liste des templates disponibles
    
    Returns:
        List[str]: Noms des templates disponibles
    """
    if not _TEMPLATES_LOADED:
        return []
    
    available = []
    templates_to_check = [
        ('BASE_TEMPLATE', BASE_TEMPLATE),
        ('WALLETS_TEMPLATE', WALLETS_TEMPLATE),
        ('TOKENS_TEMPLATE', TOKENS_TEMPLATE), 
        ('ACTIVITY_TEMPLATE', ACTIVITY_TEMPLATE)
    ]
    
    for name, template in templates_to_check:
        if template and template.strip() and len(template) > 100:
            available.append(name)
    
    return available


def check_template_health() -> Dict[str, Any]:
    """
    Vérifie la santé globale du système de templates
    
    Returns:
        Dict[str, Any]: Rapport de santé complet
    """
    health_report = {
        'overall_status': 'healthy',
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'checks': {},
        'recommendations': [],
        'summary': {}
    }
    
    try:
        # Vérification de base
        health_report['checks']['templates_loaded'] = _TEMPLATES_LOADED
        health_report['checks']['import_errors'] = len(_IMPORT_ERRORS) == 0
        
        # Validation des templates
        validation = validate_templates()
        health_report['checks']['validation_passed'] = validation['valid']
        
        # Statistiques
        stats = get_template_stats()
        health_report['checks']['templates_available'] = stats['templates_count'] >= 4
        health_report['checks']['reasonable_size'] = stats.get('total_size_kb', 0) < 1000  # < 1MB
        
        # Vérification des dépendances
        available_templates = list_available_templates()
        health_report['checks']['all_templates_available'] = len(available_templates) >= 4
        
        # Détermination du statut global
        all_checks_passed = all(health_report['checks'].values())
        if not all_checks_passed:
            if not _TEMPLATES_LOADED or not validation['valid']:
                health_report['overall_status'] = 'critical'
            else:
                health_report['overall_status'] = 'warning'
        
        # Recommandations
        if not _TEMPLATES_LOADED:
            health_report['recommendations'].append(
                "Vérifier les imports des templates et corriger les erreurs"
            )
        
        if not validation['valid']:
            health_report['recommendations'].append(
                "Corriger les erreurs de validation des templates"
            )
        
        if stats.get('total_size_kb', 0) > 500:
            health_report['recommendations'].append(
                "Considérer l'optimisation de la taille des templates"
            )
        
        # Résumé
        health_report['summary'] = {
            'templates_count': stats.get('templates_count', 0),
            'total_size_kb': stats.get('total_size_kb', 0),
            'validation_errors': len(validation.get('errors', [])),
            'import_errors': len(_IMPORT_ERRORS)
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de santé: {e}")
        health_report['overall_status'] = 'critical'
        health_report['checks']['health_check_error'] = str(e)
    
    return health_report


# Log de démarrage si les templates sont chargés avec succès
if _TEMPLATES_LOADED:
    logger.info(f"Templates HyperEVM chargés avec succès - Version {__version__}")
else:
    logger.error(f"Erreur de chargement des templates: {_IMPORT_ERRORS}")

# Validation automatique au chargement (en mode debug uniquement)
try:
    import os
    if os.getenv('FLASK_ENV', '').lower() in ['development', 'debug']:
        validation_result = validate_templates()
        if not validation_result['valid']:
            logger.warning(f"Problèmes de validation détectés: {validation_result['errors']}")
except Exception:
    pass  # Ignorer les erreurs de validation au chargement