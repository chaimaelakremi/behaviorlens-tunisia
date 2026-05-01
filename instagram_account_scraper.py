#!/usr/bin/env python3
"""
Instagram Scraper using Instagrapi (Regular Account)
⚠️ WARNING: This uses unofficial API - use with caution!
"""

import os
import json
import logging
from datetime import datetime
from instagrapi import Client
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class InstagramAccountScraper:
    """Scrape Instagram using regular account credentials"""
    
    def __init__(self, username: str, password: str):
        """
        Initialize Instagram client
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        try:
            self.cl = Client()
            logger.info(f"🔐 Logging in as {username}...")
            self.cl.login(username, password)
            logger.info(f"✅ Logged in successfully!")
            self.posts = []
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            logger.error(f"   Make sure username and password are correct")
            raise
    
    def scrape_hashtag(self, hashtag: str, limit: int = 20) -> List[Dict]:
        """
        Scrape posts from a hashtag
        
        Args:
            hashtag: Hashtag to scrape (without #)
            limit: Number of posts to get
        
        Returns:
            List of posts
        """
        try:
            logger.info(f"📸 Scraping #{hashtag}...")
            
            medias = self.cl.hashtag_medias_recent(hashtag, amount=limit)
            posts = []
            
            for media in medias:
                try:
                    post = {
                        "id": f"ig_{media.id}",
                        "text": media.caption or "",
                        "author": media.user.username,
                        "platform": "Instagram",
                        "url": f"https://instagram.com/p/{media.code}/",
                        "timestamp": media.taken_at.isoformat(),
                        "engagement": {
                            "likes": media.like_count,
                            "comments": media.comment_count,
                            "views": media.view_count
                        },
                        "hashtags": media.caption_hashtags if media.caption else [],
                        "media_type": media.media_type,
                        "source": "instagram_account"
                    }
                    posts.append(post)
                except Exception as e:
                    logger.debug(f"   Skipping post: {e}")
                    continue
            
            logger.info(f"   ✅ Got {len(posts)} posts from #{hashtag}")
            self.posts.extend(posts)
            return posts
        
        except Exception as e:
            logger.error(f"❌ Error scraping #{hashtag}: {e}")
            return []
    
    def scrape_user_posts(self, username: str, limit: int = 20) -> List[Dict]:
        """
        Scrape posts from a user
        
        Args:
            username: Instagram username (without @)
            limit: Number of posts
        
        Returns:
            List of posts
        """
        try:
            logger.info(f"📸 Scraping @{username}...")
            
            user = self.cl.user_info_by_username(username)
            medias = self.cl.user_medias(user.pk, amount=limit)
            posts = []
            
            for media in medias:
                try:
                    post = {
                        "id": f"ig_{media.id}",
                        "text": media.caption or "",
                        "author": username,
                        "platform": "Instagram",
                        "url": f"https://instagram.com/p/{media.code}/",
                        "timestamp": media.taken_at.isoformat(),
                        "engagement": {
                            "likes": media.like_count,
                            "comments": media.comment_count
                        },
                        "hashtags": media.caption_hashtags if media.caption else [],
                        "source": "instagram_account"
                    }
                    posts.append(post)
                except Exception as e:
                    logger.debug(f"   Skipping post: {e}")
                    continue
            
            logger.info(f"   ✅ Got {len(posts)} posts from @{username}")
            self.posts.extend(posts)
            return posts
        
        except Exception as e:
            logger.error(f"❌ Error scraping @{username}: {e}")
            return []
    
    def get_posts(self) -> List[Dict]:
        """Get all collected posts"""
        return self.posts
    
    def save_posts(self, filename: str = "data/instagram_posts.json"):
        """Save posts to file"""
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.posts)} posts to {filename}")


def main():
    """Main function"""
    print("\n" + "📱 " * 10)
    print("  Instagram Scraper (Account-Based)")
    print("📱 " * 10 + "\n")
    
    print("=" * 70)
    print("⚠️  IMPORTANT WARNINGS")
    print("=" * 70)
    
    print("\n🔴 Risks of Using Unofficial API:")
    print("   1. Account may be banned or locked")
    print("   2. Violates Instagram's Terms of Service")
    print("   3. Instagram actively blocks this library")
    print("   4. No official support or guarantees")
    print("   5. May require 2FA or verification")
    
    print("\n🟢 Safer Alternative: Official Graph API")
    print("   1. No account risk (uses app token)")
    print("   2. Legal and supported")
    print("   3. Unlimited rate limits")
    print("   4. Official Instagram support")
    print("   5. Takes only 5 minutes to setup")
    
    print("\n" + "=" * 70)
    print("📝 HOW TO USE THIS SCRIPT")
    print("=" * 70)
    
    print("\n1. Create environment variables (SAFE WAY):")
    print("   PowerShell:")
    print("   $env:IG_USERNAME='your_username'")
    print("   $env:IG_PASSWORD='your_password'")
    
    print("\n2. Or edit this script directly (NOT RECOMMENDED):")
    print("   username = 'your_instagram_username'")
    print("   password = 'your_instagram_password'")
    
    print("\n3. Then run:")
    print("   python instagram_account_scraper.py")
    
    print("\n" + "=" * 70)
    print("🚀 TRYING TO CONNECT...")
    print("=" * 70 + "\n")
    
    # Try to get credentials from environment
    username = os.getenv('IG_USERNAME')
    password = os.getenv('IG_PASSWORD')
    
    if not username or not password:
        print("\n❌ No Instagram credentials found!")
        print("\nTo use this script, set environment variables:")
        print("\n   $env:IG_USERNAME='your_username'")
        print("   $env:IG_PASSWORD='your_password'")
        print("   python instagram_account_scraper.py")
        
        print("\n" + "=" * 70)
        print("💡 RECOMMENDED: Use Official API Instead")
        print("=" * 70)
        
        print("\nIt's safer and easier:")
        print("   python graph_api_demo.py")
        print("\nOr follow: FACEBOOK_INSTAGRAM_API_GUIDE.md")
        return
    
    try:
        # Connect to Instagram
        scraper = InstagramAccountScraper(username, password)
        
        print("\n✅ Connected! Now collecting data...\n")
        
        # Scrape hashtags
        hashtags = ['tunisia', 'tunisie', 'tunis']
        for tag in hashtags:
            scraper.scrape_hashtag(tag, limit=10)
        
        # Save results
        scraper.save_posts()
        
        print(f"\n✅ Collected {len(scraper.get_posts())} posts total!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Tip: If login fails, try:")
        print("   1. Check username and password are correct")
        print("   2. Disable 2FA temporarily")
        print("   3. Try from a VPN (Instagram blocks scraping)")
        print("   4. Use Official Graph API instead (recommended)")


if __name__ == "__main__":
    main()
