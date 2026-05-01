#!/usr/bin/env python3
"""
Scrapy + Playwright Facebook Scraper for Hackathon
Pre-scrapes Tunisian Facebook page comments for demo reliability
"""

import json
import time
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("❌ Playwright not installed")
    exit(1)


class FacebookPreScraper:
    """Pre-scrape Facebook comments for hackathon demo"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.comments = []
    
    def scrape_page(self, page_url: str, limit: int = 20):
        """Scrape comments from a Facebook page post"""
        
        print(f"🔍 Starting Facebook scraper on {page_url}...")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            try:
                print(f"📄 Loading {page_url}...")
                page.goto(page_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(3000)
                
                # Accept cookies if present
                try:
                    page.click("button:has-text('Accept')", timeout=2000)
                    page.wait_for_timeout(1000)
                except:
                    pass
                
                # Scroll to load comments
                print("📜 Scrolling to load comments...")
                for i in range(5):
                    page.evaluate("window.scrollBy(0, 2000)")
                    page.wait_for_timeout(1500)
                    print(f"   Scroll {i+1}/5...")
                
                # Try to find and click "Load more comments"
                try:
                    print("🔘 Clicking 'Load more' buttons...")
                    for _ in range(3):
                        load_buttons = page.query_selector_all(
                            "div[role='button'][aria-label*='comment'], button:has-text('Load')"
                        )
                        if load_buttons:
                            for btn in load_buttons[:2]:
                                try:
                                    btn.click(timeout=1000)
                                    page.wait_for_timeout(800)
                                except:
                                    pass
                        else:
                            break
                except:
                    pass
                
                # Extract comments
                print("📝 Extracting comments...")
                
                # Method 1: Direct comment text elements
                comment_elements = page.query_selector_all("div[dir='auto'] span:not([class])")
                
                extracted = set()  # Use set to avoid duplicates
                for elem in comment_elements:
                    try:
                        text = elem.inner_text().strip()
                        if len(text) > 10 and text not in extracted:
                            extracted.add(text)
                            self.comments.append({
                                "id": f"fb_{len(self.comments)}_{int(time.time())}",
                                "text": text,
                                "source": "facebook",
                                "url": page_url,
                                "timestamp": datetime.now().isoformat(),
                                "platform": "Facebook",
                                "language": "unknown"
                            })
                            if len(self.comments) >= limit:
                                break
                    except:
                        continue
                
                print(f"✅ Extracted {len(self.comments)} comments")
                
                # Take screenshot for verification
                page.screenshot(path="facebook_scrape_screenshot.png")
                print("📸 Screenshot saved: facebook_scrape_screenshot.png")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            finally:
                context.close()
                browser.close()
    
    def scrape_multiple_posts(self, page_urls: list, limit_per_page: int = 15):
        """Scrape comments from multiple Facebook pages"""
        
        for url in page_urls:
            print(f"\n{'='*70}")
            self.scrape_page(url, limit=limit_per_page)
            print(f"Total comments so far: {len(self.comments)}")
            time.sleep(3)  # Be polite, don't hammer Facebook
    
    def save_to_json(self, filename: str = "facebook_comments.json"):
        """Save scraped comments to JSON"""
        
        Path("data").mkdir(exist_ok=True)
        filepath = Path("data") / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.comments, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Saved {len(self.comments)} comments to {filepath}")
        return filepath


def main():
    """Main execution"""
    
    print("\n" + "🕷️  " * 15)
    print("  FACEBOOK PRE-SCRAPER FOR HACKATHON")
    print("🕷️  " * 15 + "\n")
    
    # Tunisian Facebook pages
    facebook_pages = [
        "https://www.facebook.com/MosaiqueFM",
        "https://www.facebook.com/nessma",
        "https://www.facebook.com/JawaharFM",
    ]
    
    # Initialize scraper
    # Set headless=False to see the browser during scraping (for debugging)
    scraper = FacebookPreScraper(headless=True)
    
    print("📋 TARGET PAGES:")
    for page in facebook_pages:
        print(f"   • {page}")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   • This is for PRE-DEMO data collection only")
    print("   • Run this BEFORE your hackathon demo (not live)")
    print("   • Facebook may block after 50-100 comments")
    print("   • If blocked, wait 1-2 hours and try again")
    print("   • Screenshot will show what was successfully scraped")
    
    # Scrape all pages
    try:
        scraper.scrape_multiple_posts(facebook_pages, limit_per_page=15)
    except KeyboardInterrupt:
        print("\n⏸️  Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
    
    # Save results
    if scraper.comments:
        filepath = scraper.save_to_json("facebook_comments.json")
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETE")
        print("="*70)
        print(f"\n📊 Statistics:")
        print(f"   • Total comments: {len(scraper.comments)}")
        print(f"   • Saved to: {filepath}")
        print(f"   • Ready to use in your pipeline!")
        
        # Show sample
        print(f"\n📝 SAMPLE COMMENTS (first 3):")
        for i, comment in enumerate(scraper.comments[:3], 1):
            print(f"\n   {i}. {comment['text'][:100]}...")
    
    else:
        print("\n❌ No comments were extracted. Facebook may have blocked access.")
        print("Try again later or use a different account.")


if __name__ == "__main__":
    main()
