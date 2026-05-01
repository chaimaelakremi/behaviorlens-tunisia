"""
Social Media Collection System - Main Entry Point
Run with: python -m social_media
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from social_media.app import SocialMediaCollector
from social_media.utils import print_collection_summary, setup_logging
from social_media.config import get_config_summary

logger = setup_logging()


def print_header():
    """Print welcome header"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🌍 SOCIAL MEDIA INTELLIGENCE COLLECTOR 🌍          ║
║                                                              ║
║              Real-time Tunisian Social Insights              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def print_menu():
    """Print main menu"""
    print("""
┌──────────────────────────────────────────────────────────────┐
│                      MAIN MENU                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Run Full Collection Pipeline                            │
│  2. Collect from Specific Platform                          │
│  3. Show Statistics                                         │
│  4. Export Data                                             │
│  5. Run Examples                                            │
│  6. Show Configuration                                      │
│                                                              │
│  0. Exit                                                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
    """)


def menu_collect_full():
    """Menu option 1: Run full collection"""
    print("\n📡 Running Full Collection Pipeline...\n")
    
    collector = SocialMediaCollector()
    result = collector.run_collection_pipeline()
    
    if result.get("success"):
        print_collection_summary(result)
    else:
        print(f"❌ Error: {result.get('message')}")


def menu_collect_platform():
    """Menu option 2: Collect from specific platform"""
    print("\n📱 Available Platforms:")
    
    from social_media.config import SOCIAL_MEDIA_CONFIG
    
    platforms = [
        (name, config)
        for name, config in SOCIAL_MEDIA_CONFIG.items()
        if config.get("enabled", False)
    ]
    
    for i, (name, config) in enumerate(platforms, 1):
        print(f"  {i}. {name} - {config.get('description', 'N/A')}")
    
    choice = input("\nSelect platform (number): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(platforms):
            platform_name, _ = platforms[idx]
            
            print(f"\n🔄 Collecting from {platform_name}...\n")
            
            collector = SocialMediaCollector()
            posts = collector.collect_from_platform(platform_name)
            
            print(f"✓ Collected {len(posts)} posts")
            
            if posts:
                print("\nSample posts:")
                for i, post in enumerate(posts[:3], 1):
                    print(f"\n{i}. From @{post.get('author')}")
                    print(f"   Text: {post.get('text', '')[:100]}...")
                    print(f"   Sentiment: {post.get('metadata', {}).get('sentiment')}")
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Invalid input")


def menu_stats():
    """Menu option 3: Show statistics"""
    print("\n📊 Loading Statistics...\n")
    
    collector = SocialMediaCollector()
    
    # First check if we have data
    try:
        stats = collector.get_stats()
        
        if stats.get("total", 0) == 0:
            print("⚠️  No posts found. Run collection first.")
            return
        
        print(f"Total posts: {stats.get('total', 0)}\n")
        
        print("📱 By Platform:")
        for platform, count in sorted(stats.get("by_platform", {}).items()):
            print(f"  {platform}: {count}")
        
        print("\n📂 By Category:")
        for category, count in sorted(stats.get("by_category", {}).items()):
            print(f"  {category}: {count}")
        
        print("\n🗣️  By Language:")
        for lang, count in sorted(stats.get("by_language", {}).items()):
            print(f"  {lang}: {count}")
        
        print("\n💭 Sentiment Distribution:")
        sentiment = stats.get("sentiment_distribution", {})
        total = sum(sentiment.values())
        for sent_type, count in sentiment.items():
            pct = (count / total * 100) if total > 0 else 0
            print(f"  {sent_type}: {count} ({pct:.1f}%)")
        
        print("\n#️⃣  Top 5 Hashtags:")
        for hashtag, count in stats.get("top_hashtags", [])[:5]:
            print(f"  {hashtag}: {count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def menu_export():
    """Menu option 4: Export data"""
    print("\n📤 Export Options:")
    print("  1. JSON")
    print("  2. CSV")
    
    choice = input("\nSelect format: ").strip()
    
    format_map = {"1": "json", "2": "csv"}
    
    if choice in format_map:
        fmt = format_map[choice]
        
        output_file = input(f"Output file (press Enter for default): ").strip()
        if not output_file:
            output_file = None
        
        collector = SocialMediaCollector()
        
        try:
            output = collector.export_posts(format=fmt, output_file=output_file)
            print(f"\n✓ Exported to: {output}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    else:
        print("❌ Invalid choice")


def menu_examples():
    """Menu option 5: Run examples"""
    print("\n📚 Available Examples:")
    
    examples = {
        "1": "Basic Collection Pipeline",
        "2": "Platform-Specific Collection",
        "3": "Statistics and Analysis",
        "4": "Export to Different Formats",
        "5": "Sentiment Analysis",
        "6": "Real-Time Monitoring Loop",
        "7": "Category Tracking",
        "8": "Language Detection",
    }
    
    for key, name in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example: ").strip()
    
    if choice in examples:
        from social_media import examples as ex_module
        
        try:
            ex_module.run_examples()
        except Exception as e:
            print(f"❌ Error running example: {e}")
    else:
        print("❌ Invalid choice")


def menu_config():
    """Menu option 6: Show configuration"""
    print("\n⚙️  Configuration Summary:\n")
    
    config = get_config_summary()
    
    for key, value in config.items():
        if isinstance(value, list):
            print(f"{key}:")
            for item in value:
                print(f"  - {item}")
        else:
            print(f"{key}: {value}")
    
    print("\n📂 Data Directory:", config.get("data_dir", "N/A"))


def main():
    """Main entry point"""
    print_header()
    
    while True:
        print_menu()
        choice = input("Select option: ").strip()
        
        if choice == "1":
            menu_collect_full()
        elif choice == "2":
            menu_collect_platform()
        elif choice == "3":
            menu_stats()
        elif choice == "4":
            menu_export()
        elif choice == "5":
            menu_examples()
        elif choice == "6":
            menu_config()
        elif choice == "0":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Please try again.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user\n")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)
