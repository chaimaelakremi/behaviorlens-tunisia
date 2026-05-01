"""
Abstract storage backend interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..schemas import PostSchema, CommentSchema


class StorageBackend(ABC):
    """Abstract base class for storage implementations"""
    
    @abstractmethod
    async def initialize(self):
        """Initialize storage (create tables, connections, etc.)"""
        pass
    
    @abstractmethod
    async def save_post(self, post: PostSchema) -> bool:
        """
        Save a single post
        
        Returns:
            True if saved, False if duplicate
        """
        pass
    
    @abstractmethod
    async def save_posts(self, posts: List[PostSchema]) -> int:
        """
        Save multiple posts
        
        Returns:
            Number of posts saved
        """
        pass
    
    @abstractmethod
    async def get_posts(self, filters: Dict[str, Any] = None, 
                       limit: int = 50, offset: int = 0) -> List[PostSchema]:
        """
        Retrieve posts with optional filters
        
        Filters:
            - source: Filter by platform
            - post_type: Filter by post type
            - sentiment: Filter by sentiment
            - is_tunisian: Filter by Tunisian relevance
            - language: Filter by language
            - date_from: Posts after this date
            - date_to: Posts before this date
        """
        pass
    
    @abstractmethod
    async def get_post(self, post_id: str) -> Optional[PostSchema]:
        """Retrieve a single post by ID"""
        pass
    
    @abstractmethod
    async def save_comment(self, post_id: str, comment: CommentSchema) -> bool:
        """Save a comment for a post"""
        pass
    
    @abstractmethod
    async def get_comments(self, post_id: str) -> List[CommentSchema]:
        """Get comments for a post"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics
        
        Returns:
            Dict with:
            - total_posts
            - total_comments
            - posts_by_source
            - posts_by_sentiment
            - posts_by_type
            - posts_by_language
            - tunisian_posts_count
            - posts_last_24h
        """
        pass
    
    @abstractmethod
    async def delete_old_posts(self, days: int):
        """Delete posts older than specified days"""
        pass
    
    @abstractmethod
    async def close(self):
        """Close storage connection"""
        pass
