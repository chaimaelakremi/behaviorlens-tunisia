"""
Post normalizer - deduplicates, cleans, and normalizes posts
"""

import re
import hashlib
from typing import List, Dict, Optional
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class PostNormalizer:
    """Normalize and deduplicate posts"""
    
    def __init__(self):
        """Initialize normalizer"""
        self.seen_hashes: set = set()
        self.seen_content: dict = {}  # content_hash -> post_id
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for comparison
        - Convert to lowercase
        - Remove extra whitespace
        - Remove diacritics
        - Remove URLs
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+', '', text)
        
        # Remove hashtags (just the # symbol)
        text = re.sub(r'#', '', text)
        
        # Remove mentions (just the @ symbol)
        text = re.sub(r'@', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common noise
        text = re.sub(r'[🎉😍❤️😂👍😢😡💔]', '', text)
        
        return text
    
    def get_content_hash(self, text: str) -> str:
        """Get SHA256 hash of normalized content"""
        normalized = self.normalize_text(text)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def is_duplicate(self, text: str, threshold: float = 0.85) -> bool:
        """
        Check if text is a duplicate
        Uses fuzzy matching with configurable threshold
        """
        if not text:
            return False
        
        normalized = self.normalize_text(text)
        content_hash = hashlib.sha256(normalized.encode()).hexdigest()
        
        # Exact match
        if content_hash in self.seen_hashes:
            return True
        
        # Fuzzy match against existing content
        for existing_hash, (existing_text, existing_id) in self.seen_content.items():
            similarity = SequenceMatcher(None, normalized, existing_text).ratio()
            if similarity >= threshold:
                logger.debug(f"Fuzzy duplicate detected: {similarity:.2%}")
                return True
        
        return False
    
    def register_post(self, text: str, post_id: str):
        """Register a post as seen"""
        if not text:
            return
        
        normalized = self.normalize_text(text)
        content_hash = hashlib.sha256(normalized.encode()).hexdigest()
        
        self.seen_hashes.add(content_hash)
        self.seen_content[content_hash] = (normalized, post_id)
    
    def normalize_post(self, post: dict) -> dict:
        """
        Normalize post data
        
        Args:
            post: Post dictionary from collector
            
        Returns:
            Normalized post dictionary
        """
        normalized = post.copy()
        
        # Normalize text
        if "text" in normalized:
            normalized["text"] = self.normalize_text(normalized["text"])
        
        # Ensure source is lowercase
        if "source" in normalized:
            normalized["source"] = normalized["source"].lower()
        
        # Clean URLs
        if "url" in normalized:
            normalized["url"] = normalized["url"].strip()
        
        # Normalize engagement metrics
        for metric in ["likes", "shares", "comments_count"]:
            if metric in normalized:
                normalized[metric] = max(0, int(normalized[metric]))
        
        # Ensure author is string
        if "author" in normalized:
            normalized["author"] = str(normalized["author"]).strip()
        
        return normalized
    
    def deduplicate_posts(self, posts: List[dict]) -> List[dict]:
        """
        Remove duplicates from post list
        Uses both exact and fuzzy matching
        """
        unique_posts = []
        
        for post in posts:
            text = post.get("text", "")
            if not self.is_duplicate(text):
                unique_posts.append(post)
                self.register_post(text, post.get("post_id", "unknown"))
            else:
                logger.debug(f"Skipping duplicate post: {text[:50]}...")
        
        logger.info(f"Deduplicated {len(posts)} posts to {len(unique_posts)} unique posts")
        return unique_posts
    
    def merge_duplicates(self, posts: List[dict]) -> List[dict]:
        """
        Merge duplicate posts, keeping the best version
        Useful for combining posts from multiple sources
        """
        if not posts:
            return []
        
        # Group by normalized content
        groups: Dict[str, List[dict]] = {}
        
        for post in posts:
            text = post.get("text", "")
            normalized = self.normalize_text(text)
            content_hash = hashlib.sha256(normalized.encode()).hexdigest()
            
            if content_hash not in groups:
                groups[content_hash] = []
            groups[content_hash].append(post)
        
        # Merge each group, keeping best post
        merged = []
        for group in groups.values():
            best_post = self._select_best_post(group)
            merged.append(best_post)
        
        logger.info(f"Merged {len(posts)} posts into {len(merged)} unique posts")
        return merged
    
    def _select_best_post(self, posts: List[dict]) -> dict:
        """
        Select best post from duplicates
        Criteria: Most engagement, most complete data
        """
        def score_post(post):
            score = 0
            score += post.get("likes", 0) * 0.5
            score += post.get("comments_count", 0)
            score += len(post.get("text", "")) / 100  # Longer text preferred
            if post.get("media_type") != "text":
                score += 10  # Media preferred
            return score
        
        return max(posts, key=score_post)
    
    def reset(self):
        """Reset deduplication cache"""
        self.seen_hashes.clear()
        self.seen_content.clear()
        logger.info("Normalizer cache reset")
