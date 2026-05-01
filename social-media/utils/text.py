"""
Text utilities for Tunisian content processing
"""

import re
from typing import List, Tuple
from enum import Enum


class Language(str, Enum):
    """Supported languages"""
    ARABIC = "arabic"
    FRENCH = "french"
    TUNISIAN_DIALECT = "tunisian_dialect"
    MIXED = "mixed"
    ENGLISH = "english"
    UNKNOWN = "unknown"


# Tunisian geographic markers
TUNISIAN_GEOGRAPHIC = [
    "tunisie", "tunis", "sfax", "sousse", "monastir", "gabes", "bizerte",
    "kairouan", "gafsa", "jendouba", "kef", "kasserine", "sidi bouzid",
    "تونس", "صفاقس", "سوسة", "منستير", "قابس", "بنزرت", "القيروان",
    "قفصة", "جندوبة", "الكاف", "القصرين", "سيدي بوزيد", "المنستير"
]

# Tunisian dialect words
TUNISIAN_DIALECT = [
    "barcha", "برشا", "mta3", "متاع", "bch", "يزي", "yezzi", "fisa3",
    "manich", "مانيش", "behi", "بهي", "3ayech", "عايش", "chwiya", "شوية",
    "taw", "تو", "maak", "نحي", "ya3tik", "نعم يسر", "ahna", "و الله",
    "wAllah", "weld", "bneta", "بنت", "الراجل", "الولد", "نهايتو", "تمام",
    "kif", "كيف", "walou", "وللو", "ykherbji", "متاعك", "شكون", "إلا"
]

# Tunisian institutions
TUNISIAN_INSTITUTIONS = [
    "mosaique", "shems", "jawhara", "attessia", "watania", "express.fm",
    "tap", "tap tna", "مساح", "شمس", "جوهرة", "تاص", "الوطنية", "إكسبريس"
]

# Tunisian hashtags
TUNISIAN_HASHTAGS = [
    "#tunisie", "#tunis", "#تونس", "#تونسي", "#تونسية", "#sfax", "#sousse",
    "#tunisian", "#تونسيين", "#تونسيات", "#الجنة", "#صفاقس", "#سوسة"
]

# Negative sentiment words
NEGATIVE_KEYWORDS = [
    "مشكل", "كارثة", "hchouma", "مخزي", "غالي", "barrani", "ظلم", "corruption",
    "فساد", "😡", "😢", "💔", "non", "لا", "ما تمام", "سيء", "تاع",
    "خطير", "وجع", "ألم", "مقرف", "فاشل", "ما بهيش", "كيف هكا", "شنوة هذا"
]

# Positive sentiment words
POSITIVE_KEYWORDS = [
    "برشا مليح", "بارك", "تمام", "super", "excellent", "bravo", "شكرا",
    "شكراً", "مرحبا", "نجاح", "فرحة", "فرحان", "😍", "❤️", "👍", "🎉",
    "mabrouk", "مبروك", "ألف مبروك", "yesss", "yeah", "والله يفرجها"
]


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    if not text:
        return []
    hashtags = re.findall(r'#\S+', text)
    return list(set(hashtags))


def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text"""
    if not text:
        return []
    mentions = re.findall(r'@\S+', text)
    return list(set(mentions))


def detect_language(text: str) -> Language:
    """
    Detect language: arabic, french, tunisian_dialect, mixed, or unknown
    """
    if not text:
        return Language.UNKNOWN
    
    text_lower = text.lower()
    
    # Count character types
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(text)
    
    if total_chars == 0:
        return Language.UNKNOWN
    
    arabic_ratio = arabic_chars / total_chars
    latin_ratio = latin_chars / total_chars
    
    # Check for Tunisian dialect markers
    has_dialect = any(marker in text_lower for marker in TUNISIAN_DIALECT)
    
    if has_dialect and arabic_ratio > 0.3:
        return Language.TUNISIAN_DIALECT
    elif arabic_ratio > 0.4:
        return Language.ARABIC
    elif latin_ratio > 0.4:
        # Check if it's French or English
        french_markers = ["le ", "la ", "de ", "et ", "pour ", "avec "]
        has_french = any(marker in text_lower for marker in french_markers)
        return Language.FRENCH if has_french else Language.ENGLISH
    elif arabic_ratio > 0.1 and latin_ratio > 0.1:
        return Language.MIXED
    
    return Language.UNKNOWN


def detect_tunisian(text: str) -> Tuple[bool, float]:
    """
    Detect if text is Tunisian with confidence score (0-1)
    Returns: (is_tunisian, confidence_score)
    """
    if not text:
        return False, 0.0
    
    text_lower = text.lower()
    score = 0.0
    max_score = 0.0
    
    # Geographic markers
    for marker in TUNISIAN_GEOGRAPHIC:
        max_score += 0.25
        if marker in text_lower:
            score += 0.25
    
    # Dialect words
    for marker in TUNISIAN_DIALECT:
        max_score += 0.15
        if marker in text_lower:
            score += 0.15
    
    # Institutions
    for marker in TUNISIAN_INSTITUTIONS:
        max_score += 0.20
        if marker in text_lower:
            score += 0.20
    
    # Hashtags
    hashtags = extract_hashtags(text)
    for hashtag in hashtags:
        for tn_tag in TUNISIAN_HASHTAGS:
            max_score += 0.10
            if tn_tag.lower() in hashtag.lower():
                score += 0.10
    
    # Language check
    lang = detect_language(text)
    if lang == Language.TUNISIAN_DIALECT:
        score += 0.30
        max_score += 0.30
    elif lang == Language.ARABIC:
        score += 0.15
        max_score += 0.30
    
    # Normalize score
    confidence = score / max_score if max_score > 0 else 0.0
    confidence = min(1.0, max(0.0, confidence))
    
    is_tunisian = confidence > 0.3
    
    return is_tunisian, confidence


def classify_sentiment(text: str) -> str:
    """Classify sentiment: positive, negative, or neutral"""
    if not text:
        return "neutral"
    
    text_lower = text.lower()
    neg_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    pos_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    
    if neg_count > pos_count and neg_count > 0:
        return "negative"
    elif pos_count > neg_count and pos_count > 0:
        return "positive"
    
    return "neutral"


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    
    return text


def extract_entities(text: str) -> dict:
    """Extract entities from text"""
    entities = {
        "hashtags": extract_hashtags(text),
        "mentions": extract_mentions(text),
        "language": detect_language(text).value,
        "urls": re.findall(r'http\S+|www\S+', text),
    }
    return entities
