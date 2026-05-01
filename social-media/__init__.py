"""
Social Media Intelligence Collection System
Part of BehaviorLens - Real-time Tunisian social insight platform

This module provides a complete social media data collection system
using multiple legal data sources and the unified media collection architecture.
"""

__version__ = "1.0.0"
__author__ = "BehaviorLens Team"

from .app import SocialMediaCollector
from .config import SOCIAL_MEDIA_CONFIG

__all__ = ["SocialMediaCollector", "SOCIAL_MEDIA_CONFIG"]
