"""
Bot detection and suspicious pattern analysis
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BotDetectorAdvanced:
    """Advanced bot detection using multiple heuristics"""
    
    # Suspicious patterns
    SPAM_URLS = [
        r"bit\.ly", r"tinyurl", r"short\.link", r"ur\.cm",
        r"t\.co", r"goo\.gl", r"ow\.ly"
    ]
    
    # URL sharing patterns (suspicious if >3 different URLs)
    URL_THRESHOLD = 3
    
    # Repetitive content
    REPETITION_THRESHOLD = 0.3  # If >30% repeated words
    
    def __init__(self):
        """Initialize bot detector"""
        self.known_bots: set = set()
    
    def detect_bot_score(self, post: Dict) -> Tuple[float, Dict[str, any]]:
        """
        Calculate bot probability score (0-1)
        
        Args:
            post: Post dictionary with text, author, likes, etc.
            
        Returns:
            Tuple of (score, details)
        """
        text = post.get("text", "")
        author = post.get("author", "")
        likes = post.get("likes", 0)
        shares = post.get("shares", 0)
        comments_count = post.get("comments_count", 0)
        
        details = {
            "url_spam": False,
            "excessive_urls": False,
            "repetitive_content": False,
            "suspicious_engagement": False,
            "account_pattern": False,
            "hashtag_spam": False,
            "mention_spam": False,
        }
        
        score = 0.0
        
        # 1. Check for URL spam
        url_spam_score, url_spam = self._check_url_spam(text)
        score += url_spam_score * 0.15
        details["url_spam"] = url_spam
        
        # 2. Check for excessive URLs
        url_count_score, excessive = self._check_url_count(text)
        score += url_count_score * 0.15
        details["excessive_urls"] = excessive
        
        # 3. Check for repetitive content
        repeat_score, is_repetitive = self._check_repetition(text)
        score += repeat_score * 0.15
        details["repetitive_content"] = is_repetitive
        
        # 4. Check for suspicious engagement
        engagement_score = self._check_engagement(likes, shares, comments_count, len(text))
        score += engagement_score * 0.15
        details["suspicious_engagement"] = engagement_score > 0.5
        
        # 5. Check author/account patterns
        account_score = self._check_account_pattern(author)
        score += account_score * 0.15
        details["account_pattern"] = account_score > 0.5
        
        # 6. Check hashtag spam
        hashtag_score, has_spam = self._check_hashtag_spam(text)
        score += hashtag_score * 0.125
        details["hashtag_spam"] = has_spam
        
        # 7. Check mention spam
        mention_score, has_spam = self._check_mention_spam(text)
        score += mention_score * 0.125
        details["mention_spam"] = has_spam
        
        return min(1.0, score), details
    
    def _check_url_spam(self, text: str) -> Tuple[float, bool]:
        """Check for known spam URL shorteners"""
        if not text:
            return 0.0, False
        
        for pattern in self.SPAM_URLS:
            if re.search(pattern, text, re.IGNORECASE):
                return 0.8, True
        
        return 0.0, False
    
    def _check_url_count(self, text: str) -> Tuple[float, bool]:
        """Check for excessive URLs"""
        if not text:
            return 0.0, False
        
        urls = re.findall(r'http\S+|www\S+', text)
        
        if len(urls) > self.URL_THRESHOLD:
            # Score increases with URL count
            score = min(1.0, len(urls) / 10)
            return score, True
        
        return 0.0, False
    
    def _check_repetition(self, text: str) -> Tuple[float, bool]:
        """Check for repetitive content"""
        if not text:
            return 0.0, False
        
        words = text.split()
        if len(words) < 5:
            return 0.0, False
        
        # Calculate unique word ratio
        unique_words = set(words)
        unique_ratio = len(unique_words) / len(words)
        
        if unique_ratio < self.REPETITION_THRESHOLD:
            score = 1.0 - unique_ratio
            return score, True
        
        return 0.0, False
    
    def _check_engagement(self, likes: int, shares: int, 
                         comments: int, text_length: int) -> float:
        """Check for suspicious engagement patterns"""
        # Small/no text with high engagement = suspicious
        if text_length < 50 and likes > 100000:
            return 1.0
        
        # Disproportionate engagement
        engagement = likes + shares + comments * 10  # Weight comments higher
        text_score = text_length / 100
        
        if text_score > 0:
            ratio = engagement / text_score
            if ratio > 1000:
                return 0.8
            elif ratio > 500:
                return 0.5
        
        return 0.0
    
    def _check_account_pattern(self, author: str) -> float:
        """Check for suspicious account patterns"""
        if not author:
            return 0.0
        
        author_lower = author.lower()
        score = 0.0
        
        # Check for random string patterns
        if re.match(r'^[a-z0-9]{20,}$', author_lower):
            score += 0.5
        
        # Check for duplicate characters
        if re.search(r'(.)\1{5,}', author_lower):
            score += 0.3
        
        # Check for number-only patterns
        if re.match(r'^\d{10,}$', author):
            score += 0.5
        
        return min(1.0, score)
    
    def _check_hashtag_spam(self, text: str) -> Tuple[float, bool]:
        """Check for hashtag spam"""
        if not text:
            return 0.0, False
        
        hashtags = re.findall(r'#\S+', text)
        
        # Too many hashtags
        if len(hashtags) > 15:
            return min(1.0, len(hashtags) / 30), True
        
        # All text is hashtags
        text_without_hashtags = re.sub(r'#\S+', '', text).strip()
        if len(text_without_hashtags) < 10 and len(hashtags) > 5:
            return 0.8, True
        
        return 0.0, False
    
    def _check_mention_spam(self, text: str) -> Tuple[float, bool]:
        """Check for mention spam"""
        if not text:
            return 0.0, False
        
        mentions = re.findall(r'@\S+', text)
        
        # Too many mentions
        if len(mentions) > 10:
            return min(1.0, len(mentions) / 20), True
        
        # All text is mentions
        text_without_mentions = re.sub(r'@\S+', '', text).strip()
        if len(text_without_mentions) < 10 and len(mentions) > 3:
            return 0.7, True
        
        return 0.0, False
    
    def is_bot_account(self, author: str) -> bool:
        """Check if account is known bot"""
        return author in self.known_bots
    
    def register_bot(self, author: str):
        """Register account as bot"""
        self.known_bots.add(author)
        logger.info(f"Registered bot account: {author}")
    
    def unregister_bot(self, author: str):
        """Unregister account from bot list"""
        self.known_bots.discard(author)
