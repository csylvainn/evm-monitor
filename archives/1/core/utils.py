"""
Fonctions utilitaires partagées pour HyperEVM Monitor
"""

from datetime import datetime
from typing import Any


def get_time_slot(timestamp: int) -> str:
    """Convertit un timestamp en tranche de 5min (ex: 14h03 → '14:00')"""
    dt = datetime.fromtimestamp(timestamp)
    minutes = (dt.minute // 5) * 5
    return dt.replace(minute=minutes, second=0, microsecond=0).strftime('%H:%M')


def get_date_from_timestamp(timestamp: int) -> str:
    """Convertit timestamp en date (ex: '2025-06-18')"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')


def format_number(value: Any) -> str:
    """Formate un nombre avec séparateurs"""
    try:
        if isinstance(value, str):
            num = int(value)
        else:
            num = value
        return f"{num:,}"
    except:
        return str(value)


def format_supply(supply_str: str, decimals: int) -> str:
    """Formate le totalSupply avec decimals"""
    try:
        supply = int(supply_str)
        if decimals > 0:
            formatted = supply / (10 ** decimals)
            if formatted >= 1000000:
                return f"{formatted/1000000:.1f}M"
            elif formatted >= 1000:
                return f"{formatted/1000:.1f}K"
            else:
                return f"{formatted:.2f}"
        else:
            return format_number(supply)
    except:
        return supply_str


def format_timestamp(timestamp: int) -> str:
    """Formate un timestamp en date lisible"""
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return 'N/A'


def safe_hex_to_int(hex_str: str) -> int:
    """Convertit une string hex en int de façon sécurisée"""
    try:
        return int(hex_str, 16) if hex_str and hex_str != "0x" else 0
    except:
        return 0


def truncate_address(address: str, start: int = 6, end: int = 4) -> str:
    """Tronque une adresse pour l'affichage (ex: 0x1234...abcd)"""
    if len(address) <= start + end:
        return address
    return f"{address[:start]}...{address[-end:]}"


def validate_ethereum_address(address: str) -> bool:
    """Valide une adresse Ethereum"""
    if not address or not isinstance(address, str):
        return False
    
    # Retirer le préfixe 0x s'il existe
    if address.startswith('0x'):
        address = address[2:]
    
    # Vérifier la longueur (40 caractères hex)
    if len(address) != 40:
        return False
    
    # Vérifier que ce sont des caractères hexadécimaux
    try:
        int(address, 16)
        return True
    except ValueError:
        return False


def calculate_percentage(part: int, total: int) -> float:
    """Calcule un pourcentage de façon sécurisée"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def bytes_to_string(hex_bytes: str) -> str:
    """Convertit des bytes hex en string"""
    try:
        # Retirer 0x si présent
        if hex_bytes.startswith('0x'):
            hex_bytes = hex_bytes[2:]
        
        # Convertir en bytes puis en string
        return bytes.fromhex(hex_bytes).decode('utf-8').rstrip('\x00')
    except:
        return ""


def is_contract_creation(tx: dict) -> bool:
    """Vérifie si une transaction est une création de contrat"""
    return tx.get("to") is None and tx.get("from") is not None


def extract_contract_address_from_receipt(receipt: dict) -> str:
    """Extrait l'adresse de contrat d'un receipt"""
    return receipt.get("contractAddress", "") if receipt else ""


class PerformanceTimer:
    """Timer simple pour mesurer les performances"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Démarre le timer"""
        self.start_time = datetime.now()
        return self
    
    def stop(self):
        """Arrête le timer"""
        self.end_time = datetime.now()
        return self
    
    def elapsed(self) -> float:
        """Retourne le temps écoulé en secondes"""
        if not self.start_time:
            return 0.0
        
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def elapsed_ms(self) -> float:
        """Retourne le temps écoulé en millisecondes"""
        return self.elapsed() * 1000


def create_progress_bar(current: int, total: int, width: int = 30) -> str:
    """Crée une barre de progression textuelle"""
    if total == 0:
        return "[" + "=" * width + "]"
    
    progress = current / total
    filled = int(width * progress)
    bar = "=" * filled + "-" * (width - filled)
    return f"[{bar}] {progress:.1%}"