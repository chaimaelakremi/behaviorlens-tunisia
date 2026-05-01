"""
BehaviorLens Social Media Collection Layer
Complete production-grade modular system for multi-platform social media data collection
"""

__version__ = "2.0.0"
__author__ = "BehaviorLens Team"

from .core import SocialMediaCollector, get_collector, initialize_collector
from .collectors import HybridCollector
from .processors import (
    PostClassifier,
    PostNormalizer,
    TunisianSentimentAnalyzer,
    BotDetectorAdvanced,
)
from .storage import StorageBackend, SQLiteStorage
from .schemas import PostSchema, CommentSchema, CollectionStatsSchema
from .config import get_settings, Settings
from .exceptions import (
    SocialMediaCollectorError,
    ConfigurationError,
    CollectionError,
    AuthenticationError,
    RateLimitError,
    StorageError,
    ValidationError,
)

__all__ = [
    "SocialMediaCollector",
    "get_collector",
    "initialize_collector",
    "HybridCollector",
    "PostClassifier",
    "PostNormalizer",
    "TunisianSentimentAnalyzer",
    "BotDetectorAdvanced",
    "StorageBackend",
    "SQLiteStorage",
    "PostSchema",
    "CommentSchema",
    "CollectionStatsSchema",
    "get_settings",
    "Settings",
    "SocialMediaCollectorError",
    "ConfigurationError",
    "CollectionError",
    "AuthenticationError",
    "RateLimitError",
    "StorageError",
    "ValidationError",
]
