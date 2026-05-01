#!/usr/bin/env python3
"""
Playwright Spiders - Account-Based Social Media Scraping
Unified interface similar to Scrapy spiders
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict
import os
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("❌ Playwright not installed. Run: pip install playwright")
    exit(1)

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class PlaywrightSpider:
    """Base spider using Playwright"""
    
    name = "base_spider"
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.items = []
    
    async def login(self, page: Page) -> bool:
        """Override in subclass"""
        raise NotImplementedError
    
    async def scrape(self) -> List[Dict]:
        """Override in subclass"""
        raise NotImplementedError
    
    def save(self, filename: str = None):
        """Save items to JSON"""
        if not filename:
            filename = f"data/{self.name}.json"
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.items)} items to {filename}")


class InstagramSpider(PlaywrightSpider):
    """Instagram Scraper Spider"""
    
    name = "instagram"
    
    async def login(self, page: Page) -> bool:
        """Login to Instagram"""
        logger.info(f"🔐 Logging in as {self.username}...")
        
        await page.goto("https://www.instagram.com/accounts/login/")
        await page.wait_for_timeout(2000)
        
        # Enter credentials
        await page.fill("input[name='username']", self.username)
        await page.fill("input[name='password']", self.password)
        await page.click("button[type='button']:has-text('Log in')")
        
        try:
            await page.wait_for_url("https://www.instagram.com/", timeout=10000)
            logger.info("✅ Instagram logged in!")
            return True
        except:
            logger.error("❌ Instagram login failed")
            return False
    
    async def scrape_hashtag(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """Scrape Instagram hashtag"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                if not await self.login(page):
                    return []
                
                # Navigate to hashtag
                await page.goto(f"https://www.instagram.com/explore/tags/{hashtag}/")
                await page.wait_for_timeout(3000)
                
                logger.info(f"📸 Scraping #{hashtag}...")
                
                posts = []
                
                # Scroll and collect posts
                for scroll in range(3):
                    links = await page.query_selector_all("a[href*='/p/']")
                    logger.info(f"   Found {len(links)} posts (scroll {scroll+1})")
                    
                    for idx, link in enumerate(links[:limit], 1):
                        try:
                            href = await link.get_attribute("href")
                            if href:
                                posts.append({
                                    "id": f"ig_{idx}_{datetime.now().timestamp()}",
                                    "url": f"https://www.instagram.com{href}",
                                    "platform": "Instagram",
                                    "hashtag": hashtag,
                                    "timestamp": datetime.now().isoformat(),
                                    "source": "playwright"
                                })
                        except:
                            continue
                    
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1000)
                
                logger.info(f"✅ Got {len(posts)} posts")
                self.items.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()


class FacebookSpider(PlaywrightSpider):
    """Facebook Scraper Spider"""
    
    name = "facebook"
    
    async def login(self, page: Page) -> bool:
        """Login to Facebook"""
        logger.info(f"🔐 Logging in to Facebook...")
        
        await page.goto("https://www.facebook.com/login/")
        await page.wait_for_timeout(2000)
        
        # Enter credentials
        await page.fill("input[name='email']", self.username)
        await page.fill("input[name='pass']", self.password)
        await page.click("button[type='submit']")
        
        try:
            await page.wait_for_url("https://www.facebook.com/", timeout=10000)
            logger.info("✅ Facebook logged in!")
            return True
        except:
            logger.error("❌ Facebook login failed")
            return False
    
    async def scrape_page(self, page_url: str, limit: int = 10) -> List[Dict]:
        """Scrape Facebook page"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                if not await self.login(page):
                    return []
                
                logger.info(f"📰 Scraping Facebook page...")
                
                # Navigate to page
                await page.goto(page_url)
                await page.wait_for_timeout(3000)
                
                posts = []
                
                # Scroll and collect posts
                for _ in range(3):
                    post_divs = await page.query_selector_all("div[data-testid='post']")
                    
                    for idx, post in enumerate(post_divs[:limit], 1):
                        try:
                            posts.append({
                                "id": f"fb_{idx}_{datetime.now().timestamp()}",
                                "url": page_url,
                                "platform": "Facebook",
                                "timestamp": datetime.now().isoformat(),
                                "source": "playwright"
                            })
                        except:
                            continue
                    
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1000)
                
                logger.info(f"✅ Got {len(posts)} posts")
                self.items.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()


class TikTokSpider(PlaywrightSpider):
    """TikTok Scraper Spider"""
    
    name = "tiktok"
    
    async def login(self, page: Page) -> bool:
        """Login to TikTok"""
        logger.info(f"🔐 Logging in to TikTok...")
        
        await page.goto("https://www.tiktok.com/login")
        await page.wait_for_timeout(3000)
        
        try:
            await page.click("button:has-text('Use phone or email')")
            await page.wait_for_timeout(1000)
            
            await page.fill("input[type='text']", self.username)
            await page.fill("input[type='password']", self.password)
            await page.click("button:has-text('Log in')")
            
            await page.wait_for_url("https://www.tiktok.com/", timeout=15000)
            logger.info("✅ TikTok logged in!")
            return True
        except:
            logger.error("❌ TikTok login failed")
            return False
    
    async def scrape_hashtag(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """Scrape TikTok hashtag"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                # TikTok hashtags don't require login
                logger.info(f"🎵 Scraping #{hashtag} on TikTok...")
                
                await page.goto(f"https://www.tiktok.com/tag/{hashtag}")
                await page.wait_for_timeout(3000)
                
                videos = []
                
                for _ in range(3):
                    links = await page.query_selector_all("a[href*='/video/']")
                    
                    for idx, link in enumerate(links[:limit], 1):
                        try:
                            href = await link.get_attribute("href")
                            if href:
                                videos.append({
                                    "id": f"tiktok_{idx}_{datetime.now().timestamp()}",
                                    "url": f"https://www.tiktok.com{href}",
                                    "platform": "TikTok",
                                    "hashtag": hashtag,
                                    "timestamp": datetime.now().isoformat(),
                                    "source": "playwright"
                                })
                        except:
                            continue
                    
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1000)
                
                logger.info(f"✅ Got {len(videos)} videos")
                self.items.extend(videos)
                return videos
            
            finally:
                await context.close()
                await browser.close()


async def main():
    """Demo"""
    print("\n" + "🕷️  " * 10)
    print("  Playwright Spiders - Account-Based Scraping")
    print("🕷️  " * 10 + "\n")
    
    # Get credentials from environment
    ig_user = os.getenv('IG_USERNAME')
    ig_pass = os.getenv('IG_PASSWORD')
    fb_user = os.getenv('FB_EMAIL')
    fb_pass = os.getenv('FB_PASSWORD')
    tiktok_user = os.getenv('TIKTOK_USERNAME')
    tiktok_pass = os.getenv('TIKTOK_PASSWORD')
    
    print("=" * 70)
    print("📝 SETUP INSTRUCTIONS")
    print("=" * 70)
    
    print("\nSet environment variables (PowerShell):")
    print("\n   Instagram:")
    print("   $env:IG_USERNAME='your_ig_username'")
    print("   $env:IG_PASSWORD='your_ig_password'")
    
    print("\n   Facebook:")
    print("   $env:FB_EMAIL='your_facebook_email'")
    print("   $env:FB_PASSWORD='your_facebook_password'")
    
    print("\n   TikTok:")
    print("   $env:TIKTOK_USERNAME='your_tiktok_username'")
    print("   $env:TIKTOK_PASSWORD='your_tiktok_password'")
    
    print("\nThen run:")
    print("   python playwright_spiders.py")
    
    print("\n" + "=" * 70)
    print("🚀 EXAMPLE USAGE")
    print("=" * 70)
    
    if ig_user and ig_pass:
        print("\n✅ Instagram credentials found!")
        print("   Running: await instagram_spider.scrape_hashtag('tunisia', limit=5)")
        
        instagram_spider = InstagramSpider(ig_user, ig_pass)
        await instagram_spider.scrape_hashtag("tunisia", limit=5)
        instagram_spider.save()
    else:
        print("\n❌ Instagram credentials not found")
    
    if tiktok_user and tiktok_pass:
        print("\n✅ TikTok credentials found!")
        print("   Running: await tiktok_spider.scrape_hashtag('tunisia', limit=5)")
        
        tiktok_spider = TikTokSpider(tiktok_user, tiktok_pass)
        await tiktok_spider.scrape_hashtag("tunisia", limit=5)
        tiktok_spider.save()
    else:
        print("\n❌ TikTok credentials not found")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
