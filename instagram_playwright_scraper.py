#!/usr/bin/env python3
"""
Instagram Scraper with Playwright (Account-Based)
Automates browser login and scraping
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import os

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class InstagramPlaywrightScraper:
    """Scrape Instagram using Playwright (account-based)"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.posts = []
        self.browser = None
        self.context = None
    
    async def login(self, page):
        """Login to Instagram"""
        logger.info(f"🔐 Logging in as {self.username}...")
        
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_timeout(2000)
        
        # Enter username
        await page.fill("input[name='username']", self.username)
        await page.wait_for_timeout(500)
        
        # Enter password
        await page.fill("input[name='password']", self.password)
        await page.wait_for_timeout(500)
        
        # Click login
        await page.click("button[type='button']:has-text('Log in')")
        
        try:
            # Wait for login to complete
            await page.wait_for_url("https://www.instagram.com/", timeout=10000)
            logger.info("✅ Logged in successfully!")
            return True
        except:
            logger.error("❌ Login failed. Check credentials.")
            return False
    
    async def scrape_hashtag(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """Scrape posts from hashtag"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                posts = []
                
                # Go to hashtag
                url = f"https://www.instagram.com/explore/tags/{hashtag}/"
                await page.goto(url)
                await page.wait_for_timeout(3000)
                
                logger.info(f"📸 Scraping #{hashtag}...")
                
                # Scroll and extract posts
                post_links = []
                for _ in range(3):  # Scroll 3 times
                    # Get all post links
                    links = await page.query_selector_all("a[href*='/p/']")
                    for link in links:
                        href = await link.get_attribute("href")
                        if href and href not in post_links:
                            post_links.append(href)
                    
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1000)
                
                logger.info(f"   Found {len(post_links)} posts")
                
                # Visit each post
                for idx, link in enumerate(post_links[:limit], 1):
                    try:
                        await page.goto(f"https://www.instagram.com{link}")
                        await page.wait_for_timeout(2000)
                        
                        # Extract post data
                        try:
                            caption = await page.text_content("span[data-aria-label='Expande']")
                        except:
                            caption = ""
                        
                        post = {
                            "id": f"ig_pw_{idx}",
                            "text": caption or "No caption",
                            "url": f"https://www.instagram.com{link}",
                            "timestamp": datetime.now().isoformat(),
                            "platform": "Instagram",
                            "source": "playwright_account"
                        }
                        posts.append(post)
                        logger.info(f"   ✓ Post {idx}/{limit}")
                        
                    except Exception as e:
                        logger.debug(f"   Error on post {idx}: {e}")
                        continue
                
                logger.info(f"✅ Scraped {len(posts)} posts from #{hashtag}")
                self.posts.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()
    
    async def scrape_user(self, username: str, limit: int = 10) -> List[Dict]:
        """Scrape posts from user"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                posts = []
                
                # Go to user profile
                url = f"https://www.instagram.com/{username}/"
                await page.goto(url)
                await page.wait_for_timeout(3000)
                
                logger.info(f"📸 Scraping @{username}...")
                
                # Get posts
                post_links = await page.query_selector_all("a[href*='/p/']")
                
                logger.info(f"   Found {len(post_links)} posts")
                
                for idx, link in enumerate(post_links[:limit], 1):
                    try:
                        href = await link.get_attribute("href")
                        if href:
                            posts.append({
                                "id": f"ig_pw_{idx}",
                                "author": username,
                                "url": f"https://www.instagram.com{href}",
                                "timestamp": datetime.now().isoformat(),
                                "platform": "Instagram",
                                "source": "playwright_account"
                            })
                    except:
                        continue
                
                logger.info(f"✅ Scraped {len(posts)} posts from @{username}")
                self.posts.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()
    
    def save_posts(self, filename: str = "data/instagram_playwright.json"):
        """Save posts"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.posts)} posts")


async def main():
    print("\n" + "📱 " * 10)
    print("  Instagram Scraper - Playwright (Account-Based)")
    print("📱 " * 10 + "\n")
    
    # Get credentials from environment
    username = os.getenv('IG_USERNAME')
    password = os.getenv('IG_PASSWORD')
    
    if not username or not password:
        print("❌ No Instagram credentials found!")
        print("\nSet environment variables:")
        print("   $env:IG_USERNAME='your_username'")
        print("   $env:IG_PASSWORD='your_password'")
        print("   python instagram_playwright_scraper.py")
        return
    
    try:
        scraper = InstagramPlaywrightScraper(username, password)
        
        # Scrape hashtags
        await scraper.scrape_hashtag("tunisia", limit=5)
        
        # Save
        scraper.save_posts()
        
        print(f"\n✅ Done! Collected {len(scraper.posts)} posts")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
