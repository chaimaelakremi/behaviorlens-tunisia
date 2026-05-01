"""
Advanced sentiment analysis with dialect support
"""

import logging
from typing import Dict, Tuple, Optional
import re

logger = logging.getLogger(__name__)


class TunisianSentimentAnalyzer:
    """Tunisian dialect sentiment analysis"""
    
    # Tunisian positive expressions
    TUNISIAN_POSITIVE = {
        "barcha": 1.0,  # very/a lot (positive intensity)
        "مليح": 1.0,  # good
        "الحمد لله": 1.0,  # thanks to God
        "تمام": 0.8,  # okay/good
        "بارك": 0.9,  # blessing (approval)
        "فخور": 0.9,  # proud
        "يسر": 0.8,  # facilitated (positive)
        "والله": 0.7,  # By God (emphasis)
        "ألف مبروك": 1.0,  # Congratulations
        "بهاء": 0.8,  # beautiful/nice
    }
    
    # Tunisian negative expressions
    TUNISIAN_NEGATIVE = {
        "ما تمام": -1.0,  # not okay
        "مشكل": -0.8,  # problem
        "ظلم": -0.9,  # injustice
        "كارثة": -1.0,  # catastrophe
        "تاع البلاغة": -0.9,  # nonsense
        "ما بهيش": -0.9,  # not right
        "الحرقة": -0.9,  # anger/fury
        "هادا ظلم": -1.0,  # this is unjust
        "خسارة": -0.8,  # shame/loss
        "مقرف": -1.0,  # disgusting
    }
    
    # Contextual modifiers
    INTENSIFIERS = ["برشا", "كتر", "كثير", "very", "so", "really"]
    NEGATORS = ["لا", "ما", "not", "no", "doesn't", "don't"]
    
    def analyze_tunisian(self, text: str) -> Dict[str, float]:
        """
        Analyze Tunisian dialect sentiment
        
        Returns:
            Dict with sentiment, score, and confidence
        """
        if not text:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "dialect_confidence": 0.0,
            }
        
        text_lower = text.lower()
        score = 0.0
        matched_keywords = []
        
        # Check positive expressions
        for expression, weight in self.TUNISIAN_POSITIVE.items():
            if expression in text_lower:
                # Check for intensifiers
                if any(intensifier in text_lower for intensifier in self.INTENSIFIERS):
                    score += weight * 1.3
                else:
                    score += weight
                matched_keywords.append((expression, weight))
        
        # Check negative expressions
        for expression, weight in self.TUNISIAN_NEGATIVE.items():
            if expression in text_lower:
                # Check for intensifiers
                if any(intensifier in text_lower for intensifier in self.INTENSIFIERS):
                    score += weight * 1.3
                else:
                    score += weight
                matched_keywords.append((expression, weight))
        
        # Normalize score
        score = max(-1.0, min(1.0, score / (len(text_lower) / 100)))
        
        # Determine sentiment
        if score > 0.2:
            sentiment = "positive"
            confidence = abs(score)
        elif score < -0.2:
            sentiment = "negative"
            confidence = abs(score)
        else:
            sentiment = "neutral"
            confidence = 1 - abs(score)
        
        # Dialect confidence based on matched keywords
        dialect_confidence = len(matched_keywords) / max(len(text_lower.split()), 1)
        
        return {
            "sentiment": sentiment,
            "score": score,
            "confidence": confidence,
            "dialect_confidence": dialect_confidence,
            "matched_expressions": [kw[0] for kw in matched_keywords],
        }
    
    def analyze_french(self, text: str) -> Dict[str, float]:
        """Analyze French sentiment"""
        french_positive = [
            "bien", "bon", "super", "excellent", "merveilleux",
            "fantastique", "génial", "awesome", "formidable"
        ]
        french_negative = [
            "mal", "mauvais", "horrible", "terrible", "nul",
            "catastrophe", "débâcle", "awful", "disgusting"
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for w in french_positive if w in text_lower)
        neg_count = sum(1 for w in french_negative if w in text_lower)
        
        score = pos_count - neg_count
        score = max(-1.0, min(1.0, score / max(len(text_lower.split()), 1)))
        
        if score > 0.2:
            return {"sentiment": "positive", "score": score, "confidence": abs(score)}
        elif score < -0.2:
            return {"sentiment": "negative", "score": score, "confidence": abs(score)}
        else:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 1.0}
    
    def analyze_arabic(self, text: str) -> Dict[str, float]:
        """Analyze Modern Standard Arabic sentiment"""
        msa_positive = [
            "ممتاز", "جميل", "رائع", "لطيف", "معجب",
            "فخور", "سعيد", "مسرور", "شاكر", "ممنون"
        ]
        msa_negative = [
            "سيء", "رديء", "كريه", "قبيح", "مكروه",
            "حزن", "أسف", "ندم", "غضب", "فشل"
        ]
        
        text_lower = text.lower()
        pos_count = sum(1 for w in msa_positive if w in text_lower)
        neg_count = sum(1 for w in msa_negative if w in text_lower)
        
        score = pos_count - neg_count
        score = max(-1.0, min(1.0, score / max(len(text_lower.split()), 1)))
        
        if score > 0.2:
            return {"sentiment": "positive", "score": score, "confidence": abs(score)}
        elif score < -0.2:
            return {"sentiment": "negative", "score": score, "confidence": abs(score)}
        else:
            return {"sentiment": "neutral", "score": 0.0, "confidence": 1.0}
    
    def analyze(self, text: str, language: Optional[str] = None) -> Dict[str, float]:
        """
        Analyze sentiment with language detection
        
        Args:
            text: Text to analyze
            language: Optional language hint (arabic, french, tunisian, mixed)
            
        Returns:
            Sentiment analysis result
        """
        if not text:
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
            }
        
        # If Tunisian is possible, try it first (most specific)
        if language is None or language in ["tunisian_dialect", "mixed", "arabic"]:
            result = self.analyze_tunisian(text)
            if result["dialect_confidence"] > 0.3:
                return result
        
        # Try based on language
        if language == "french":
            return self.analyze_french(text)
        elif language == "arabic":
            return self.analyze_arabic(text)
        
        # Fallback: detect based on content
        if "http" in text:
            # If has URLs, likely French/English content
            return self.analyze_french(text)
        else:
            # Default to Tunisian attempt
            result = self.analyze_tunisian(text)
            if result["dialect_confidence"] > 0:
                return result
            # Fallback to generic
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
            }
