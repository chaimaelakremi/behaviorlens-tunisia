"""
Example scripts demonstrating the Social Media Collection System
Run with: python -m social_media.examples.<example_name>
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from social_media.app import SocialMediaCollector
from social_media.config import get_config_summary
from social_media.utils import print_collection_summary


def example_1_basic_collection():
    """
    Example 1: Basic Collection
    Run the default collection pipeline and show results
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Collection Pipeline")
    print("="*60 + "\n")
    
    # Initialize collector
    collector = SocialMediaCollector()
    
    # Show configuration
    print("📋 Configuration Summary:")
    config = get_config_summary()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # Run collection
    print("\n🚀 Running collection pipeline...")
    result = collector.run_collection_pipeline()
    
    # Show results
    print_collection_summary(result)


def example_2_platform_specific():
    """
    Example 2: Collect from Specific Platforms
    Demonstrate collecting from individual platforms
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Platform-Specific Collection")
    print("="*60 + "\n")
    
    collector = SocialMediaCollector()
    
    platforms = ["twitter_rss", "facebook_pages", "instagram_hashtags", "reddit_communities"]
    
    for platform in platforms:
        print(f"\n📱 Collecting from {platform}...")
        posts = collector.collect_from_platform(platform)
        
        if posts:
            print(f"  ✓ Collected {len(posts)} posts")
            if posts:
                print(f"  Sample: {posts[0]['text'][:80]}...")
        else:
            print(f"  ✗ No posts collected")


def example_3_statistics_analysis():
    """
    Example 3: Statistics and Analysis
    Show detailed statistics about collected posts
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Statistics and Analysis")
    print("="*60 + "\n")
    
    collector = SocialMediaCollector()
    
    # Run collection
    print("Collecting posts...")
    collector.run_collection_pipeline()
    
    # Get statistics
    print("\nGenerating statistics...")
    stats = collector.get_stats()
    
    # Display statistics
    print("\n📊 DETAILED STATISTICS:")
    print(f"Total posts: {stats.get('total', 0)}")
    
    print(f"\n📱 Posts by Platform:")
    for platform, count in sorted(stats.get("by_platform", {}).items()):
        print(f"  {platform}: {count}")
    
    print(f"\n📂 Posts by Category:")
    for category, count in sorted(stats.get("by_category", {}).items()):
        print(f"  {category}: {count}")
    
    print(f"\n🗣️  Languages Detected:")
    for language, count in sorted(stats.get("by_language", {}).items()):
        print(f"  {language}: {count}")
    
    print(f"\n💭 Sentiment Distribution:")
    sentiment = stats.get("sentiment_distribution", {})
    total_sentiment = sum(sentiment.values())
    for sent_type, count in sentiment.items():
        percentage = (count / total_sentiment * 100) if total_sentiment > 0 else 0
        print(f"  {sent_type}: {count} ({percentage:.1f}%)")
    
    print(f"\n#️⃣  Top 5 Hashtags:")
    for hashtag, count in stats.get("top_hashtags", [])[:5]:
        print(f"  {hashtag}: {count} mentions")
    
    print(f"\n👥 Top 5 Mentions:")
    for mention, count in stats.get("top_mentions", [])[:5]:
        print(f"  {mention}: {count} mentions")


def example_4_export_formats():
    """
    Example 4: Export in Different Formats
    Demonstrate exporting to JSON and CSV
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Export to Different Formats")
    print("="*60 + "\n")
    
    collector = SocialMediaCollector()
    
    # Run collection
    print("Collecting posts...")
    collector.run_collection_pipeline()
    
    # Export to JSON
    print("\n📄 Exporting to JSON...")
    json_file = collector.export_posts(format="json")
    print(f"  ✓ Saved to: {json_file}")
    
    # Export to CSV
    print("\n📊 Exporting to CSV...")
    csv_file = collector.export_posts(format="csv")
    print(f"  ✓ Saved to: {csv_file}")


def example_5_sentiment_analysis():
    """
    Example 5: Sentiment Analysis
    Demonstrate sentiment analysis on collected posts
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Sentiment Analysis")
    print("="*60 + "\n")
    
    collector = SocialMediaCollector()
    
    # Run collection
    print("Collecting posts...")
    collector.run_collection_pipeline()
    
    # Get posts
    posts = collector.storage.load()
    
    # Analyze sentiment
    print("\n💭 Sentiment Analysis:")
    print(f"Total posts: {len(posts)}")
    
    positive = sum(1 for p in posts if p.get("metadata", {}).get("sentiment") == "positive")
    negative = sum(1 for p in posts if p.get("metadata", {}).get("sentiment") == "negative")
    neutral = sum(1 for p in posts if p.get("metadata", {}).get("sentiment") == "neutral")
    
    print(f"  Positive: {positive} ({positive/len(posts)*100:.1f}%)")
    print(f"  Negative: {negative} ({negative/len(posts)*100:.1f}%)")
    print(f"  Neutral: {neutral} ({neutral/len(posts)*100:.1f}%)")
    
    print("\n📌 Sample Negative Posts:")
    neg_posts = [p for p in posts if p.get("metadata", {}).get("sentiment") == "negative"]
    for i, post in enumerate(neg_posts[:3], 1):
        print(f"\n  {i}. From {post.get('platform')} (@{post.get('author')})")
        print(f"     Text: {post.get('text')[:100]}...")
        print(f"     Category: {post.get('metadata', {}).get('category')}")


def example_6_real_time_monitoring():
    """
    Example 6: Real-Time Monitoring Loop
    Demonstrate continuous monitoring (run for specified duration)
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Real-Time Monitoring Loop")
    print("="*60 + "\n")
    
    import time
    
    collector = SocialMediaCollector()
    
    print("Starting monitoring loop...")
    print("(Press Ctrl+C to stop)\n")
    
    cycle = 1
    try:
        while True:
            print(f"\n📡 Collection Cycle {cycle} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
            # Run collection
            result = collector.run_collection_pipeline()
            
            # Get stats
            stats = collector.get_stats()
            
            # Display key metrics
            print(f"✓ Total posts collected: {result['total_posts']}")
            print(f"✓ By platform: {stats.get('by_platform', {})}")
            print(f"✓ Sentiment: {stats.get('sentiment_distribution', {})}")
            
            cycle += 1
            
            # Wait before next cycle (in demo, just do one cycle)
            print(f"\nNext cycle in 60 seconds... (Press Ctrl+C to stop)")
            # time.sleep(60)  # Uncomment for real monitoring
            break
    
    except KeyboardInterrupt:
        print("\n\n✓ Monitoring stopped")


def example_7_category_tracking():
    """
    Example 7: Track Posts by Category
    Show distribution across different topics
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Category Tracking")
    print("="*60 + "\n")
    
    collector = SocialMediaCollector()
    
    # Run collection
    print("Collecting posts...")
    collector.run_collection_pipeline()
    
    # Get posts and group by category
    posts = collector.storage.load()
    
    print(f"\nTotal posts: {len(posts)}")
    print("\n📂 Posts by Category:")
    print("-" * 40)
    
    categories = {}
    for post in posts:
        category = post.get("metadata", {}).get("category", "uncategorized")
        if category not in categories:
            categories[category] = []
        categories[category].append(post)
    
    for category in sorted(categories.keys()):
        posts_in_cat = categories[category]
        print(f"\n{category.upper()} ({len(posts_in_cat)} posts)")
        
        for post in posts_in_cat[:2]:  # Show first 2
            text = post.get("text", "")[:70]
            print(f"  • {text}...")


def example_8_language_detection():
    """
    Example 8: Language Detection
    Show distribution of detected languages
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: Language Detection")
    print("="*60 + "\n")
    
    collector = SocialMediaCollector()
    
    # Run collection
    print("Collecting posts...")
    collector.run_collection_pipeline()
    
    # Get posts
    posts = collector.storage.load()
    
    # Count by language
    languages = {}
    for post in posts:
        lang = post.get("metadata", {}).get("language", "unknown")
        languages[lang] = languages.get(lang, 0) + 1
    
    print(f"\nTotal posts: {len(posts)}")
    print("\n🗣️  Languages Detected:")
    print("-" * 40)
    
    for lang in sorted(languages.keys()):
        count = languages[lang]
        percentage = (count / len(posts) * 100) if posts else 0
        print(f"{lang:10} {count:3} posts ({percentage:5.1f}%)")


# Run examples menu
def run_examples():
    """Interactive examples menu"""
    examples = {
        "1": ("Basic Collection Pipeline", example_1_basic_collection),
        "2": ("Platform-Specific Collection", example_2_platform_specific),
        "3": ("Statistics and Analysis", example_3_statistics_analysis),
        "4": ("Export to Different Formats", example_4_export_formats),
        "5": ("Sentiment Analysis", example_5_sentiment_analysis),
        "6": ("Real-Time Monitoring Loop", example_6_real_time_monitoring),
        "7": ("Category Tracking", example_7_category_tracking),
        "8": ("Language Detection", example_8_language_detection),
    }
    
    print("\n" + "="*60)
    print("SOCIAL MEDIA COLLECTION - EXAMPLES")
    print("="*60)
    print("\nAvailable Examples:")
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\n  0. Run All Examples")
    print("  q. Quit")
    
    choice = input("\nSelect example (0-8, q): ").strip()
    
    if choice == "0":
        for key in sorted(examples.keys()):
            try:
                examples[key][1]()
            except Exception as e:
                print(f"Error running example: {e}")
    elif choice in examples:
        try:
            examples[choice][1]()
        except Exception as e:
            print(f"Error running example: {e}")
    elif choice == "q":
        print("Goodbye!")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples = {
            "1": example_1_basic_collection,
            "2": example_2_platform_specific,
            "3": example_3_statistics_analysis,
            "4": example_4_export_formats,
            "5": example_5_sentiment_analysis,
            "6": example_6_real_time_monitoring,
            "7": example_7_category_tracking,
            "8": example_8_language_detection,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Unknown example: {example_num}")
            print("Available: 1-8")
    else:
        # Run interactive menu
        run_examples()
