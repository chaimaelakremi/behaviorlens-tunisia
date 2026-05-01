#!/usr/bin/env python3
"""
Advanced Web Scraper for Tunisian Social Media
Focuses on Twitter-like feeds and public social media content
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from typing import List, Dict
import time
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class SocialMediaScraper:
    """Web scraper for social media platforms"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.posts = []
    
    def scrape_twitter_like(self, username: str) -> List[Dict]:
        """
        Try to scrape Twitter-like content (limited due to API restrictions)
        This is a demonstration - actual Twitter scraping requires special setup
        """
        logger.info(f"📱 Note: Direct Twitter scraping requires API access")
        logger.info(f"   Alternative: Use Twitter's Official API or Academic Research API")
        return []
    
    def scrape_reddit_tunisia(self) -> List[Dict]:
        """Scrape Tunisia-related discussions from Reddit (public content)"""
        try:
            logger.info("🔍 Scraping Reddit Tunisia subreddit...")
            
            # Note: Reddit has rate limiting, this is for demonstration
            url = "https://www.reddit.com/r/Tunisia/top.json?t=week&limit=10"
            
            response = self.session.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                data = response.json()
                posts = []
                
                for item in data.get('data', {}).get('children', []):
                    try:
                        post_data = item['data']
                        
                        post = {
                            "id": f"reddit_{post_data['id']}",
                            "text": post_data['title'],
                            "author": post_data['author'],
                            "platform": "Reddit",
                            "source": "web_scraper",
                            "url": f"https://reddit.com{post_data['permalink']}",
                            "timestamp": datetime.fromtimestamp(post_data['created_utc']).isoformat(),
                            "sentiment": self._sentiment_analysis(post_data['title']),
                            "engagement": {
                                "upvotes": post_data['score'],
                                "comments": post_data['num_comments']
                            },
                            "post_type": "social"
                        }
                        posts.append(post)
                    except:
                        continue
                
                logger.info(f"   ✅ Extracted {len(posts)} posts from Reddit")
                self.posts.extend(posts)
                return posts
        
        except Exception as e:
            logger.info(f"   Note: Could not access Reddit (rate limited or blocked): {e}")
        
        return []
    
    def scrape_public_feeds(self) -> List[Dict]:
        """Scrape public RSS feeds and social media feeds"""
        feeds = [
            ("https://www.facebook.com/pages/Tunisia/...", "Facebook Tunisia Pages"),
            ("https://twitter.com/search?q=tunisia", "Twitter Tunisia"),
        ]
        
        posts = []
        for url, name in feeds:
            logger.info(f"📰 Note: {name} requires special API access")
        
        return posts
    
    def scrape_instagram_hashtags(self, hashtag: str = "tunisia") -> List[Dict]:
        """
        Note: Instagram scraping from browser is blocked
        Recommends using Instagram's official Graph API or third-party services
        """
        logger.info(f"📱 Instagram Scraping Note:")
        logger.info(f"   Direct scraping is blocked by Instagram")
        logger.info(f"   Recommended: Use Instagram Graph API (official)")
        logger.info(f"   Alternative: Use services like Apify or ScraperAPI")
        return []
    
    def _sentiment_analysis(self, text: str) -> str:
        """Analyze sentiment"""
        negative_words = ['crisis', 'problem', 'death', 'crisis', 'failed', 'bad', 'worst']
        positive_words = ['success', 'win', 'achievement', 'growth', 'good', 'best']
        
        text_lower = text.lower()
        
        neg = sum(1 for w in negative_words if w in text_lower)
        pos = sum(1 for w in positive_words if w in text_lower)
        
        if pos > neg:
            return "positive"
        elif neg > pos:
            return "negative"
        return "neutral"
    
    def get_all_posts(self) -> List[Dict]:
        return self.posts
    
    def save_posts(self, filename: str = "data/social_media_scraped.json"):
        import os
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.posts)} posts to {filename}")


def main():
    """Main function"""
    print("\n" + "📱 " * 10)
    print("  Advanced Social Media Scraper")
    print("📱 " * 10 + "\n")
    
    scraper = SocialMediaScraper()
    
    print("=" * 70)
    print("📋 AVAILABLE SCRAPING OPTIONS")
    print("=" * 70)
    
    print("\n1️⃣  NEWS SITES (Full Scraping) ✅")
    print("   Use: simple_web_scraper.py")
    print("   → Scrapes news content from Tunisian news websites")
    print("   → No restrictions, works immediately")
    
    print("\n2️⃣  REDDIT (Public Content) ⏱️")
    print("   Use: SocialMediaScraper.scrape_reddit_tunisia()")
    print("   → Scrapes public discussions from r/Tunisia")
    print("   → May have rate limiting")
    
    print("\n3️⃣  FACEBOOK / INSTAGRAM (Official API) 🔑")
    print("   Best Method: Use Graph API (official)")
    print("   See: graph_api_demo.py")
    print("   → Requires access token")
    print("   → Official & Reliable")
    print("   → Better permissions and rate limits")
    
    print("\n4️⃣  TWITTER (Official API) 🔑")
    print("   Best Method: Use Twitter API v2 (official)")
    print("   → Requires API keys")
    print("   → Academic Research tier available")
    
    print("\n5️⃣  INSTAGRAM HASHTAGS 📷")
    print("   Alternative Services:")
    print("   → Apify.com (cloud scraper)")
    print("   → ScraperAPI.com (rotating proxies)")
    print("   → Instazood / Instabot services")
    
    print("\n" + "=" * 70)
    print("🎯 RECOMMENDED WORKFLOW")
    print("=" * 70)
    
    print("\n✅ IMMEDIATE (No Setup):")
    print("   1. Run: python simple_web_scraper.py")
    print("      → Gets news from Tunisian news sites")
    print("      → 35+ posts in seconds")
    
    print("\n✅ EASY (5 minutes):")
    print("   1. Get Facebook/Instagram token")
    print("   2. Run: python graph_api_demo.py")
    print("      → Real social media data")
    print("      → Official API")
    
    print("\n✅ COMPREHENSIVE (All Data):")
    print("   1. Run simple_web_scraper.py (news)")
    print("   2. Use Graph API (Facebook/Instagram)")
    print("   3. Try Reddit scraping")
    print("      → Combined data from all sources")
    
    print("\n" + "=" * 70)
    print("⚠️  IMPORTANT NOTES")
    print("=" * 70)
    
    print("\n🔒 API Requirements (Better than Scraping):")
    print("   • Facebook/Instagram: Free with access token")
    print("   • Twitter: Academic tier available (free)")
    print("   • TikTok: Official API (application required)")
    
    print("\n⚙️ Why APIs are Better:")
    print("   ✓ Faster and more reliable")
    print("   ✓ Official rate limits & support")
    print("   ✓ Legal and compliant")
    print("   ✓ Better data quality")
    print("   ✓ Historical data access")
    
    print("\n🚫 Scraping Limitations:")
    print("   × Rate limiting and blocks")
    print("   × Terms of Service violations risk")
    print("   × IP blocking")
    print("   × Unreliable (sites change structure)")
    
    print("\n" + "=" * 70)
    print("📊 COLLECTING DATA...")
    print("=" * 70)
    
    # Try scraping Reddit
    logger.info("\n🔍 Attempting Reddit scrape...\n")
    reddit_posts = scraper.scrape_reddit_tunisia()
    if reddit_posts:
        logger.info(f"✅ Got {len(reddit_posts)} posts from Reddit")
    else:
        logger.info("⏱️  Reddit scrape returned no results (may be rate limited)")
    
    # Summary
    print("\n" + "=" * 70)
    print("📈 SUMMARY")
    print("=" * 70)
    
    print(f"\n📊 Total posts collected: {len(scraper.posts)}")
    print("\n📝 NEXT STEPS:")
    print("   1. For news: python simple_web_scraper.py")
    print("   2. For social media: python graph_api_demo.py")
    print("   3. For comprehensive: Combine both methods")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
