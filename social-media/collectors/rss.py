"""
RSS feed collector for news aggregation
"""

import asyncio
import aiohttp
import feedparser
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from .base import BaseCollector
from ..schemas import PostSchema
from ..exceptions import CollectionError

logger = logging.getLogger(__name__)


class RSSCollector(BaseCollector):
    """Collector for RSS feeds"""
    
    def __init__(self, feeds: List[str], config: Dict[str, Any]):
        """
        Initialize RSS collector
        
        Args:
            feeds: List of RSS feed URLs
            config: Configuration dictionary
        """
        super().__init__("rss", config)
        self.feeds = feeds
        self.timeout = config.get("timeout_seconds", 15)
    
    async def collect(self) -> List[PostSchema]:
        """Collect posts from RSS feeds"""
        posts = []
        
        try:
            await self.on_start()
            
            tasks = [self._collect_feed(feed) for feed in self.feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    await self.on_error(result)
                else:
                    posts.extend(result)
            
            self.logger.info(f"Collected {len(posts)} posts from RSS feeds")
            
        finally:
            await self.on_stop()
        
        return posts
    
    async def _collect_feed(self, feed_url: str) -> List[PostSchema]:
        """Collect posts from a single RSS feed"""
        posts = []
        
        try:
            # Parse feed
            feed_data = await asyncio.to_thread(self._fetch_feed, feed_url)
            
            for entry in feed_data.get("entries", [])[:25]:  # Limit to 25 entries
                post = self._parse_entry(entry, feed_url)
                if post:
                    posts.append(post)
        except Exception as e:
            self.logger.error(f"Error collecting from feed {feed_url}: {e}")
        
        return posts
    
    def _fetch_feed(self, feed_url: str) -> Dict[str, Any]:
        """Fetch and parse RSS feed"""
        feed = feedparser.parse(feed_url)
        
        if feed.bozo and isinstance(feed.bozo_exception, Exception):
            self.logger.warning(f"Feed parse warning: {feed.bozo_exception}")
        
        return feed
    
    def _parse_entry(self, entry: Dict[str, Any], feed_url: str) -> Optional[PostSchema]:
        """Parse RSS entry to PostSchema"""
        try:
            # Extract date
            published = entry.get("published_parsed")
            if published:
                created_at = datetime(*published[:6])
            else:
                created_at = datetime.utcnow()
            
            # Get content
            content = entry.get("summary", entry.get("description", ""))
            title = entry.get("title", "")
            text = f"{title}\n{content}" if title else content
            
            # Get link
            link = entry.get("link", feed_url)
            
            post = PostSchema(
                source="rss",
                url=link,
                post_id=entry.get("id", link),
                author=entry.get("author", "Unknown"),
                text=text,
                media_type="text",
                created_at=created_at,
                scraped_at=datetime.utcnow(),
            )
            
            return self._validate_post(post.model_dump())
        except Exception as e:
            self.logger.error(f"Error parsing RSS entry: {e}")
            return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Check RSS feed connectivity"""
        if not self.feeds:
            return {
                "status": "error",
                "message": "No RSS feeds configured",
                "details": {}
            }
        
        try:
            # Try to fetch first feed
            feed_data = await asyncio.to_thread(
                self._fetch_feed, self.feeds[0]
            )
            
            if not feed_data.get("entries"):
                return {
                    "status": "degraded",
                    "message": "Feed accessible but contains no entries",
                    "details": {"feed": self.feeds[0]}
                }
            
            return {
                "status": "healthy",
                "message": "RSS feeds accessible",
                "details": {
                    "feeds_configured": len(self.feeds),
                    "first_feed_entries": len(feed_data.get("entries", []))
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"RSS collection failed: {e}",
                "details": {}
            }
