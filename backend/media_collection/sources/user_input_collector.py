"""
User Input Collector
Collects opinions directly from users
"""

from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserInputCollector:
    """Collects opinions directly from users via CLI or web forms"""
    
    def __init__(self):
        self.posts = []
        self.input_methods = ["cli", "web_form"]
    
    def collect_from_cli(self, batch_size: int = 5) -> List[Dict]:
        """
        Interactive CLI input for demo / manual testing
        
        Args:
            batch_size: number of opinions to collect
        
        Returns:
            List of user-generated posts
        """
        logger.info(f"Starting CLI input collection ({batch_size} opinions)...")
        
        posts = []
        
        print("\n" + "="*70)
        print("🎤 BEHAVIORLENS - OPINION COLLECTOR")
        print("="*70)
        print("📝 What do you think about Tunisia today?")
        print("   Topics: transport, prices, jobs, politics, education")
        print("   Languages: Arabic, French, or mix")
        print("   (Press Enter twice to skip an opinion)")
        print("="*70)
        
        for i in range(batch_size):
            print(f"\n📝 Opinion #{i+1} out of {batch_size}:")
            print("   > ", end="", flush=True)
            
            text = input().strip()
            
            if not text or len(text) < 5:
                logger.debug(f"  Skipped opinion #{i+1} (too short or empty)")
                continue
            
            # Auto-detect category
            category = self._detect_category(text)
            language = self._detect_language(text)
            
            post = {
                "id": f"user_input_{datetime.now().timestamp()}_{i}",
                "text": text,
                "source": "user_input",
                "platform": "cli",
                "author": "user",
                "timestamp": datetime.now().isoformat(),
                "url": None,
                "metadata": {
                    "category": category,
                    "language": language,
                    "confidence": 0.85
                }
            }
            
            posts.append(post)
            logger.info(f"  ✅ Opinion #{i+1} collected | Category: {category} | Lang: {language}")
        
        self.posts.extend(posts)
        logger.info(f"✅ CLI collection complete: {len(posts)} opinions collected")
        
        return posts
    
    def collect_from_web_form(self, form_data: Dict) -> Dict:
        """
        Collect from web form submission
        
        Expected form_data:
        {
            "text": "opinion text",
            "category": "transport",
            "location": "Tunis",
            "name": "user_name"  (optional)
        }
        
        Args:
            form_data: form submission data
        
        Returns:
            Normalized post dictionary
        """
        text = form_data.get("text", "").strip()
        
        if not text or len(text) < 5:
            logger.warning("Form submission rejected: text too short")
            return None
        
        post = {
            "id": f"user_input_{datetime.now().timestamp()}",
            "text": text,
            "source": "user_input",
            "platform": "web_form",
            "author": form_data.get("name", "anonymous"),
            "timestamp": datetime.now().isoformat(),
            "url": None,
            "metadata": {
                "category": form_data.get("category", self._detect_category(text)),
                "language": self._detect_language(text),
                "location": form_data.get("location", "unknown"),
                "confidence": 0.85
            }
        }
        
        self.posts.append(post)
        logger.info(f"✅ Web form opinion collected | Category: {post['metadata']['category']}")
        
        return post
    
    def collect_from_list(self, texts: List[str]) -> List[Dict]:
        """
        Batch collect from a list of texts
        
        Args:
            texts: list of opinion texts
        
        Returns:
            List of posts
        """
        posts = []
        
        for i, text in enumerate(texts):
            if not text or len(text) < 5:
                continue
            
            post = {
                "id": f"user_input_batch_{i}_{datetime.now().timestamp()}",
                "text": text,
                "source": "user_input",
                "platform": "batch",
                "author": "batch_user",
                "timestamp": datetime.now().isoformat(),
                "url": None,
                "metadata": {
                    "category": self._detect_category(text),
                    "language": self._detect_language(text),
                    "confidence": 0.80
                }
            }
            posts.append(post)
        
        self.posts.extend(posts)
        logger.info(f"✅ Batch collection: {len(posts)} opinions processed")
        
        return posts
    
    @staticmethod
    def _detect_category(text: str) -> str:
        """
        Simple keyword-based category detection
        
        Args:
            text: opinion text
        
        Returns:
            Detected category
        """
        from config import CATEGORY_KEYWORDS
        
        text_lower = text.lower()
        
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return "general"
    
    @staticmethod
    def _detect_language(text: str) -> str:
        """
        Simple language detection
        
        Args:
            text: opinion text
        
        Returns:
            Language code (ar, fr, en, mix)
        """
        from config import ARABIC_UNICODE_RANGE
        
        # Count Arabic characters
        arabic_count = sum(1 for c in text if ARABIC_UNICODE_RANGE[0] <= ord(c) <= ARABIC_UNICODE_RANGE[1])
        total_chars = len(text)
        
        # Determine language
        if arabic_count > 0 and total_chars - arabic_count > 0:
            return "mix"  # Mix of Arabic and other
        elif arabic_count > total_chars * 0.5:
            return "ar"   # Predominantly Arabic
        else:
            return "fr"   # Default to French/other


# USAGE EXAMPLES
if __name__ == "__main__":
    collector = UserInputCollector()
    
    # Example 1: CLI Collection
    print("\n=== CLI COLLECTION EXAMPLE ===")
    posts_cli = collector.collect_from_cli(batch_size=2)
    
    # Example 2: Web Form Collection
    print("\n=== WEB FORM COLLECTION EXAMPLE ===")
    form_data = {
        "text": "transport fi tounes 3ayech barcha 😡",
        "category": "transport",
        "location": "Tunis",
        "name": "Ali"
    }
    post_form = collector.collect_from_web_form(form_data)
    
    # Example 3: Batch Collection
    print("\n=== BATCH COLLECTION EXAMPLE ===")
    opinions = [
        "prices are increasing too fast",
        "el khdem ma fama",
        "service public wala behi"
    ]
    posts_batch = collector.collect_from_list(opinions)
    
    # Display results
    print("\n" + "="*70)
    print("COLLECTED OPINIONS")
    print("="*70)
    
    all_posts = posts_cli + ([post_form] if post_form else []) + posts_batch
    
    for post in all_posts:
        if post:
            print(f"\n📝 {post['author'].upper()}")
            print(f"   Text: {post['text']}")
            print(f"   Category: {post['metadata']['category']}")
            print(f"   Language: {post['metadata']['language']}")
