"""
Dataset Loader
Loads historical data from CSV files
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import random
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads historical data from CSV/Kaggle datasets"""
    
    def __init__(self, datasets_config: Dict):
        self.datasets = datasets_config
        self.posts = []
    
    def load_dataset(self, dataset_name: str) -> List[Dict]:
        """
        Load a single dataset file
        
        Args:
            dataset_name: name of dataset from config
        
        Returns:
            List of normalized posts
        """
        try:
            if dataset_name not in self.datasets:
                logger.error(f"❌ Dataset {dataset_name} not found in config")
                return []
            
            config = self.datasets[dataset_name]
            
            # Skip if not enabled
            if not config.get("enabled", True):
                logger.info(f"⏭️  Dataset {dataset_name} is disabled (skipping)")
                return []
            
            file_path = config["path"]
            
            # Check if file exists
            if not Path(file_path).exists():
                logger.warning(f"⚠️  Dataset file not found: {file_path}")
                logger.info(f"   Please download the dataset from Kaggle and place it at {file_path}")
                return []
            
            logger.info(f"📊 Loading dataset: {dataset_name}")
            
            # Load CSV
            df = pd.read_csv(file_path, encoding='utf-8')
            
            logger.info(f"   Loaded {len(df)} rows from CSV")
            
            posts = []
            
            for idx, row in df.iterrows():
                try:
                    # Get text content
                    text_col = config.get("text_column", "text")
                    if text_col not in row:
                        # Try common alternatives
                        for alt in ["content", "tweet", "comment", "message"]:
                            if alt in row:
                                text_col = alt
                                break
                    
                    text = str(row.get(text_col, "")).strip()
                    
                    if not text or len(text) < 5:
                        continue
                    
                    # Create timestamp spread over past 30 days
                    days_ago = random.randint(0, 30)
                    timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
                    
                    post = {
                        "id": f"dataset_{dataset_name}_{idx}",
                        "text": text,
                        "source": "dataset",
                        "platform": dataset_name,
                        "author": str(row.get("author", "dataset_user")),
                        "timestamp": timestamp,
                        "url": None,
                        "metadata": {
                            "category": str(row.get("category", "general")),
                            "language": self._detect_language_from_text(text),
                            "original_sentiment": row.get("sentiment", None),
                            "original_label": row.get("label", None),
                            "confidence": 0.75
                        }
                    }
                    posts.append(post)
                
                except Exception as e:
                    logger.debug(f"   Skipping row {idx}: {str(e)}")
                    continue
            
            logger.info(f"   ✅ Loaded {len(posts)} posts from {dataset_name}")
            self.posts.extend(posts)
            
            return posts
        
        except FileNotFoundError:
            logger.error(f"❌ Dataset file not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"❌ Error loading dataset {dataset_name}: {str(e)}")
            return []
    
    def load_all(self) -> List[Dict]:
        """
        Load all configured datasets
        
        Returns:
            All loaded posts
        """
        all_posts = []
        
        logger.info(f"Loading {len(self.datasets)} datasets...")
        
        for dataset_name in self.datasets.keys():
            posts = self.load_dataset(dataset_name)
            all_posts.extend(posts)
        
        logger.info(f"✅ Total dataset posts loaded: {len(all_posts)}")
        
        return all_posts
    
    def load_sample(self, sample_size: int = 100) -> List[Dict]:
        """
        Load random sample for quick demo
        
        Args:
            sample_size: number of posts to sample
        
        Returns:
            Random sample of posts
        """
        all_posts = self.load_all()
        
        if not all_posts:
            logger.warning("⚠️  No posts available to sample")
            return []
        
        sample = random.sample(all_posts, min(sample_size, len(all_posts)))
        logger.info(f"✅ Sampled {len(sample)} posts from dataset")
        
        return sample
    
    @staticmethod
    def _detect_language_from_text(text: str) -> str:
        """
        Detect language from text content
        
        Args:
            text: text to analyze
        
        Returns:
            Language code
        """
        from config import ARABIC_UNICODE_RANGE
        
        # Count Arabic characters
        arabic_count = sum(
            1 for c in text 
            if ARABIC_UNICODE_RANGE[0] <= ord(c) <= ARABIC_UNICODE_RANGE[1]
        )
        total_chars = len(text)
        
        if arabic_count > 0 and total_chars - arabic_count > 0:
            return "mix"
        elif arabic_count > total_chars * 0.5:
            return "ar"
        else:
            return "en"


# USAGE EXAMPLE
if __name__ == "__main__":
    from config import DATASETS
    
    loader = DatasetLoader(DATASETS)
    
    # Try to load sample
    print("\n" + "="*60)
    print("DATASET LOADER DEMO")
    print("="*60)
    
    posts = loader.load_sample(sample_size=50)
    
    if posts:
        print(f"\n✅ Loaded {len(posts)} sample posts")
        print("\nSample posts:")
        for post in posts[:3]:
            print(f"\n📊 {post['platform'].upper()}")
            print(f"   Text: {post['text'][:80]}...")
            print(f"   Language: {post['metadata']['language']}")
    else:
        print("\n⚠️  No datasets available yet.")
        print("   To use datasets, download from Kaggle:")
        print("   1. https://www.kaggle.com/datasets/kazanova/sentiment140")
        print("   2. Place CSV files in data/raw/datasets/")
        print("   3. Enable in config.py")
