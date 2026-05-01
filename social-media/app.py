"""
Social Media Collection Application
Main entry point for social media intelligence gathering
"""

import json
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.media_collection import MediaCollectionPipeline
from backend.media_collection.normalizer import DataNormalizer
from backend.media_collection.storage import StorageManager

from .config import (
    SOCIAL_MEDIA_CONFIG,
    DATA_FILES,
    COLLECTION_SETTINGS,
    TOPIC_CATEGORIES,
    SENTIMENT_KEYWORDS,
    LANGUAGE_SETTINGS,
    MONITORED_HASHTAGS,
    BOT_DETECTION,
    get_config_summary,
)
from .utils import (
    setup_logging,
    generate_id,
    extract_hashtags,
    extract_mentions,
    detect_sentiment,
    detect_language,
    detect_bot_behavior,
)
from .graph_api_collector import FacebookInstagramGraphAPICollector

# Setup logging
logger = setup_logging()


class SocialMediaCollector:
    """
    Unified Social Media Collection System
    
    Collects data from multiple social media platforms and sources,
    normalizes to unified schema, and stores for analysis.
    """
    
    def __init__(self):
        """Initialize the social media collector"""
        self.config = SOCIAL_MEDIA_CONFIG
        self.settings = COLLECTION_SETTINGS
        self.media_pipeline = MediaCollectionPipeline()
        self.storage = StorageManager(data_file=DATA_FILES["processed"])
        self.raw_storage = StorageManager(data_file=DATA_FILES["raw"])
        
        # Initialize Graph API collector (optional, requires credentials)
        self.graph_api_collector = FacebookInstagramGraphAPICollector()
        
        logger.info("Social Media Collector initialized")
        logger.info(f"Config: {get_config_summary()}")
        
        if self.graph_api_collector.enabled:
            logger.info("✓ Graph API credentials found - official API collection enabled")
        else:
            logger.info("ℹ️  Graph API not configured - using RSS/public feeds only")
    
    def collect_from_all_sources(self) -> List[Dict[str, Any]]:
        """
        Collect data from all enabled social media sources
        
        Returns:
            List of normalized posts from all sources
        """
        logger.info("Starting collection from all social media sources")
        
        all_posts = []
        
        # Collect from each enabled platform
        for platform_name, platform_config in self.config.items():
            if platform_config.get("enabled", False):
                try:
                    logger.info(f"Collecting from {platform_name}...")
                    posts = self.collect_from_platform(platform_name)
                    all_posts.extend(posts)
                    logger.info(f"✓ Collected {len(posts)} posts from {platform_name}")
                except Exception as e:
                    logger.error(f"✗ Error collecting from {platform_name}: {e}")
                    continue
        
        logger.info(f"Total posts collected: {len(all_posts)}")
        return all_posts
    
    def collect_from_platform(self, platform_name: str) -> List[Dict[str, Any]]:
        """
        Collect from a specific social media platform
        
        Args:
            platform_name: Name of the platform
            
        Returns:
            List of posts from that platform
        """
        platform_config = self.config.get(platform_name, {})
        platform = platform_config.get("platform")
        
        posts = []
        
        try:
            if platform_name == "twitter_rss":
                posts = self._collect_twitter_rss(platform_config)
            elif platform_name == "facebook_pages":
                posts = self._collect_facebook_pages(platform_config)
            elif platform_name == "facebook_graph_api":
                posts = self._collect_facebook_graph_api(platform_config)
            elif platform_name == "instagram_hashtags":
                posts = self._collect_instagram_hashtags(platform_config)
            elif platform_name == "instagram_graph_api":
                posts = self._collect_instagram_graph_api(platform_config)
            elif platform_name == "tiktok_trends":
                posts = self._collect_tiktok_trends(platform_config)
            elif platform_name == "reddit_communities":
                posts = self._collect_reddit_communities(platform_config)
            else:
                logger.warning(f"Unknown platform: {platform_name}")
                return []
            
            # Normalize all posts
            normalized_posts = self._normalize_posts(posts, platform)
            return normalized_posts
            
        except Exception as e:
            logger.error(f"Error collecting from {platform_name}: {e}")
            return []
    
    def _collect_twitter_rss(self, config: Dict) -> List[Dict]:
        """Collect from Twitter trending topics via RSS"""
        logger.debug("Collecting from Twitter (RSS mode)")
        
        # Use the media pipeline's RSS collector
        from backend.media_collection.sources.rss_collector import RSSCollector
        
        rss_config = {url: {"category": "social_media"} for url in config.get("urls", [])}
        collector = RSSCollector(rss_config)
        posts = collector.collect_all()
        
        logger.debug(f"Collected {len(posts)} posts from Twitter RSS feeds")
        return posts
    
    def _collect_facebook_pages(self, config: Dict) -> List[Dict]:
        """Collect from Facebook public pages"""
        logger.debug("Collecting from Facebook public pages")
        
        # Simulate collection from Facebook pages
        # In production, would use official Facebook Graph API
        posts = self._simulate_social_posts(
            source="facebook",
            count=config.get("post_limit", 50),
            pages=config.get("pages", []),
            keywords=config.get("keywords", [])
        )
        
        logger.debug(f"Collected {len(posts)} posts from Facebook pages")
        return posts
    
    def _collect_facebook_graph_api(self, config: Dict) -> List[Dict]:
        """Collect from Facebook using official Graph API"""
        logger.debug("Collecting from Facebook via Graph API")
        
        if not self.graph_api_collector.enabled:
            logger.warning("Graph API not configured - falling back to RSS")
            return self._collect_facebook_pages(config)
        
        try:
            # Use Graph API collector
            page_ids = config.get("graph_api_page_ids", [])
            
            if not page_ids:
                logger.warning("No Graph API page IDs configured")
                return []
            
            posts = []
            for page_id in page_ids:
                page_posts = self.graph_api_collector.get_facebook_posts(
                    page_id=page_id,
                    limit=config.get("post_limit", 50),
                    include_comments=config.get("include_comments", True)
                )
                posts.extend(page_posts)
            
            logger.debug(f"Collected {len(posts)} posts from Facebook Graph API")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting from Facebook Graph API: {e}")
            return []
    
    def _collect_instagram_hashtags(self, config: Dict) -> List[Dict]:
        """Collect from Instagram hashtags"""
        logger.debug("Collecting from Instagram hashtags")
        
        # Simulate collection from Instagram hashtags
        posts = self._simulate_social_posts(
            source="instagram",
            count=config.get("post_limit", 40),
            hashtags=config.get("hashtags", []),
            keywords=config.get("keywords", [])
        )
        
        logger.debug(f"Collected {len(posts)} posts from Instagram hashtags")
        return posts
    
    def _collect_instagram_graph_api(self, config: Dict) -> List[Dict]:
        """Collect from Instagram using official Graph API"""
        logger.debug("Collecting from Instagram via Graph API")
        
        if not self.graph_api_collector.enabled:
            logger.warning("Graph API not configured - falling back to hashtag RSS")
            return self._collect_instagram_hashtags(config)
        
        try:
            # Use Graph API collector
            account_ids = config.get("graph_api_business_account_ids", [])
            
            if not account_ids:
                logger.warning("No Graph API Instagram Business Account IDs configured")
                return []
            
            posts = []
            for account_id in account_ids:
                account_posts = self.graph_api_collector.get_instagram_posts(
                    business_account_id=account_id,
                    limit=config.get("post_limit", 40),
                    include_comments=config.get("include_comments", True)
                )
                posts.extend(account_posts)
            
            logger.debug(f"Collected {len(posts)} posts from Instagram Graph API")
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting from Instagram Graph API: {e}")
            return []
    
    def _collect_tiktok_trends(self, config: Dict) -> List[Dict]:
        """Collect from TikTok trending sounds"""
        logger.debug("Collecting from TikTok trends")
        
        posts = self._simulate_social_posts(
            source="tiktok",
            count=config.get("post_limit", 30),
            hashtags=config.get("hashtags", []),
            keywords=config.get("keywords", [])
        )
        
        logger.debug(f"Collected {len(posts)} posts from TikTok trends")
        return posts
    
    def _collect_reddit_communities(self, config: Dict) -> List[Dict]:
        """Collect from Reddit communities"""
        logger.debug("Collecting from Reddit communities")
        
        posts = self._simulate_social_posts(
            source="reddit",
            count=config.get("post_limit", 40),
            subreddits=config.get("subreddits", []),
            keywords=config.get("keywords", [])
        )
        
        logger.debug(f"Collected {len(posts)} posts from Reddit communities")
        return posts
    
    def _simulate_social_posts(self, source: str, count: int, **kwargs) -> List[Dict]:
        """
        Simulate social media posts (for demo/development)
        In production, would fetch from actual APIs
        """
        from random import choice, randint
        
        posts = []
        sample_texts = [
            "The fuel prices are getting out of control! This can't continue much longer.",
            "Public transport in {city} is completely broken. Need solutions NOW.",
            "Just lost my job. Employment situation is getting worse every day.",
            "Government needs to address the economic crisis affecting ordinary families.",
            "Why are prices increasing so much? Can't afford basic necessities.",
            "Transport strike again? This is affecting everyone's daily life.",
            "Education costs are skyrocketing. How are students supposed to study?",
            "Another scandal? When will corruption end in this country?",
            "Healthcare system is struggling. We need better services.",
            "Business is slowing down. Economic outlook is concerning.",
        ]
        
        for i in range(min(count, 50)):
            text = choice(sample_texts)
            posts.append({
                "text": text,
                "author": f"{source}_user_{randint(1000, 9999)}",
                "platform": source,
                "timestamp": datetime.now().isoformat(),
                "url": f"https://{source}.com/post/{generate_id()}",
            })
        
        return posts
    
    def _normalize_posts(self, posts: List[Dict], platform: str) -> List[Dict]:
        """
        Normalize posts to unified schema and add social media metadata
        
        Args:
            posts: Raw posts from platform
            platform: Platform name
            
        Returns:
            Normalized posts with metadata
        """
        normalized = []
        
        for post in posts:
            try:
                # Create unified post schema
                normalized_post = {
                    "id": generate_id(prefix=platform),
                    "text": post.get("text", "")[:self.settings["max_text_length"]],
                    "source": "social_media",
                    "platform": platform,
                    "author": post.get("author", "unknown"),
                    "timestamp": post.get("timestamp", datetime.now().isoformat()),
                    "url": post.get("url", ""),
                    "metadata": {
                        "category": self._detect_category(post.get("text", "")),
                        "language": detect_language(post.get("text", "")),
                        "confidence": 0.8,
                        "sentiment": detect_sentiment(post.get("text", "")),
                        "hashtags": extract_hashtags(post.get("text", "")),
                        "mentions": extract_mentions(post.get("text", "")),
                        "engagement": post.get("engagement", {
                            "likes": 0,
                            "comments": 0,
                            "shares": 0
                        }),
                    }
                }
                
                # Add social media specific fields
                if "engagement" in post:
                    normalized_post["metadata"]["engagement"] = post["engagement"]
                
                # Bot detection
                if BOT_DETECTION.get("enabled", False):
                    normalized_post["metadata"]["bot_score"] = detect_bot_behavior(normalized_post)
                
                normalized.append(normalized_post)
                
            except Exception as e:
                logger.warning(f"Error normalizing post: {e}")
                continue
        
        return normalized
    
    def _detect_category(self, text: str) -> str:
        """
        Detect which category a post belongs to
        
        Args:
            text: Post text
            
        Returns:
            Category name
        """
        text_lower = text.lower()
        
        for category, keywords in TOPIC_CATEGORIES.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "general"
    
    def process_and_store(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process posts and store to disk
        
        Args:
            posts: Collected posts
            
        Returns:
            Processing statistics
        """
        logger.info(f"Processing {len(posts)} posts...")
        
        # Normalize
        posts = DataNormalizer.normalize(posts)
        logger.info(f"After normalization: {len(posts)} posts")
        
        # Deduplicate
        posts = DataNormalizer.deduplicate(posts)
        logger.info(f"After deduplication: {len(posts)} posts")
        
        # Store
        self.storage.save(posts)
        logger.info(f"Stored {len(posts)} posts to {DATA_FILES['processed']}")
        
        # Generate statistics
        stats = self._generate_statistics(posts)
        
        return {
            "total_posts": len(posts),
            "sources": len(set(p.get("platform") for p in posts)),
            "statistics": stats,
            "output_file": DATA_FILES["processed"],
        }
    
    def _generate_statistics(self, posts: List[Dict]) -> Dict[str, Any]:
        """Generate statistics about collected posts"""
        stats = {
            "total": len(posts),
            "by_platform": {},
            "by_category": {},
            "by_language": {},
            "sentiment_distribution": {
                "positive": 0,
                "negative": 0,
                "neutral": 0,
            },
            "hashtags": {},
            "mentions": {},
            "timestamp_range": None,
        }
        
        for post in posts:
            # Platform counts
            platform = post.get("platform", "unknown")
            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
            
            # Category counts
            category = post.get("metadata", {}).get("category", "general")
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Language counts
            language = post.get("metadata", {}).get("language", "unknown")
            stats["by_language"][language] = stats["by_language"].get(language, 0) + 1
            
            # Sentiment distribution
            sentiment = post.get("metadata", {}).get("sentiment", "neutral")
            if sentiment in stats["sentiment_distribution"]:
                stats["sentiment_distribution"][sentiment] += 1
            
            # Hashtags
            hashtags = post.get("metadata", {}).get("hashtags", [])
            for tag in hashtags:
                stats["hashtags"][tag] = stats["hashtags"].get(tag, 0) + 1
            
            # Mentions
            mentions = post.get("metadata", {}).get("mentions", [])
            for mention in mentions:
                stats["mentions"][mention] = stats["mentions"].get(mention, 0) + 1
        
        # Top hashtags and mentions
        stats["top_hashtags"] = sorted(
            stats["hashtags"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        stats["top_mentions"] = sorted(
            stats["mentions"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return stats
    
    def run_collection_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete collection pipeline
        
        Returns:
            Results of the collection
        """
        logger.info("=" * 60)
        logger.info("SOCIAL MEDIA COLLECTION PIPELINE")
        logger.info("=" * 60)
        
        # Collect from all sources
        posts = self.collect_from_all_sources()
        
        if not posts:
            logger.error("No posts collected from any source")
            return {
                "success": False,
                "message": "No posts collected",
                "total_posts": 0,
            }
        
        # Process and store
        result = self.process_and_store(posts)
        
        logger.info("=" * 60)
        logger.info("COLLECTION COMPLETE")
        logger.info(f"Total posts: {result['total_posts']}")
        logger.info(f"Output file: {result['output_file']}")
        logger.info("=" * 60)
        
        return {
            "success": True,
            **result
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored posts"""
        posts = self.storage.load()
        return self._generate_statistics(posts)
    
    def export_posts(self, format: str = "json", output_file: Optional[str] = None) -> str:
        """
        Export posts in different formats
        
        Args:
            format: Export format (json, csv)
            output_file: Output file path (optional)
            
        Returns:
            Output file path
        """
        posts = self.storage.load()
        
        if format == "json":
            if output_file is None:
                output_file = DATA_FILES["processed"]
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
        
        elif format == "csv":
            import csv
            if output_file is None:
                output_file = DATA_FILES["processed"].replace(".json", ".csv")
            
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                if posts:
                    writer = csv.DictWriter(f, fieldnames=posts[0].keys())
                    writer.writeheader()
                    writer.writerows(posts)
        
        logger.info(f"Exported {len(posts)} posts to {output_file}")
        return output_file


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Social Media Intelligence Collection System"
    )
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Run collection pipeline"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics"
    )
    parser.add_argument(
        "--export",
        choices=["json", "csv"],
        help="Export posts"
    )
    parser.add_argument(
        "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    collector = SocialMediaCollector()
    
    if args.collect:
        result = collector.run_collection_pipeline()
        print(json.dumps(result, indent=2))
    
    elif args.stats:
        stats = collector.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.export:
        output = collector.export_posts(format=args.export, output_file=args.output)
        print(f"Exported to: {output}")
    
    else:
        # Default: run full pipeline
        result = collector.run_collection_pipeline()
        stats = collector.get_stats()
        
        print("\n📊 COLLECTION RESULTS:")
        print(f"Total posts: {result['total_posts']}")
        print(f"Output file: {result['output_file']}")
        print(f"\n📈 STATISTICS:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
