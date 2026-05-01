"""
RSS Feeds Collector
Fetches news from RSS feeds
"""

import feedparser
from datetime import datetime
from typing import List, Dict
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSCollector:
    """Collects data from RSS feeds (news sources)"""
    
    def __init__(self, feeds_config: Dict):
        self.feeds = feeds_config
        self.collected_posts = []
    
    def collect_from_feed(self, feed_name: str, feed_url: str) -> List[Dict]:
        """
        Fetch posts from a single RSS feed
        
        Args:
            feed_name: identifier for the feed
            feed_url: URL of the RSS feed
        
        Returns:
            List of normalized post dictionaries
        """
        try:
            logger.info(f"📰 Fetching RSS feed: {feed_name}")
            feed = feedparser.parse(feed_url)
            
            if not feed.entries:
                logger.warning(f"  No entries found in {feed_name}")
                return []
            
            posts = []
            
            for entry in feed.entries[:50]:  # Limit to 50 per feed
                try:
                    post = {
                        "id": f"rss_{feed_name}_{entry.get('id', entry.get('link', ''))}",
                        "text": self._clean_text(
                            entry.get('title', ''),
                            entry.get('summary', '')
                        ),
                        "source": "rss",
                        "platform": feed_name,
                        "author": entry.get('author', 'News Source'),
                        "timestamp": self._parse_date(entry.get('published', '')),
                        "url": entry.get('link', ''),
                        "metadata": {
                            "category": "general",
                            "language": "en",
                            "confidence": 0.9
                        }
                    }
                    
                    if post["text"]:  # Only add if text exists
                        posts.append(post)
                
                except Exception as e:
                    logger.debug(f"  Skipping entry: {str(e)}")
                    continue
            
            logger.info(f"  ✅ Collected {len(posts)} posts from {feed_name}")
            return posts
        
        except Exception as e:
            logger.error(f"❌ Error fetching {feed_name}: {str(e)}")
            return []
    
    def collect_all(self) -> List[Dict]:
        """
        Collect from all configured feeds
        
        Returns:
            All collected posts from all feeds
        """
        all_posts = []
        
        logger.info(f"Starting RSS collection from {len(self.feeds)} feeds...")
        
        for feed_name, feed_config in self.feeds.items():
            posts = self.collect_from_feed(feed_name, feed_config["url"])
            all_posts.extend(posts)
        
        self.collected_posts = all_posts
        logger.info(f"✅ RSS Collection complete: {len(all_posts)} total posts")
        
        return all_posts
    
    @staticmethod
    def _clean_text(title: str, summary: str) -> str:
        """
        Clean and combine title + summary
        
        Args:
            title: article title
            summary: article summary
        
        Returns:
            Clean combined text
        """
        text = f"{title} {summary}".strip()
        
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Truncate to 500 characters
        return text[:500]
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """
        Parse date to ISO format
        
        Args:
            date_str: date string from RSS entry
        
        Returns:
            ISO format datetime string
        """
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()


# USAGE EXAMPLE
if __name__ == "__main__":
    from config import RSS_FEEDS
    
    collector = RSSCollector(RSS_FEEDS)
    posts = collector.collect_all()
    
    print(f"\n{'='*60}")
    print(f"Collected {len(posts)} RSS posts")
    print(f"{'='*60}")
    
    for post in posts[:3]:
        print(f"\n📰 {post['platform'].upper()}")
        print(f"   Text: {post['text'][:100]}...")
        print(f"   Source: {post['author']}")
        print(f"   URL: {post['url'][:50]}...")
