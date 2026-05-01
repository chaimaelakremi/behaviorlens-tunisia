#!/usr/bin/env python3
"""
Quick test script to run social media collection and show extracted data
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    try:
        from social_media.app import SocialMediaCollector
        from social_media.utils import setup_logging
        
        logger = setup_logging()
        logger.info("=" * 80)
        logger.info("BEHAVIORLENS - Social Media Collection & Analysis")
        logger.info("=" * 80)
        
        # Initialize collector
        logger.info("\n[1/4] Initializing collector...")
        collector = SocialMediaCollector()
        
        # Run collection pipeline
        logger.info("[2/4] Running collection pipeline...")
        result = collector.run_collection_pipeline()
        
        logger.info(f"[3/4] Collection complete! Collected {len(result)} posts total")
        
        # Get statistics
        logger.info("\n[4/4] Generating statistics...")
        stats = collector.get_stats()
        
        # Display results
        print("\n" + "=" * 80)
        print("COLLECTION RESULTS")
        print("=" * 80)
        
        print(f"\nTotal Posts Collected: {stats['total_posts']}")
        print(f"\nBreakdown by Source:")
        for source, count in stats['by_source'].items():
            print(f"  • {source}: {count} posts")
        
        print(f"\nBreakdown by Sentiment:")
        for sentiment, count in stats['by_sentiment'].items():
            print(f"  • {sentiment.capitalize()}: {count} posts")
        
        print(f"\nBreakdown by Language:")
        for lang, count in stats['by_language'].items():
            print(f"  • {lang.upper()}: {count} posts")
        
        print(f"\nBreakdown by Category:")
        for category, count in stats['by_category'].items():
            print(f"  • {category}: {count} posts")
        
        # Show sample posts
        print("\n" + "=" * 80)
        print("SAMPLE EXTRACTED DATA (First 3 Posts)")
        print("=" * 80)
        
        posts = collector.storage.load()
        for i, post in enumerate(posts[:3], 1):
            print(f"\n--- POST {i} ---")
            print(f"Source: {post.get('source', 'N/A')}")
            print(f"Platform: {post.get('platform', 'N/A')}")
            print(f"Author: {post.get('author', 'N/A')}")
            print(f"Text: {post.get('text', 'N/A')[:100]}...")
            print(f"Sentiment: {post.get('metadata', {}).get('sentiment', 'N/A')}")
            print(f"Language: {post.get('metadata', {}).get('language', 'N/A')}")
            print(f"Category: {post.get('metadata', {}).get('category', 'N/A')}")
            print(f"Timestamp: {post.get('timestamp', 'N/A')}")
            
            comments = post.get('metadata', {}).get('comments', [])
            if comments:
                print(f"Comments ({len(comments)}):")
                for j, comment in enumerate(comments[:2], 1):
                    print(f"  {j}. {comment['text'][:80]}...")
        
        # Save to JSON file for inspection
        output_file = Path(__file__).parent / "data" / "demo_output.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(posts[:5], f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Full data saved to: {output_file}")
        print("\n" + "=" * 80)
        print("SUCCESS - Data extraction complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
