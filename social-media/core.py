"""
Core SocialMediaCollector - Main orchestrator for the social-media collection layer
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from .collectors import HybridCollector
from .processors import (
    PostClassifier, 
    PostNormalizer, 
    TunisianSentimentAnalyzer,
    BotDetectorAdvanced
)
from .storage import StorageBackend, SQLiteStorage
from .schemas import PostSchema, CollectionStatsSchema
from .config import get_settings
from .exceptions import CollectionError, StorageError

logger = logging.getLogger(__name__)


class SocialMediaCollector:
    """
    Main collector orchestrator
    Coordinates collection, processing, and storage
    """
    
    def __init__(self, 
                 storage: Optional[StorageBackend] = None,
                 settings=None):
        """
        Initialize collector
        
        Args:
            storage: Storage backend (defaults to SQLite)
            settings: Configuration (defaults to env/config.py)
        """
        self.settings = settings or get_settings()
        self.storage = storage or SQLiteStorage(self.settings.storage.database_url)
        
        # Initialize components
        self.hybrid_collector = HybridCollector()
        self.classifier = PostClassifier()
        self.normalizer = PostNormalizer()
        self.sentiment_analyzer = TunisianSentimentAnalyzer()
        self.bot_detector = BotDetectorAdvanced()
        
        self.logger = logging.getLogger("behaviorlens.core")
        
        # Collection tracking
        self.is_collecting = False
        self.last_collection_time: Optional[datetime] = None
        self.collection_stats: Optional[CollectionStatsSchema] = None
    
    async def initialize(self):
        """Initialize storage and components"""
        try:
            await self.storage.initialize()
            self.logger.info("SocialMediaCollector initialized")
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            raise
    
    async def collect(self, 
                     platforms: Optional[List[str]] = None,
                     max_posts: Optional[int] = None,
                     process: bool = True,
                     store: bool = True) -> CollectionStatsSchema:
        """
        Collect posts from all configured sources
        
        Args:
            platforms: Specific platforms to collect from (None = all)
            max_posts: Maximum posts to collect
            process: Whether to apply classification and processing
            store: Whether to persist to storage
            
        Returns:
            Collection statistics
        """
        if self.is_collecting:
            raise CollectionError("Collection already in progress")
        
        self.is_collecting = True
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting collection...")
            
            # Collect raw posts
            raw_posts = await self.hybrid_collector.collect(
                platforms=platforms,
                max_total=max_posts or self.settings.max_posts_per_run
            )
            self.logger.info(f"Collected {len(raw_posts)} raw posts")
            
            # Process posts
            processed_posts = raw_posts
            if process:
                processed_posts = await self._process_posts(raw_posts)
                self.logger.info(f"Processed {len(processed_posts)} posts")
            
            # Store posts
            stored_count = 0
            if store:
                stored_count = await self.storage.save_posts(processed_posts)
                self.logger.info(f"Stored {stored_count} new posts")
            
            # Get statistics
            duration = (datetime.utcnow() - start_time).total_seconds()
            stats = await self._generate_stats(
                len(raw_posts), stored_count, duration
            )
            
            self.last_collection_time = datetime.utcnow()
            self.collection_stats = stats
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Collection error: {e}", exc_info=True)
            raise
        finally:
            self.is_collecting = False
    
    async def _process_posts(self, posts: List[PostSchema]) -> List[PostSchema]:
        """
        Process posts with classification and enrichment
        
        Steps:
        1. Normalize text
        2. Deduplicate
        3. Classify post type, sentiment, language
        4. Detect Tunisian content
        5. Detect bots
        6. Enrich with metadata
        """
        processed = []
        
        for post in posts:
            try:
                # Normalize
                normalized_post = self.normalizer.normalize_post(post.model_dump())
                
                # Check for duplicates
                if self.normalizer.is_duplicate(normalized_post.get("text", "")):
                    self.logger.debug(f"Skipping duplicate: {normalized_post['text'][:50]}...")
                    continue
                
                # Classify
                classification = self.classifier.classify_post(
                    normalized_post.get("text", ""),
                    normalized_post.get("source", "unknown")
                )
                
                # Update with classification
                normalized_post.update(classification)
                
                # Advanced sentiment analysis
                sentiment_result = self.sentiment_analyzer.analyze(
                    normalized_post.get("text", ""),
                    language=classification.get("language")
                )
                normalized_post["sentiment"] = sentiment_result.get("sentiment")
                
                # Bot detection
                bot_score, bot_details = self.bot_detector.detect_bot_score(normalized_post)
                normalized_post["bot_score"] = bot_score
                normalized_post["bot_details"] = bot_details
                
                # Reconstruct PostSchema
                post_data = {
                    "source": normalized_post["source"],
                    "url": normalized_post["url"],
                    "post_id": normalized_post["post_id"],
                    "author": normalized_post["author"],
                    "text": normalized_post["text"],
                    "media_type": normalized_post.get("media_type", "text"),
                    "likes": normalized_post.get("likes", 0),
                    "shares": normalized_post.get("shares", 0),
                    "comments_count": normalized_post.get("comments_count", 0),
                    "post_type": normalized_post.get("post_type"),
                    "sentiment": normalized_post.get("sentiment"),
                    "language": normalized_post.get("language"),
                    "is_tunisian": normalized_post.get("is_tunisian", False),
                    "tunisian_score": normalized_post.get("tunisian_score", 0.0),
                    "hashtags": normalized_post.get("hashtags", []),
                    "mentions": normalized_post.get("mentions", []),
                    "entities": normalized_post.get("entities", {}),
                    "created_at": normalized_post.get("created_at"),
                    "scraped_at": normalized_post.get("scraped_at"),
                }
                
                processed_post = PostSchema(**post_data)
                processed.append(processed_post)
                
                # Register as seen for future deduplication
                self.normalizer.register_post(post.text, post.post_id)
                
            except Exception as e:
                self.logger.error(f"Error processing post: {e}")
                continue
        
        return processed
    
    async def _generate_stats(self, total_collected: int, 
                             total_stored: int,
                             duration: float) -> CollectionStatsSchema:
        """Generate collection statistics"""
        storage_stats = await self.storage.get_stats()
        
        return CollectionStatsSchema(
            total_posts=total_collected,
            total_comments=total_stored,  # Approximation
            posts_by_source=storage_stats.get("posts_by_source", {}),
            posts_by_sentiment=storage_stats.get("posts_by_sentiment", {}),
            posts_by_type=storage_stats.get("posts_by_type", {}),
            tunisian_posts=storage_stats.get("tunisian_posts", 0),
            avg_tunisian_score=0.0,  # Can be computed from actual scores
            collection_duration_seconds=duration,
        )
    
    async def get_posts(self, filters: Optional[Dict[str, Any]] = None,
                       limit: int = 50, offset: int = 0) -> List[PostSchema]:
        """Retrieve posts from storage"""
        return await self.storage.get_posts(filters, limit, offset)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics"""
        return await self.storage.get_stats()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all components"""
        collector_health = await self.hybrid_collector.health_check()
        
        return {
            "status": collector_health.get("status"),
            "message": collector_health.get("message"),
            "collectors": collector_health.get("collectors", {}),
            "last_collection": self.last_collection_time.isoformat() if self.last_collection_time else None,
            "is_collecting": self.is_collecting,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def cleanup(self, days: int = 30):
        """Clean up old data"""
        await self.storage.delete_old_posts(days)
    
    async def close(self):
        """Close all connections"""
        await self.storage.close()
        self.logger.info("SocialMediaCollector closed")


# Global collector instance
_collector: Optional[SocialMediaCollector] = None


async def get_collector() -> SocialMediaCollector:
    """Get or create global collector instance"""
    global _collector
    if _collector is None:
        _collector = SocialMediaCollector()
        await _collector.initialize()
    return _collector


async def initialize_collector():
    """Initialize global collector"""
    collector = await get_collector()
    return collector
