"""
Post classification system - categorizes posts by type, sentiment, language, and Tunisian relevance
"""

from typing import Tuple, Optional
import logging
from ..utils.text import (
    detect_language,
    detect_tunisian,
    classify_sentiment,
    extract_hashtags,
    Language,
)

logger = logging.getLogger(__name__)


class PostClassifier:
    """Classify posts by multiple dimensions"""
    
    # Post type keywords
    COMPLAINT_KEYWORDS = [
        "شكاية", "complaint", "problem", "issue", "problème", "مشكل",
        "bug", "crash", "broken", "doesn't work", "ne marche pas",
        "ظالمة", "ظلم", "hchouma", "مخزي"
    ]
    
    OPINION_KEYWORDS = [
        "رأي", "opinion", "think", "believe", "اعتقد", "عندي رأي",
        "حسبي", "je pense", "à mon avis", "I believe", "IMHO",
        "I think", "في رأيي", "حسب رأيي"
    ]
    
    NEWS_KEYWORDS = [
        "news", "breaking", "update", "announced", "reported",
        "أخبار", "عاجل", "نبأ", "إعلان", "أفادت", "أعلنت"
    ]
    
    HUMOR_KEYWORDS = [
        "😂", "😄", "🤣", "haha", "lol", "lmao", "funny", "joke",
        "meme", "funny", "ههه", "ولول", "😅", "😆"
    ]
    
    QUESTION_KEYWORDS = [
        "?", "سؤال", "question", "how", "what", "why", "where",
        "كيف", "إيه", "ليش", "فين", "الله يعين"
    ]
    
    PROMOTION_KEYWORDS = [
        "discount", "sale", "offer", "promo", "buy", "shop",
        "تخفيف", "عرض", "تخفيض", "شراء", "متاع", "available",
        "special price", "limited time"
    ]
    
    ANNOUNCEMENT_KEYWORDS = [
        "announce", "announce", "event", "happening", "coming soon",
        "إعلان", "حدث", "موعد", "قريبا", "سيكون", "happening"
    ]
    
    def classify_post_type(self, text: str) -> Optional[str]:
        """
        Classify post into categories:
        - complaint: Reporting issues
        - opinion: Personal viewpoint
        - news: News/updates
        - humor: Funny content
        - question: Questions/enquiries
        - promotion: Sales/marketing
        - announcement: Events/announcements
        - other: Default
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Check for question marks, but exclude URLs
        has_question = "?" in text and "http" not in text.split("?")[0]
        
        scores = {
            "complaint": sum(1 for kw in self.COMPLAINT_KEYWORDS if kw in text_lower),
            "opinion": sum(1 for kw in self.OPINION_KEYWORDS if kw in text_lower),
            "news": sum(1 for kw in self.NEWS_KEYWORDS if kw in text_lower),
            "humor": sum(1 for kw in self.HUMOR_KEYWORDS if kw in text_lower),
            "question": (1 if has_question else 0) + sum(1 for kw in self.QUESTION_KEYWORDS if kw in text_lower),
            "promotion": sum(1 for kw in self.PROMOTION_KEYWORDS if kw in text_lower),
            "announcement": sum(1 for kw in self.ANNOUNCEMENT_KEYWORDS if kw in text_lower),
        }
        
        # Get highest scoring type
        max_type = max(scores.items(), key=lambda x: x[1])
        
        if max_type[1] > 0:
            return max_type[0]
        
        return None
    
    def classify_post(self, text: str, source: str = "unknown") -> dict:
        """
        Comprehensive post classification
        
        Args:
            text: Post text content
            source: Source platform
            
        Returns:
            Dictionary with classification results
        """
        if not text or len(text) < 10:
            return {
                "post_type": None,
                "sentiment": "neutral",
                "language": "unknown",
                "is_tunisian": False,
                "tunisian_score": 0.0,
                "confidence": 0.0,
            }
        
        # Classify post type
        post_type = self.classify_post_type(text)
        
        # Detect language
        language = detect_language(text)
        
        # Detect sentiment
        sentiment = classify_sentiment(text)
        
        # Detect if Tunisian
        is_tunisian, tunisian_score = detect_tunisian(text)
        
        # Calculate overall confidence
        confidence = tunisian_score if is_tunisian else 0.5
        
        return {
            "post_type": post_type,
            "sentiment": sentiment,
            "language": language.value,
            "is_tunisian": is_tunisian,
            "tunisian_score": tunisian_score,
            "confidence": confidence,
        }


class SentimentAnalyzer:
    """Advanced sentiment analysis with dialect scoring"""
    
    # Enhanced sentiment keywords
    VERY_NEGATIVE = [
        "horrible", "worst", "disgusting", "hate", "sick",
        "كارثة", "فضيح", "خسارة", "تاع البلاغة", "ما بهيش"
    ]
    
    NEGATIVE = [
        "bad", "terrible", "awful", "worse", "problem",
        "مشكل", "سيء", "ما تمام", "ظلم"
    ]
    
    POSITIVE = [
        "good", "great", "awesome", "love", "best",
        "بارك", "مليح", "تمام", "رائع", "فخور"
    ]
    
    VERY_POSITIVE = [
        "excellent", "amazing", "wonderful", "fantastic",
        "ألف مبروك", "برشا برشا مليح", "😍", "❤️"
    ]
    
    def analyze_sentiment(self, text: str) -> dict:
        """
        Analyze sentiment with confidence scores
        
        Returns:
            Dict with sentiment, score, and confidence
        """
        if not text:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
            }
        
        text_lower = text.lower()
        
        very_neg_count = sum(1 for kw in self.VERY_NEGATIVE if kw in text_lower)
        neg_count = sum(1 for kw in self.NEGATIVE if kw in text_lower)
        pos_count = sum(1 for kw in self.POSITIVE if kw in text_lower)
        very_pos_count = sum(1 for kw in self.VERY_POSITIVE if kw in text_lower)
        
        # Calculate score (-1 to 1)
        score = (very_pos_count * 2 + pos_count - neg_count - very_neg_count * 2) / len(text_lower) * 10
        score = max(-1.0, min(1.0, score))
        
        if score > 0.2:
            sentiment = "positive"
            confidence = abs(score)
        elif score < -0.2:
            sentiment = "negative"
            confidence = abs(score)
        else:
            sentiment = "neutral"
            confidence = 1 - abs(score)
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": confidence,
        }


class BotDetector:
    """Detect bot accounts and suspicious patterns"""
    
    SUSPICIOUS_PATTERNS = [
        r"http\S+", # Multiple URLs
        r"@\w+\s@\w+\s@\w+", # Multiple mentions
        r"[a-z0-9]{40,}", # Long hex strings
        r"\d{9,}", # Very long numbers
    ]
    
    def detect_bot_score(self, text: str, metadata: dict = None) -> float:
        """
        Calculate bot probability score (0-1)
        
        Args:
            text: Post text
            metadata: Additional metadata (likes, followers, etc.)
            
        Returns:
            Bot probability score
        """
        if not text:
            return 0.0
        
        score = 0.0
        
        # Check for suspicious patterns
        import re
        for pattern in self.SUSPICIOUS_PATTERNS:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 5:
                score += 0.2
        
        # Check for repetitive content
        words = text.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                score += 0.3
        
        # Check metadata if provided
        if metadata:
            # Posts with unusual engagement patterns
            if metadata.get("likes", 0) > 100000 and len(text) < 50:
                score += 0.2
        
        return min(1.0, score)
