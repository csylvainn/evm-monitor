# detection/__init__.py
"""
Detection components for addresses and tokens
"""

from .address_classifier import AddressClassifier
from .token_detector import TokenDetector

__all__ = [
    'AddressClassifier',
    'TokenDetector'
]