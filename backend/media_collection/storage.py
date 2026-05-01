"""
Storage Manager
Handles data persistence (JSON, MongoDB, etc.)
"""

import json
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageManager:
    """Handles data persistence"""
    
    def __init__(self, storage_type: str = "json", path: str = "data/processed/posts.json"):
        """
        Initialize storage manager
        
        Args:
            storage_type: type of storage (json, mongodb, postgresql)
            path: path for file-based storage
        """
        self.storage_type = storage_type
        self.path = path
        
        # Create directory if it doesn't exist
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Storage initialized: {storage_type} at {path}")
    
    def save(self, posts: List[Dict]):
        """
        Save posts to storage
        
        Args:
            posts: list of posts to save
        """
        if self.storage_type == "json":
            self._save_json(posts)
        elif self.storage_type == "mongodb":
            self._save_mongodb(posts)
        else:
            logger.error(f"Unsupported storage type: {self.storage_type}")
    
    def load(self) -> List[Dict]:
        """
        Load posts from storage
        
        Returns:
            List of loaded posts
        """
        if self.storage_type == "json":
            return self._load_json()
        elif self.storage_type == "mongodb":
            return self._load_mongodb()
        else:
            logger.error(f"Unsupported storage type: {self.storage_type}")
            return []
    
    def _save_json(self, posts: List[Dict]):
        """Save to JSON file"""
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Saved {len(posts)} posts to {self.path}")
        except Exception as e:
            logger.error(f"❌ Error saving JSON: {str(e)}")
    
    def _load_json(self) -> List[Dict]:
        """Load from JSON file"""
        try:
            if not Path(self.path).exists():
                logger.warning(f"⚠️  File not found: {self.path}")
                return []
            
            with open(self.path, 'r', encoding='utf-8') as f:
                posts = json.load(f)
            
            logger.info(f"✅ Loaded {len(posts)} posts from {self.path}")
            return posts
        except Exception as e:
            logger.error(f"❌ Error loading JSON: {str(e)}")
            return []
    
    def _save_mongodb(self, posts: List[Dict]):
        """Save to MongoDB (future implementation)"""
        logger.warning("MongoDB support not implemented yet")
    
    def _load_mongodb(self) -> List[Dict]:
        """Load from MongoDB (future implementation)"""
        logger.warning("MongoDB support not implemented yet")
        return []
    
    def append(self, posts: List[Dict]):
        """
        Append new posts to existing storage
        
        Args:
            posts: list of posts to append
        """
        existing = self.load()
        
        # Combine and deduplicate by ID
        all_posts = existing + posts
        unique_posts = {p["id"]: p for p in all_posts}.values()
        
        self.save(list(unique_posts))
        logger.info(f"✅ Appended {len(posts)} posts")
    
    def get_by_source(self, source: str) -> List[Dict]:
        """
        Get posts from specific source
        
        Args:
            source: source type (rss, user_input, dataset)
        
        Returns:
            Posts from that source
        """
        posts = self.load()
        filtered = [p for p in posts if p.get("source") == source]
        logger.info(f"Retrieved {len(filtered)} posts from source: {source}")
        return filtered
    
    def get_by_category(self, category: str) -> List[Dict]:
        """
        Get posts from specific category
        
        Args:
            category: category name
        
        Returns:
            Posts in that category
        """
        posts = self.load()
        filtered = [
            p for p in posts
            if p.get("metadata", {}).get("category") == category
        ]
        logger.info(f"Retrieved {len(filtered)} posts from category: {category}")
        return filtered
    
    def clear(self):
        """Clear all stored data"""
        try:
            self.save([])
            logger.info("✅ Storage cleared")
        except Exception as e:
            logger.error(f"❌ Error clearing storage: {str(e)}")
    
    def get_stats(self) -> Dict:
        """
        Get storage statistics
        
        Returns:
            Dictionary with stats
        """
        posts = self.load()
        
        sources = {}
        categories = {}
        languages = {}
        
        for post in posts:
            # Count by source
            source = post.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
            
            # Count by category
            category = post.get("metadata", {}).get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
            
            # Count by language
            language = post.get("metadata", {}).get("language", "unknown")
            languages[language] = languages.get(language, 0) + 1
        
        stats = {
            "total_posts": len(posts),
            "by_source": sources,
            "by_category": categories,
            "by_language": languages
        }
        
        return stats


# USAGE EXAMPLE
if __name__ == "__main__":
    storage = StorageManager(storage_type="json", path="data/processed/posts.json")
    
    # Create sample data
    sample_posts = [
        {
            "id": "test_1",
            "text": "transport is bad",
            "source": "rss",
            "platform": "bbc",
            "author": "bbc",
            "timestamp": "2026-05-01T10:00:00",
            "url": "http://example.com",
            "metadata": {
                "category": "transport",
                "language": "en",
                "confidence": 0.9
            }
        },
        {
            "id": "test_2",
            "text": "prices too high",
            "source": "user_input",
            "platform": "cli",
            "author": "user",
            "timestamp": "2026-05-01T10:05:00",
            "url": None,
            "metadata": {
                "category": "prices",
                "language": "en",
                "confidence": 0.85
            }
        }
    ]
    
    print("\n" + "="*60)
    print("STORAGE MANAGER DEMO")
    print("="*60)
    
    # Save
    storage.save(sample_posts)
    
    # Load
    loaded = storage.load()
    print(f"\n✅ Saved and loaded {len(loaded)} posts")
    
    # Get stats
    stats = storage.get_stats()
    print(f"\n📊 STATISTICS")
    print(f"   Total posts: {stats['total_posts']}")
    print(f"   By source: {stats['by_source']}")
    print(f"   By category: {stats['by_category']}")
    print(f"   By language: {stats['by_language']}")
