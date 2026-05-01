#!/usr/bin/env python3
"""
TikTok Scraper with Playwright (Account-Based)
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


class TikTokPlaywrightScraper:
    """Scrape TikTok using Playwright (account-based)"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.posts = []
    
    async def login(self, page):
        """Login to TikTok"""
        logger.info(f"🔐 Logging in to TikTok...")
        
        await page.goto("https://www.tiktok.com/login")
        await page.wait_for_timeout(3000)
        
        try:
            # Click phone/email login
            await page.click("button:has-text('Use phone or email')")
            await page.wait_for_timeout(1000)
            
            # Enter username
            await page.fill("input[type='text']", self.username)
            await page.wait_for_timeout(500)
            
            # Enter password
            await page.fill("input[type='password']", self.password)
            await page.wait_for_timeout(500)
            
            # Click login
            await page.click("button:has-text('Log in')")
            
            # Wait for redirect
            await page.wait_for_url("https://www.tiktok.com/", timeout=15000)
            logger.info("✅ Logged in!")
            return True
        except:
            logger.error("❌ Login failed")
            return False
    
    async def scrape_hashtag(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """Scrape videos from hashtag"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                posts = []
                
                # Go to hashtag
                url = f"https://www.tiktok.com/tag/{hashtag}"
                await page.goto(url)
                await page.wait_for_timeout(3000)
                
                logger.info(f"🎵 Scraping #{hashtag} on TikTok...")
                
                # Scroll and collect videos
                video_links = []
                for _ in range(3):
                    # Get all video links
                    links = await page.query_selector_all("a[href*='/video/']")
                    for link in links:
                        href = await link.get_attribute("href")
                        if href and href not in video_links:
                            video_links.append(href)
                    
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1000)
                
                logger.info(f"   Found {len(video_links)} videos")
                
                # Visit each video
                for idx, link in enumerate(video_links[:limit], 1):
                    try:
                        await page.goto(f"https://www.tiktok.com{link}")
                        await page.wait_for_timeout(2000)
                        
                        # Try to get caption
                        try:
                            caption = await page.text_content("span[data-testid='VideoCaption']")
                        except:
                            caption = ""
                        
                        posts.append({
                            "id": f"tiktok_pw_{idx}",
                            "text": caption or "No caption",
                            "url": f"https://www.tiktok.com{link}",
                            "timestamp": datetime.now().isoformat(),
                            "platform": "TikTok",
                            "source": "playwright_account"
                        })
                        logger.info(f"   ✓ Video {idx}/{limit}")
                        
                    except Exception as e:
                        logger.debug(f"   Error: {e}")
                        continue
                
                logger.info(f"✅ Scraped {len(posts)} videos from #{hashtag}")
                self.posts.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()
    
    async def scrape_user(self, username: str, limit: int = 10) -> List[Dict]:
        """Scrape videos from user"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                posts = []
                
                # Go to user profile
                url = f"https://www.tiktok.com/@{username}"
                await page.goto(url)
                await page.wait_for_timeout(3000)
                
                logger.info(f"🎵 Scraping @{username}...")
                
                # Get videos
                video_links = []
                for _ in range(2):
                    links = await page.query_selector_all("a[href*='/video/']")
                    for link in links:
                        href = await link.get_attribute("href")
                        if href and href not in video_links:
                            video_links.append(href)
                    
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(800)
                
                logger.info(f"   Found {len(video_links)} videos")
                
                for idx, link in enumerate(video_links[:limit], 1):
                    try:
                        posts.append({
                            "id": f"tiktok_pw_{idx}",
                            "author": username,
                            "url": f"https://www.tiktok.com{link}",
                            "timestamp": datetime.now().isoformat(),
                            "platform": "TikTok",
                            "source": "playwright_account"
                        })
                    except:
                        continue
                
                logger.info(f"✅ Scraped {len(posts)} videos from @{username}")
                self.posts.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()
    
    def save_posts(self, filename: str = "data/tiktok_playwright.json"):
        """Save posts"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.posts)} videos")


async def main():
    print("\n" + "🎵 " * 10)
    print("  TikTok Scraper - Playwright (Account-Based)")
    print("🎵 " * 10 + "\n")
    
    username = os.getenv('TIKTOK_USERNAME')
    password = os.getenv('TIKTOK_PASSWORD')
    
    if not username or not password:
        print("❌ No TikTok credentials found!")
        print("\nSet environment variables:")
        print("   $env:TIKTOK_USERNAME='your_username'")
        print("   $env:TIKTOK_PASSWORD='your_password'")
        print("   python tiktok_playwright_scraper.py")
        return
    
    try:
        scraper = TikTokPlaywrightScraper(username, password)
        
        # Example: Scrape hashtag
        # await scraper.scrape_hashtag("tunisia", limit=5)
        
        logger.info("⚠️  Note: TikTok has anti-scraping measures")
        logger.info("   May require phone verification")
        logger.info("   Use with caution - may violate ToS")
        
        print(f"\n✅ Collected {len(scraper.posts)} videos")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
