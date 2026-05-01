"""
Utility functions for Social Media Collection System
Includes sentiment analysis, language detection, text processing
"""

import logging
import hashlib
import re
from datetime import datetime
from typing import List, Dict, Any
import os

from .config import (
    SENTIMENT_KEYWORDS,
    LANGUAGE_SETTINGS,
    LOGGING_CONFIG,
    BOT_DETECTION,
)


def setup_logging() -> logging.Logger:
    """
    Setup logging configuration
    
    Returns:
        Configured logger instance
    """
    # Create logs directory
    log_dir = os.path.dirname(LOGGING_CONFIG["file"])
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("social_media")
    logger.setLevel(getattr(logging, LOGGING_CONFIG["level"]))
    
    # Create handlers
    from logging.handlers import RotatingFileHandler
    
    file_handler = RotatingFileHandler(
        LOGGING_CONFIG["file"],
        maxBytes=LOGGING_CONFIG["max_size"],
        backupCount=LOGGING_CONFIG["backup_count"]
    )
    
    console_handler = logging.StreamHandler()
    
    # Create formatter
    formatter = logging.Formatter(LOGGING_CONFIG["format"])
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logging()


def generate_id(prefix: str = "sm", length: int = 12) -> str:
    """
    Generate a unique ID
    
    Args:
        prefix: ID prefix
        length: ID length
        
    Returns:
        Unique ID string
    """
    timestamp = datetime.now().isoformat().encode()
    hash_obj = hashlib.sha256(timestamp)
    hash_hex = hash_obj.hexdigest()[:length]
    return f"{prefix}_{hash_hex}"


def extract_hashtags(text: str) -> List[str]:
    """
    Extract hashtags from text
    
    Args:
        text: Text to extract from
        
    Returns:
        List of hashtags
    """
    pattern = r"#\w+"
    hashtags = re.findall(pattern, text)
    return list(set(hashtags))  # Remove duplicates


def extract_mentions(text: str) -> List[str]:
    """
    Extract mentions from text
    
    Args:
        text: Text to extract from
        
    Returns:
        List of mentions
    """
    pattern = r"@\w+"
    mentions = re.findall(pattern, text)
    return list(set(mentions))  # Remove duplicates


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text
    
    Args:
        text: Text to extract from
        
    Returns:
        List of URLs
    """
    pattern = r"https?://\S+"
    urls = re.findall(pattern, text)
    return urls


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)
    
    # Remove mentions and hashtags (optional - keep for now)
    # text = re.sub(r"@\w+|#\w+", "", text)
    
    return text


def detect_sentiment(text: str) -> str:
    """
    Detect sentiment of text (positive, negative, neutral)
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment: "positive", "negative", or "neutral"
    """
    text_lower = text.lower()
    
    positive_count = sum(1 for word in SENTIMENT_KEYWORDS["positive"] if word in text_lower)
    negative_count = sum(1 for word in SENTIMENT_KEYWORDS["negative"] if word in text_lower)
    urgent_count = sum(1 for word in SENTIMENT_KEYWORDS["urgent"] if word in text_lower)
    
    # Boost negative score if urgent words present
    negative_count += urgent_count * 0.5
    
    if negative_count > positive_count:
        return "negative"
    elif positive_count > negative_count:
        return "positive"
    else:
        return "neutral"


def detect_sentiment_score(text: str) -> float:
    """
    Calculate sentiment score (0.0 to 1.0)
    
    Args:
        text: Text to analyze
        
    Returns:
        Sentiment score (0 = very negative, 1 = very positive)
    """
    text_lower = text.lower()
    
    positive_count = sum(1 for word in SENTIMENT_KEYWORDS["positive"] if word in text_lower)
    negative_count = sum(1 for word in SENTIMENT_KEYWORDS["negative"] if word in text_lower)
    
    total = positive_count + negative_count
    
    if total == 0:
        return 0.5  # Neutral
    
    positive_ratio = positive_count / total
    return positive_ratio


def detect_language(text: str) -> str:
    """
    Detect language of text
    
    Args:
        text: Text to analyze
        
    Returns:
        Language code: "ar", "fr", "en", or "mix"
    """
    # Simple heuristic-based detection
    
    # Check for Arabic characters
    arabic_pattern = r"[\u0600-\u06FF]"
    has_arabic = bool(re.search(arabic_pattern, text))
    
    # Check for French/English words
    french_keywords = LANGUAGE_SETTINGS["arabic_keywords"]["French"]
    english_keywords = LANGUAGE_SETTINGS["arabic_keywords"]["English"]
    
    has_french = any(word in text.lower() for word in french_keywords)
    has_english = any(word in text.lower() for word in english_keywords)
    
    # Determine language
    languages_found = sum([has_arabic, has_french, has_english])
    
    if languages_found > 1:
        return "mix"
    elif has_arabic:
        return "ar"
    elif has_french:
        return "fr"
    elif has_english:
        return "en"
    else:
        return "en"  # Default


def detect_urgency(text: str) -> float:
    """
    Detect urgency level (0.0 to 1.0)
    
    Args:
        text: Text to analyze
        
    Returns:
        Urgency score
    """
    text_lower = text.lower()
    urgent_keywords = SENTIMENT_KEYWORDS["urgent"]
    
    count = sum(1 for word in urgent_keywords if word in text_lower)
    
    # Cap at 1.0
    return min(count * 0.2, 1.0)


def detect_bot_behavior(post: Dict[str, Any]) -> float:
    """
    Detect likelihood that post is from a bot
    
    Args:
        post: Post data
        
    Returns:
        Bot score (0.0 to 1.0, higher = more likely bot)
    """
    score = 0.0
    max_score = 0.0
    
    if not BOT_DETECTION.get("enabled", False):
        return 0.0
    
    # Check 1: Posting frequency pattern
    if BOT_DETECTION.get("check_posting_patterns", False):
        # If author has many posts in short time = likely bot
        # (Would need time series data)
        max_score += 0.3
    
    # Check 2: Content similarity
    if BOT_DETECTION.get("check_content_similarity", False):
        # Check if text contains repeated phrases
        text = post.get("text", "").lower()
        words = text.split()
        
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.5:  # Very repetitive
                score += 0.3
        
        max_score += 0.3
    
    # Check 3: Engagement ratio
    if BOT_DETECTION.get("check_engagement_ratio", False):
        engagement = post.get("metadata", {}).get("engagement", {})
        if engagement:
            likes = engagement.get("likes", 0)
            comments = engagement.get("comments", 0)
            shares = engagement.get("shares", 0)
            
            # Bots often have high likes but low comments/shares
            total_engagement = likes + comments + shares
            if total_engagement > 0:
                non_like_ratio = (comments + shares) / total_engagement
                if non_like_ratio < 0.1:  # <10% non-like engagement
                    score += 0.2
        
        max_score += 0.2
    
    # Additional checks
    author = post.get("author", "").lower()
    if len(author) < 3 or author.isdigit():
        score += 0.2
        max_score += 0.2
    
    # Normalize to 0-1
    if max_score > 0:
        return min(score / max_score, 1.0)
    
    return 0.0


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    return text


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts (0.0 to 1.0)
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score
    """
    from difflib import SequenceMatcher
    
    text1 = normalize_text(text1)
    text2 = normalize_text(text2)
    
    return SequenceMatcher(None, text1, text2).ratio()


def format_timestamp(timestamp: str) -> str:
    """
    Format timestamp to readable format
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        Formatted timestamp
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def get_time_ago(timestamp: str) -> str:
    """
    Get human-readable time ago (e.g., "2 hours ago")
    
    Args:
        timestamp: ISO format timestamp
        
    Returns:
        Human-readable time difference
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "just now"
    except:
        return "unknown"


def batch_process_posts(posts: List[Dict], batch_size: int = 100) -> List[List[Dict]]:
    """
    Split posts into batches for processing
    
    Args:
        posts: List of posts
        batch_size: Size of each batch
        
    Returns:
        List of post batches
    """
    batches = []
    for i in range(0, len(posts), batch_size):
        batches.append(posts[i:i + batch_size])
    return batches


def print_collection_summary(result: Dict[str, Any]) -> None:
    """
    Print collection results summary
    
    Args:
        result: Collection result dictionary
    """
    print("\n" + "=" * 60)
    print("📊 SOCIAL MEDIA COLLECTION SUMMARY")
    print("=" * 60)
    
    print(f"✓ Total posts: {result.get('total_posts', 0)}")
    print(f"✓ Sources: {result.get('sources', 0)}")
    print(f"✓ Output file: {result.get('output_file', 'N/A')}")
    
    stats = result.get("statistics", {})
    
    if stats.get("by_platform"):
        print(f"\n📱 By Platform:")
        for platform, count in sorted(stats["by_platform"].items()):
            print(f"  - {platform}: {count} posts")
    
    if stats.get("by_category"):
        print(f"\n📂 By Category:")
        for category, count in sorted(stats["by_category"].items()):
            print(f"  - {category}: {count} posts")
    
    if stats.get("by_language"):
        print(f"\n🗣️  By Language:")
        for lang, count in sorted(stats["by_language"].items()):
            print(f"  - {lang}: {count} posts")
    
    if stats.get("sentiment_distribution"):
        print(f"\n💭 Sentiment Distribution:")
        sentiment = stats["sentiment_distribution"]
        print(f"  - Positive: {sentiment.get('positive', 0)}")
        print(f"  - Negative: {sentiment.get('negative', 0)}")
        print(f"  - Neutral: {sentiment.get('neutral', 0)}")
    
    if stats.get("top_hashtags"):
        print(f"\n#️⃣  Top Hashtags:")
        for hashtag, count in stats["top_hashtags"][:5]:
            print(f"  - {hashtag}: {count} mentions")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test utilities
    test_text = "I hate the fuel prices! #tunisia #expensive @government"
    
    print(f"Text: {test_text}")
    print(f"Sentiment: {detect_sentiment(test_text)}")
    print(f"Sentiment score: {detect_sentiment_score(test_text):.2f}")
    print(f"Language: {detect_language(test_text)}")
    print(f"Urgency: {detect_urgency(test_text):.2f}")
    print(f"Hashtags: {extract_hashtags(test_text)}")
    print(f"Mentions: {extract_mentions(test_text)}")
