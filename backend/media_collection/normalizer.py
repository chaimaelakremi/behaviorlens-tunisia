"""
Data Normalizer
Standardizes all posts from different sources into a unified schema
"""

from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Standardizes all posts from different sources
    into a unified schema
    """
    
    REQUIRED_FIELDS = [
        "id", "text", "source", "platform",
        "author", "timestamp", "url", "metadata"
    ]
    
    @staticmethod
    def normalize(posts: List[Dict]) -> List[Dict]:
        """
        Ensure all posts match the schema
        
        Args:
            posts: raw posts from various sources
        
        Returns:
            Normalized posts matching the schema
        """
        normalized = []
        skipped = 0
        
        logger.info(f"Normalizing {len(posts)} posts...")
        
        for post in posts:
            try:
                normalized_post = DataNormalizer._validate_post(post)
                normalized.append(normalized_post)
            except Exception as e:
                logger.debug(f"Skipping post: {str(e)}")
                skipped += 1
                continue
        
        logger.info(f"✅ Normalization complete: {len(normalized)} valid | {skipped} skipped")
        
        return normalized
    
    @staticmethod
    def _validate_post(post: Dict) -> Dict:
        """
        Validate and fill missing fields with defaults
        
        Args:
            post: raw post dictionary
        
        Returns:
            Validated post matching schema
        
        Raises:
            ValueError: if post is invalid
        """
        validated = {}
        
        # Process each required field
        for field in DataNormalizer.REQUIRED_FIELDS:
            if field not in post or post[field] is None:
                # Provide sensible defaults
                if field == "metadata":
                    validated[field] = {
                        "category": "general",
                        "language": "unknown",
                        "confidence": 0.5
                    }
                elif field == "author":
                    validated[field] = "unknown"
                elif field == "platform":
                    validated[field] = "unknown"
                elif field == "source":
                    validated[field] = "unknown"
                elif field == "id":
                    import uuid
                    validated[field] = str(uuid.uuid4())
                elif field == "timestamp":
                    from datetime import datetime
                    validated[field] = datetime.now().isoformat()
                else:
                    validated[field] = None
            else:
                validated[field] = post[field]
        
        # Validate text is not empty and long enough
        text_str = str(validated["text"]).strip()
        if not text_str or len(text_str) < 5:
            raise ValueError("Text too short or empty")
        
        validated["text"] = text_str
        
        # Ensure metadata is dict
        if not isinstance(validated["metadata"], dict):
            validated["metadata"] = {
                "category": "general",
                "language": "unknown",
                "confidence": 0.5
            }
        
        # Validate metadata structure
        if "category" not in validated["metadata"]:
            validated["metadata"]["category"] = "general"
        if "language" not in validated["metadata"]:
            validated["metadata"]["language"] = "unknown"
        if "confidence" not in validated["metadata"]:
            validated["metadata"]["confidence"] = 0.5
        
        return validated
    
    @staticmethod
    def deduplicate(posts: List[Dict]) -> List[Dict]:
        """
        Remove duplicate posts (same text)
        
        Args:
            posts: list of posts
        
        Returns:
            List with duplicates removed
        """
        seen = set()
        unique = []
        duplicates = 0
        
        logger.info(f"Deduplicating {len(posts)} posts...")
        
        for post in posts:
            # Use text content as dedup key
            text_key = post["text"].lower().strip()
            text_hash = hash(text_key)
            
            if text_hash not in seen:
                seen.add(text_hash)
                unique.append(post)
            else:
                duplicates += 1
        
        logger.info(f"✅ Deduplication complete: {len(unique)} unique | {duplicates} duplicates removed")
        
        return unique
    
    @staticmethod
    def filter_by_language(posts: List[Dict], languages: List[str]) -> List[Dict]:
        """
        Filter posts by language
        
        Args:
            posts: list of posts
            languages: list of language codes to keep (ar, fr, en, mix)
        
        Returns:
            Filtered posts
        """
        filtered = [
            p for p in posts
            if p.get("metadata", {}).get("language") in languages
        ]
        
        logger.info(f"Filtered to {len(filtered)} posts matching languages: {languages}")
        
        return filtered
    
    @staticmethod
    def filter_by_category(posts: List[Dict], categories: List[str]) -> List[Dict]:
        """
        Filter posts by category
        
        Args:
            posts: list of posts
            categories: list of categories to keep
        
        Returns:
            Filtered posts
        """
        filtered = [
            p for p in posts
            if p.get("metadata", {}).get("category") in categories
        ]
        
        logger.info(f"Filtered to {len(filtered)} posts matching categories: {categories}")
        
        return filtered
    
    @staticmethod
    def filter_by_source(posts: List[Dict], sources: List[str]) -> List[Dict]:
        """
        Filter posts by source
        
        Args:
            posts: list of posts
            sources: list of sources to keep (rss, user_input, dataset)
        
        Returns:
            Filtered posts
        """
        filtered = [p for p in posts if p.get("source") in sources]
        
        logger.info(f"Filtered to {len(filtered)} posts from sources: {sources}")
        
        return filtered


# USAGE EXAMPLE
if __name__ == "__main__":
    # Test with sample data
    sample_posts = [
        {
            "text": "transport is bad",
            "source": "rss",
            "metadata": {"category": "transport", "language": "en"}
        },
        {
            "text": "transport is bad",  # duplicate
            "source": "user_input",
            "metadata": {"category": "transport", "language": "en"}
        },
        {
            "text": "el as3ar tal3et",
            "source": "dataset",
            "metadata": {"category": "prices", "language": "ar"}
        },
    ]
    
    print("\n" + "="*60)
    print("DATA NORMALIZER DEMO")
    print("="*60)
    
    # Normalize
    normalized = DataNormalizer.normalize(sample_posts)
    print(f"\nAfter normalization: {len(normalized)} posts")
    
    # Deduplicate
    unique = DataNormalizer.deduplicate(normalized)
    print(f"After deduplication: {len(unique)} posts")
    
    # Filter
    arabic_posts = DataNormalizer.filter_by_language(unique, ["ar", "mix"])
    print(f"Arabic/mixed posts: {len(arabic_posts)}")
