"""
Base collector interface for social media platforms
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ..schemas import PostSchema

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """Abstract base class for all collectors"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize collector
        
        Args:
            name: Collector name (facebook, instagram, tiktok, etc.)
            config: Configuration dictionary
        """
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", False)
        self.logger = logging.getLogger(f"behaviorlens.{name}")
    
    @abstractmethod
    async def collect(self) -> List[PostSchema]:
        """
        Collect posts from platform
        
        Returns:
            List of PostSchema objects
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check collector health
        
        Returns:
            Health status dict with keys: status (healthy/degraded/error), message, details
        """
        pass
    
    def _validate_post(self, post: Dict[str, Any]) -> Optional[PostSchema]:
        """
        Validate and convert post dict to PostSchema
        
        Args:
            post: Post data dictionary
            
        Returns:
            PostSchema or None if invalid
        """
        try:
            # Ensure required fields
            if not post.get("source") or not post.get("url") or not post.get("text"):
                self.logger.warning(f"Missing required fields in post: {post}")
                return None
            
            return PostSchema(**post)
        except Exception as e:
            self.logger.error(f"Error validating post: {e}")
            return None
    
    async def on_start(self):
        """Called when collection starts"""
        self.logger.info(f"Starting {self.name} collector")
    
    async def on_stop(self):
        """Called when collection stops"""
        self.logger.info(f"Stopping {self.name} collector")
    
    async def on_error(self, error: Exception):
        """Called when an error occurs"""
        self.logger.error(f"Error in {self.name} collector: {error}", exc_info=True)
