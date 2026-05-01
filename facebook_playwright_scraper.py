#!/usr/bin/env python3
"""
Facebook Scraper with Playwright (Account-Based)
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


class FacebookPlaywrightScraper:
    """Scrape Facebook using Playwright (account-based)"""
    
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.posts = []
    
    async def login(self, page):
        """Login to Facebook"""
        logger.info(f"🔐 Logging in...")
        
        await page.goto("https://www.facebook.com/login/")
        await page.wait_for_timeout(2000)
        
        # Enter email
        await page.fill("input[name='email']", self.email)
        await page.wait_for_timeout(500)
        
        # Enter password
        await page.fill("input[name='pass']", self.password)
        await page.wait_for_timeout(500)
        
        # Click login
        await page.click("button[type='submit']")
        
        try:
            await page.wait_for_url("https://www.facebook.com/", timeout=10000)
            logger.info("✅ Logged in!")
            return True
        except:
            logger.error("❌ Login failed")
            return False
    
    async def scrape_page(self, page_url: str, limit: int = 10) -> List[Dict]:
        """Scrape posts from Facebook page"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                posts = []
                
                logger.info(f"📰 Scraping Facebook page...")
                
                # Navigate to page
                await page.goto(page_url)
                await page.wait_for_timeout(3000)
                
                # Scroll to load posts
                for _ in range(5):
                    await page.evaluate("window.scrollBy(0, window.innerHeight)")
                    await page.wait_for_timeout(1000)
                
                # Extract posts
                post_divs = await page.query_selector_all("div[data-testid='post']")
                
                logger.info(f"   Found {len(post_divs)} posts")
                
                for idx, post_div in enumerate(post_divs[:limit], 1):
                    try:
                        # Try to get post text
                        text_elem = await post_div.query_selector("span")
                        text = await text_elem.text_content() if text_elem else "No text"
                        
                        posts.append({
                            "id": f"fb_pw_{idx}",
                            "text": text[:500],  # Limit to 500 chars
                            "timestamp": datetime.now().isoformat(),
                            "platform": "Facebook",
                            "source": "playwright_account"
                        })
                        logger.info(f"   ✓ Post {idx}")
                        
                    except Exception as e:
                        logger.debug(f"   Error: {e}")
                        continue
                
                logger.info(f"✅ Scraped {len(posts)} posts")
                self.posts.extend(posts)
                return posts
            
            finally:
                await context.close()
                await browser.close()
    
    def save_posts(self, filename: str = "data/facebook_playwright.json"):
        """Save posts"""
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.posts)} posts")


async def main():
    print("\n" + "📱 " * 10)
    print("  Facebook Scraper - Playwright (Account-Based)")
    print("📱 " * 10 + "\n")
    
    email = os.getenv('FB_EMAIL')
    password = os.getenv('FB_PASSWORD')
    
    if not email or not password:
        print("❌ No Facebook credentials found!")
        print("\nSet environment variables:")
        print("   $env:FB_EMAIL='your_email@example.com'")
        print("   $env:FB_PASSWORD='your_password'")
        print("   python facebook_playwright_scraper.py")
        return
    
    try:
        scraper = FacebookPlaywrightScraper(email, password)
        
        # Example: Scrape Facebook page
        # await scraper.scrape_page("https://www.facebook.com/MosaiqueFM/", limit=5)
        
        logger.info("⚠️  Note: Facebook has strong anti-scraping measures")
        logger.info("   May require 2FA verification")
        logger.info("   Consider using official Graph API instead")
        
        print(f"\n✅ Collected {len(scraper.posts)} posts")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
