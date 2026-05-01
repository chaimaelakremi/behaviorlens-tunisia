"""
Media Collection Pipeline Orchestrator
Manages the complete media collection workflow
"""

from .sources.rss_collector import RSSCollector
from .sources.user_input_collector import UserInputCollector
from .sources.dataset_loader import DatasetLoader
from .normalizer import DataNormalizer
from .storage import StorageManager
from .config import RSS_FEEDS, DATASETS, STORAGE_TYPE, STORAGE_PATH

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MediaCollectionPipeline:
    """
    Main orchestrator for all media collection
    
    Workflow:
    1. Collect from RSS feeds
    2. Collect from user input (optional)
    3. Load from datasets
    4. Normalize all data to unified schema
    5. Deduplicate
    6. Save to storage
    """
    
    def __init__(self):
        self.rss_collector = RSSCollector(RSS_FEEDS)
        self.user_collector = UserInputCollector()
        self.dataset_loader = DatasetLoader(DATASETS)
        self.storage = StorageManager(STORAGE_TYPE, STORAGE_PATH)
        
        logger.info("✅ MediaCollectionPipeline initialized")
    
    def collect_all(self, include_rss=True, include_user=False, include_datasets=True) -> list:
        """
        Collect from all sources
        
        Args:
            include_rss: whether to collect from RSS feeds
            include_user: whether to collect from user input (interactive)
            include_datasets: whether to load from datasets
        
        Returns:
            List of all collected and normalized posts
        """
        logger.info("\n" + "="*70)
        logger.info("🚀 STARTING MEDIA COLLECTION PIPELINE")
        logger.info("="*70)
        
        all_posts = []
        
        # 1️⃣ COLLECT FROM RSS FEEDS
        if include_rss:
            logger.info("\n📰 Phase 1: RSS Collection")
            logger.info("-" * 70)
            rss_posts = self.rss_collector.collect_all()
            all_posts.extend(rss_posts)
            logger.info(f"✅ RSS: {len(rss_posts)} posts collected\n")
        
        # 2️⃣ COLLECT FROM USER INPUT
        if include_user:
            logger.info("\n🎤 Phase 2: User Input Collection")
            logger.info("-" * 70)
            user_posts = self.user_collector.collect_from_cli(batch_size=3)
            all_posts.extend(user_posts)
            logger.info(f"✅ User Input: {len(user_posts)} opinions collected\n")
        
        # 3️⃣ LOAD FROM DATASETS
        if include_datasets:
            logger.info("\n📊 Phase 3: Dataset Loading")
            logger.info("-" * 70)
            dataset_posts = self.dataset_loader.load_sample(sample_size=100)
            all_posts.extend(dataset_posts)
            logger.info(f"✅ Datasets: {len(dataset_posts)} posts loaded\n")
        
        # 4️⃣ COMBINE & REPORT
        logger.info("\n🔄 Phase 4: Combining Data")
        logger.info("-" * 70)
        logger.info(f"📊 Total posts before processing: {len(all_posts)}")
        
        # 5️⃣ NORMALIZE
        logger.info("\n⚙️  Phase 5: Normalization")
        logger.info("-" * 70)
        normalized_posts = DataNormalizer.normalize(all_posts)
        
        # 6️⃣ DEDUPLICATE
        logger.info("\n🔍 Phase 6: Deduplication")
        logger.info("-" * 70)
        unique_posts = DataNormalizer.deduplicate(normalized_posts)
        
        # 7️⃣ SAVE TO STORAGE
        logger.info("\n💾 Phase 7: Storage")
        logger.info("-" * 70)
        self.storage.save(unique_posts)
        
        # 📈 FINAL REPORT
        logger.info("\n" + "="*70)
        logger.info("✅ COLLECTION PIPELINE COMPLETE")
        logger.info("="*70)
        logger.info(f"📊 FINAL STATISTICS")
        logger.info("-" * 70)
        stats = self.storage.get_stats()
        logger.info(f"  Total posts: {stats['total_posts']}")
        logger.info(f"  By source: {stats['by_source']}")
        logger.info(f"  By category: {stats['by_category']}")
        logger.info(f"  By language: {stats['by_language']}")
        logger.info("="*70 + "\n")
        
        return unique_posts
    
    def collect_incremental(self, new_posts: list):
        """
        Add new posts to existing collection
        
        Args:
            new_posts: list of new posts to add
        """
        logger.info(f"Adding {len(new_posts)} new posts to collection...")
        
        # Normalize new posts
        normalized = DataNormalizer.normalize(new_posts)
        
        # Append to storage (deduplication happens inside append)
        self.storage.append(normalized)
        
        logger.info("✅ Posts added successfully")
    
    def get_posts(self, filters=None) -> list:
        """
        Get posts with optional filters
        
        Args:
            filters: dict with keys like 'source', 'category', 'language'
        
        Returns:
            Filtered posts
        """
        posts = self.storage.load()
        
        if not filters:
            return posts
        
        # Apply filters
        if "source" in filters:
            posts = [p for p in posts if p.get("source") == filters["source"]]
        
        if "category" in filters:
            posts = [
                p for p in posts
                if p.get("metadata", {}).get("category") == filters["category"]
            ]
        
        if "language" in filters:
            posts = [
                p for p in posts
                if p.get("metadata", {}).get("language") == filters["language"]
            ]
        
        return posts
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        return self.storage.get_stats()
    
    def export(self, filename: str):
        """Export posts to file"""
        posts = self.storage.load()
        self.storage = StorageManager("json", filename)
        self.storage.save(posts)
        logger.info(f"✅ Exported {len(posts)} posts to {filename}")


# ===== MAIN ENTRY POINT =====
if __name__ == "__main__":
    # Create pipeline
    pipeline = MediaCollectionPipeline()
    
    # Collect all data
    #  Options:
    # - include_rss=True (real RSS news)
    # - include_user=False (skip interactive input for auto demo)
    # - include_datasets=True (load sample datasets)
    posts = pipeline.collect_all(
        include_rss=True,
        include_user=False,  # Set to True for interactive demo
        include_datasets=True
    )
    
    # Display sample posts
    print("\n" + "="*70)
    print("📋 SAMPLE COLLECTED POSTS")
    print("="*70)
    
    for i, post in enumerate(posts[:5]):
        print(f"\n{i+1}. {post['source'].upper()} | {post['platform']}")
        print(f"   Author: {post['author']}")
        print(f"   Text: {post['text'][:80]}...")
        print(f"   Category: {post['metadata']['category']} | Language: {post['metadata']['language']}")
        print(f"   Confidence: {post['metadata']['confidence']}")
    
    print("\n" + "="*70)
    print("✅ Media collection complete!")
    print(f"📂 Data saved to: {STORAGE_PATH}")
    print("="*70 + "\n")
