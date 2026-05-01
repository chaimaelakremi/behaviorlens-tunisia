"""Collectors module"""

from .base import BaseCollector
from .graph_api import GraphAPICollector
from .rss import RSSCollector
from .playwright import PlaywrightCollector
from .hybrid import HybridCollector

__all__ = [
    "BaseCollector",
    "GraphAPICollector",
    "RSSCollector",
    "PlaywrightCollector",
    "HybridCollector",
]
