#!/usr/bin/env python3
"""
Simple Web Scraper for Tunisian Social Media Content
Uses requests + BeautifulSoup (no Scrapy needed)
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleWebScraper:
    """Lightweight web scraper for social media content"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.posts = []
    
    def scrape_news_site(self, url: str, site_name: str) -> List[Dict]:
        """
        Scrape news from a website
        
        Args:
            url: Website URL
            site_name: Name of the site
        
        Returns:
            List of posts
        """
        try:
            logger.info(f"🔍 Scraping {site_name} from {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = []
            
            # Generic news article selector (works on most news sites)
            articles = soup.find_all(['article', 'div'], class_=lambda x: x and ('post' in x.lower() or 'article' in x.lower() or 'item' in x.lower()))
            
            if not articles:
                # Fallback: look for headings
                articles = soup.find_all(['h2', 'h3'])
            
            logger.info(f"   Found {len(articles)} articles")
            
            for idx, article in enumerate(articles[:20], 1):  # Limit to 20 posts
                try:
                    # Extract text
                    title = article.get_text(strip=True)[:200]
                    
                    if len(title) < 10:
                        continue
                    
                    # Try to find a link
                    link = article.find('a')
                    url_post = link['href'] if link else None
                    
                    # Make absolute URL
                    if url_post and not url_post.startswith('http'):
                        url_post = url.split('/')[0] + '//' + url.split('/')[2] + url_post
                    
                    post = {
                        "id": f"scrape_{site_name}_{idx}",
                        "text": title,
                        "author": site_name,
                        "platform": site_name,
                        "source": "web_scraper",
                        "url": url_post,
                        "timestamp": datetime.now().isoformat(),
                        "sentiment": self._simple_sentiment(title),
                        "language": self._detect_language(title),
                        "post_type": "news"
                    }
                    posts.append(post)
                    
                except Exception as e:
                    logger.debug(f"   Error parsing article {idx}: {e}")
                    continue
            
            logger.info(f"   ✅ Extracted {len(posts)} posts from {site_name}")
            self.posts.extend(posts)
            return posts
        
        except Exception as e:
            logger.error(f"❌ Error scraping {site_name}: {e}")
            return []
    
    def _simple_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on keywords"""
        text_lower = text.lower()
        
        negative_words = ['crisis', 'problem', 'death', 'crisis', 'failed', 'failed', 'bad', 'worst', 
                         'unemployment', 'inflation', 'scandal', 'accident', 'danger', 'risk']
        positive_words = ['success', 'win', 'achievement', 'growth', 'improvement', 'good', 'best',
                         'approved', 'launched', 'celebrate', 'record']
        
        neg_count = sum(1 for word in negative_words if word in text_lower)
        pos_count = sum(1 for word in positive_words if word in text_lower)
        
        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"
    
    def _detect_language(self, text: str) -> str:
        """Detect language in text"""
        # Simple check for Arabic script
        if any('\u0600' <= char <= '\u06FF' for char in text):
            return "Arabic"
        elif any('ç' in text.lower() or 'é' in text.lower() for text in [text]):
            return "French"
        else:
            return "English"
    
    def save_to_file(self, filename: str = "data/scraped_posts.json") -> None:
        """Save collected posts to JSON file"""
        import os
        os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Saved {len(self.posts)} posts to {filename}")
    
    def get_posts(self) -> List[Dict]:
        """Get all collected posts"""
        return self.posts


def main():
    """Main scraping function"""
    print("\n" + "🔍 " * 10)
    print("  Simple Web Scraper - Tunisian Social Media")
    print("🔍 " * 10 + "\n")
    
    scraper = SimpleWebScraper()
    
    # List of Tunisian news sites to scrape
    sites = [
        ("https://www.tunisienumerique.com", "Tunisie Numérique"),
        ("https://www.businessnews.com.tn", "Business News"),
        ("https://www.kapitalis.com", "Kapitalis"),
    ]
    
    print("📰 COLLECTING FROM TUNISIAN NEWS SITES")
    print("=" * 60)
    
    for url, name in sites:
        print(f"\n🔍 Scraping: {name}")
        print(f"   URL: {url}")
        
        try:
            posts = scraper.scrape_news_site(url, name)
            print(f"   ✅ Got {len(posts)} posts")
        except Exception as e:
            print(f"   ⚠️  Could not scrape (site may be blocked or down): {e}")
        
        # Be respectful: delay between requests
        time.sleep(2)
    
    # Display collected posts
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: Collected {len(scraper.posts)} posts total")
    print("=" * 60)
    
    if scraper.posts:
        print("\n📝 Sample Posts:")
        for post in scraper.posts[:3]:
            print(f"\n  📌 {post['author']}")
            print(f"     {post['text'][:100]}...")
            print(f"     Sentiment: {post['sentiment']} | Language: {post['language']}")
    
    # Save to file
    scraper.save_to_file()
    
    print("\n" + "🎉 " * 10)
    print("  Scraping Complete!")
    print("🎉 " * 10 + "\n")


if __name__ == "__main__":
    main()
