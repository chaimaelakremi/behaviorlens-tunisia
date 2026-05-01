#!/usr/bin/env python3
"""
BehaviorLens Social Media Intelligence Pipeline
Tunisian social media data collection and analysis for hackathon

Install:
    pip install scrapy scrapy-playwright playwright fastapi uvicorn aiofiles
    playwright install chromium
    mkdir sessions (if not exists)

Usage:
    python behaviorlens_social.py                    # Run all spiders
    python behaviorlens_social.py --save-session facebook
    python behaviorlens_social.py --save-session tiktok
    python behaviorlens_social.py --save-session instagram
    python behaviorlens_social.py --api              # Start FastAPI server
    python behaviorlens_social.py --spider facebook_tn
"""

import sys
import os
import json
import sqlite3
import asyncio
import logging
import argparse
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

# Scrapy & Playwright
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from scrapy_playwright.page import PageMethod

# Playwright for session management
from playwright.sync_api import sync_playwright

# FastAPI
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION & CONSTANTS
# ════════════════════════════════════════════════════════════════════════════════

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DB_NAME = "behaviorlens.db"
SESSIONS_DIR = "sessions"
OUTPUT_FILE = "behaviorlens_output.jsonl"

# Ensure directories exist
Path(SESSIONS_DIR).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION KEYWORDS
# ════════════════════════════════════════════════════════════════════════════════

KEYWORDS = {
    "complaint": [
        "مشكل", "مشاكل", "problème", "problèmes", "catastrophe", "غالي", "cher",
        "kharba", "خربة", "hchouma", "تعب", "تعبان", "déçu", "honte", "مخزي",
        "كارثة", "ظلم", "غالي جدا", "سيء", "تاع", "وجع", "ألم"
    ],
    "opinion": [
        "اعتقد", "أعتقد", "برأيي", "برأي", "je pense", "selon moi", "mon avis",
        "رأيي", "personnellement", "في رأيي", "نحسبو", "يقولو", "قالوا", "نقول"
    ],
    "news": [
        "عاجل", "breaking", "urgent", "خبر", "أخبار", "officiel", "annonce",
        "communiqué", "déclaration", "جديد", "أخير", "إعلان", "تصريح", "نبأ",
        "وزير", "رئيس", "حكومة"
    ],
    "humor": [
        "😂", "🤣", "hhhh", "هههه", "loool", "lol", "مضحك", "طريف", "تاوا",
        "باهي يعيش", "واش", "نكتة", "فكاهة", "ههههه", "😁", "😆"
    ],
    "promotion": [
        "solde", "promo", "تخفيض", "discount", "offre", "عرض", "livraison",
        "gratuit", "مجاني", "commander", "اشتري", "شراء", "بيع", "توصيل",
        "في السوق", "معاش", "نقص من السعر"
    ],
    "question": [
        "?", "؟", "كيف", "comment faire", "how", "pourquoi", "why", "متى",
        "quand", "شكون", "من", "وين", "أين", "شنوة", "إش", "ولاه", "إلا"
    ],
    "event": [
        "حفل", "concert", "festival", "soirée", "invitation", "موعد", "inscription",
        "حفلة", "تجمع", "ملتقى", "اجتماع", "دعوة", "الجمعة", "الأحد", "السبت"
    ]
}

POSITIVE_KEYWORDS = [
    "برشا مليح", "بارك", "تمام", "super", "excellent", "bravo", "شكرا",
    "شكراً", "مرحبا", "نجاح", "فرحة", "فرحان", "😍", "❤️", "👍", "🎉",
    "mabrouk", "مبروك", "ألف مبروك", "yesss", "yeah", "والله يفرجها",
    "بالتوفيق", "حظ موفق", "شنيع", "جميل", "راهو حسن"
]

NEGATIVE_KEYWORDS = [
    "مشكل", "كارثة", "hchouma", "مخزي", "غالي", "barrani", "ظلم", "corruption",
    "فساد", "😡", "😢", "💔", "non", "لا", "ما تمام", "سيء", "تاع",
    "خطير", "وجع", "ألم", "مقرف", "فاشل", "ما بهيش", "كيف هكا", "شنوة هذا"
]

TUNISIAN_GEOGRAPHIC = [
    "tunisie", "tunis", "sfax", "sousse", "monastir", "gabes", "bizerte",
    "kairouan", "gafsa", "jendouba", "kef", "kasserine", "sidi bouzid",
    "تونس", "صفاقس", "سوسة", "منستير", "قابس", "بنزرت", "القيروان",
    "قفصة", "جندوبة", "الكاف", "القصرين", "سيدي بوزيد"
]

TUNISIAN_DIALECT = [
    "barcha", "برشا", "mta3", "متاع", "bch", "يزي", "yezzi", "fisa3",
    "manich", "مانيش", "behi", "بهي", "3ayech", "عايش", "chwiya", "شوية",
    "taw", "تو", "maak", "نحي", "ya3tik", "نعم يسر", "ahna", "و الله",
    "wAllah", "weld", "bneta", "بنت", "الراجل", "الولد", "نهايتو", "تمام"
]

TUNISIAN_INSTITUTIONS = [
    "mosaique", "shems", "jawhara", "attessia", "watania", "express.fm",
    "tap", "tap tna", "مساح", "شمس", "جوهرة", "تاص", "الوطنية", "إكسبريس"
]

TUNISIAN_HASHTAGS = [
    "#tunisie", "#tunis", "#تونس", "#تونسي", "#تونسية", "#sfax", "#sousse",
    "#tunisian", "#تونسيين", "#تونسيات", "#الجنة", "#صفاقس", "#سوسة"
]

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE SETUP
# ════════════════════════════════════════════════════════════════════════════════

def init_database():
    """Initialize SQLite database with schema"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            url TEXT UNIQUE,
            post_id TEXT UNIQUE,
            author TEXT,
            text TEXT,
            media_type TEXT,
            hashtags_json TEXT,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            post_type TEXT,
            sentiment TEXT,
            is_tunisian BOOLEAN,
            language TEXT,
            scraped_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Comments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            text TEXT,
            likes INTEGER DEFAULT 0,
            sentiment TEXT,
            is_tunisian BOOLEAN,
            hashtags_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Database initialized: {DB_NAME}")

def insert_post(post: Dict) -> bool:
    """Insert post into database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO posts 
            (source, url, post_id, author, text, media_type, hashtags_json,
             likes, shares, comments_count, post_type, sentiment, is_tunisian, language, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post.get("source"),
            post.get("url"),
            post.get("post_id"),
            post.get("author"),
            post.get("text"),
            post.get("media_type"),
            json.dumps(post.get("hashtags", [])),
            post.get("likes", 0),
            post.get("shares", 0),
            post.get("comments_count", 0),
            post.get("post_type"),
            post.get("sentiment"),
            post.get("is_tunisian"),
            post.get("language"),
            post.get("scraped_at")
        ))
        
        post_db_id = cursor.lastrowid
        
        # Insert comments
        for comment in post.get("comments", []):
            cursor.execute("""
                INSERT INTO comments
                (post_id, text, likes, sentiment, is_tunisian, hashtags_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                post.get("post_id"),
                comment.get("text"),
                comment.get("likes", 0),
                comment.get("sentiment"),
                comment.get("is_tunisian"),
                json.dumps(comment.get("hashtags", []))
            ))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate
    except Exception as e:
        logger.error(f"❌ Database insert error: {e}")
        return False

def post_exists(post_id: str) -> bool:
    """Check if post already exists in database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM posts WHERE post_id = ?", (post_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except:
        return False

# ════════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION & DETECTION HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def make_post_id(source: str, url: str, index: str) -> str:
    """Generate unique post ID using MD5 hash"""
    content = f"{source}_{url}_{index}"
    return hashlib.md5(content.encode()).hexdigest()[:16]

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text using regex"""
    if not text:
        return []
    hashtags = re.findall(r'#\S+', text)
    return list(set(hashtags))

def detect_language(text: str) -> str:
    """Detect language: arabic, french, tunisian_dialect, mixed"""
    if not text:
        return "unknown"
    
    text_lower = text.lower()
    
    # Count Arabic characters
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    french_chars = len(re.findall(r'[a-zA-Z]', text))
    total_chars = len(text)
    
    arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0
    french_ratio = french_chars / total_chars if total_chars > 0 else 0
    
    # Check for Tunisian dialect markers
    has_dialect = any(marker in text_lower for marker in TUNISIAN_DIALECT)
    
    if has_dialect:
        return "tunisian_dialect"
    elif arabic_ratio > 0.4:
        return "arabic"
    elif french_ratio > 0.4:
        return "french"
    else:
        return "mixed"

def detect_tunisian(text: str) -> bool:
    """Detect if text is Tunisian: geography, dialect, institutions, hashtags"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Check geographic markers
    for geo in TUNISIAN_GEOGRAPHIC:
        if geo in text_lower:
            return True
    
    # Check dialect markers
    for dialect in TUNISIAN_DIALECT:
        if dialect in text_lower:
            return True
    
    # Check institutions
    for inst in TUNISIAN_INSTITUTIONS:
        if inst in text_lower:
            return True
    
    # Check hashtags
    hashtags = extract_hashtags(text)
    for tag in hashtags:
        if any(tn_tag in tag.lower() for tn_tag in TUNISIAN_HASHTAGS):
            return True
    
    return False

def classify_post_type(text: str) -> str:
    """Classify post type based on keywords"""
    if not text:
        return "general"
    
    text_lower = text.lower()
    
    # Check in priority order
    for post_type, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return post_type
    
    return "general"

def classify_sentiment(text: str) -> str:
    """Classify sentiment: positive, negative, neutral"""
    if not text:
        return "neutral"
    
    text_lower = text.lower()
    
    positive_count = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    negative_count = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    
    if positive_count > negative_count and positive_count > 0:
        return "positive"
    elif negative_count > positive_count and negative_count > 0:
        return "negative"
    else:
        return "neutral"

def extract_numbers(text: str) -> int:
    """Extract first number from text"""
    if not text:
        return 0
    match = re.search(r'\d+', text.replace("K", "000").replace("M", "000000"))
    return int(match.group()) if match else 0

def build_post_item(
    source: str,
    url: str,
    post_id: str,
    author: str,
    text: str,
    comments: List[Dict],
    media_type: str = "text",
    likes: int = 0,
    shares: int = 0
) -> Dict:
    """Build complete post item with all metadata"""
    
    # Combine text with comments for enrichment
    combined_text = text + " " + " ".join(c.get("text", "") for c in comments)
    
    hashtags = extract_hashtags(text)
    
    return {
        "source": source,
        "url": url,
        "post_id": post_id,
        "author": author,
        "text": text,
        "media_type": media_type,
        "hashtags": hashtags,
        "likes": likes,
        "shares": shares,
        "comments_count": len(comments),
        "post_type": classify_post_type(combined_text),
        "sentiment": classify_sentiment(combined_text),
        "is_tunisian": detect_tunisian(combined_text),
        "language": detect_language(combined_text),
        "scraped_at": datetime.now().isoformat(),
        "comments": [
            {
                "text": c.get("text"),
                "likes": c.get("likes", 0),
                "sentiment": classify_sentiment(c.get("text", "")),
                "is_tunisian": detect_tunisian(c.get("text", "")),
                "hashtags": extract_hashtags(c.get("text", ""))
            }
            for c in comments
        ]
    }

# ════════════════════════════════════════════════════════════════════════════════
# SCRAPY PIPELINES
# ════════════════════════════════════════════════════════════════════════════════

class TunisianFilterPipeline:
    """Filter out non-Tunisian content"""
    
    def process_item(self, item, spider):
        if item.get("is_tunisian"):
            return item
        
        # Check if any comment is Tunisian
        for comment in item.get("comments", []):
            if comment.get("is_tunisian"):
                return item
        
        # Check if hashtags contain Tunisian hashtags
        hashtags = item.get("hashtags", [])
        hashtags_str = " ".join(hashtags).lower()
        if any(tn_tag.lower() in hashtags_str for tn_tag in TUNISIAN_HASHTAGS):
            return item
        
        raise scrapy.DropItem(f"Non-Tunisian post: {item.get('post_id')}")

class DeduplicationPipeline:
    """Skip duplicate posts"""
    
    def process_item(self, item, spider):
        if post_exists(item.get("post_id")):
            raise scrapy.DropItem(f"Duplicate post: {item.get('post_id')}")
        return item

class SQLitePipeline:
    """Store items in SQLite database"""
    
    def process_item(self, item, spider):
        if insert_post(item):
            logger.info(f"✅ Stored: {item.get('post_id')} from {item.get('source')}")
        return item

# ════════════════════════════════════════════════════════════════════════════════
# SCRAPY SPIDERS
# ════════════════════════════════════════════════════════════════════════════════

def _build_contexts():
    """Build PLAYWRIGHT_CONTEXTS with existing sessions"""
    contexts = {}
    for platform in ['facebook', 'tiktok', 'instagram']:
        session_file = f'{SESSIONS_DIR}/{platform}_session.json'
        if Path(session_file).exists():
            contexts[platform] = {'storage_state': session_file}
        else:
            contexts[platform] = {}
    return contexts

class FacebookTNSpider(scrapy.Spider):
    name = "facebook_tn"
    
    custom_settings = {
        'PLAYWRIGHT_CONTEXTS': _build_contexts(),
    }
    
    start_urls = [
        "https://www.facebook.com/Mosaique.fm",
        "https://www.facebook.com/shemsfm.tunisie",
        "https://www.facebook.com/JarraTv",
        "https://www.facebook.com/attessia.tv",
        "https://www.facebook.com/tap.tna",
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": "facebook",
                    "playwright_page_methods": [
                        PageMethod("wait_for_timeout", 5000),
                        PageMethod("evaluate", "window.scrollBy(0, 2500)"),
                        PageMethod("wait_for_timeout", 1500),
                        PageMethod("evaluate", "window.scrollBy(0, 2500)"),
                        PageMethod("wait_for_timeout", 1500),
                    ],
                },
                errback=self.errback_close_spider,
            )
    
    async def parse(self, response):
        page = response.meta.get("playwright_page")
        logger.info(f"🔍 Parsing Facebook: {response.url}")
        
        try:
            # Better scrolling with Playwright
            await page.evaluate("""async () => {
                for (let i = 0; i < 5; i++) {
                    window.scrollBy(0, 1800);
                    await new Promise(r => setTimeout(r, 1200));
                }
            }""")
            
            # Extract posts using JS evaluation as primary method, CSS as fallback
            posts = await page.evaluate("""
                () => {
                    const posts = [];
                    document.querySelectorAll('article, div[role="article"]').forEach((el, i) => {
                        const text = el.innerText ? el.innerText.trim().substring(0, 800) : '';
                        if (text.length > 30) {
                            posts.push({text: text, index: i});
                        }
                    });
                    return posts.slice(0, 8);
                }
            """)
            
            for post in posts:
                post_id = make_post_id("facebook", response.url, str(post['index']))
                
                # Extract comments via Playwright JS
                comments = []
                try:
                    comments = await page.evaluate("""
                        () => Array.from(document.querySelectorAll('ul li span'))
                            .map(el => ({text: el.innerText.trim()}))
                            .filter(c => c.text.length > 5)
                            .slice(0, 12)
                    """)
                except:
                    pass
                
                item = build_post_item(
                    source="facebook",
                    url=response.url,
                    post_id=post_id,
                    author=response.url.split('/')[-1],
                    text=post['text'],
                    comments=comments,
                    media_type="mixed"
                )
                
                yield item
        
        except Exception as e:
            logger.error(f"❌ Facebook parse error: {e}")
        finally:
            if page:
                await page.close()
    
    def errback_close_spider(self, failure):
        logger.error(f"❌ Facebook spider error: {failure.getErrorMessage()}")

class TikTokTNSpider(scrapy.Spider):
    name = "tiktok_tn"
    
    custom_settings = {
        'PLAYWRIGHT_CONTEXTS': _build_contexts(),
    }
    
    start_urls = [
        "https://www.tiktok.com/tag/tunisie",
        "https://www.tiktok.com/tag/tunis",
        "https://www.tiktok.com/tag/تونس",
        "https://www.tiktok.com/tag/تونسي",
        "https://www.tiktok.com/tag/sfax",
        "https://www.tiktok.com/tag/sousse",
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": "tiktok",
                    "playwright_page_methods": [
                        PageMethod("wait_for_timeout", 6000),
                        PageMethod("evaluate", "window.scrollBy(0, 3000)"),
                        PageMethod("wait_for_timeout", 2500),
                        PageMethod("evaluate", "window.scrollBy(0, 3000)"),
                        PageMethod("wait_for_timeout", 2500),
                    ],
                },
                errback=self.errback_close_spider,
            )
    
    async def parse(self, response):
        page = response.meta.get("playwright_page")
        logger.info(f"🎵 Parsing TikTok: {response.url}")
        
        try:
            # Enhanced scrolling for TikTok feed
            await page.evaluate("""async () => {
                for (let i = 0; i < 7; i++) {
                    window.scrollBy(0, 2500);
                    await new Promise(r => setTimeout(r, 1800));
                }
            }""")
            
            # Extract videos using JS evaluation with fallback
            videos = await page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll('a[href*="/video/"]').forEach((el, idx) => {
                        const href = el.href;
                        const captionEl = el.querySelector('[data-e2e="video-desc"], .video-meta-caption, div[class*="DivDescription"]');
                        const text = captionEl ? captionEl.innerText.trim() : `#${href.split('/tag/').pop() || 'tunisie'}`;
                        if (text.length > 5) {
                            results.push({url: href, text: text.substring(0, 600), index: idx});
                        }
                    });
                    return results.slice(0, 10);
                }
            """)
            
            for video in videos:
                video_id = video['url'].split('/video/')[-1].split('?')[0] if '/video/' in video['url'] else f"tiktok_{video['index']}"
                post_id = make_post_id("tiktok", video['url'], str(video['index']))
                
                item = build_post_item(
                    source="tiktok",
                    url=video['url'],
                    post_id=post_id,
                    author="tiktok_creator",
                    text=video['text'],
                    comments=[],
                    media_type="video"
                )
                
                yield item
        
        except Exception as e:
            logger.error(f"❌ TikTok parse error on {response.url}: {e}")
        finally:
            if page:
                await page.close()
    
    def errback_close_spider(self, failure):
        logger.error(f"❌ TikTok request failed: {failure.getErrorMessage()}")

class InstagramTNSpider(scrapy.Spider):
    name = "instagram_tn"
    
    custom_settings = {
        'PLAYWRIGHT_CONTEXTS': _build_contexts(),
    }
    
    start_urls = [
        "https://www.instagram.com/mosaiquefm/",
        "https://www.instagram.com/shemsfm/",
        "https://www.instagram.com/tunisienumerique/",
        "https://www.instagram.com/tap.tna/",
    ]
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_context": "instagram",
                    "playwright_page_methods": [
                        PageMethod("wait_for_timeout", 5000),
                        PageMethod("evaluate", "window.scrollBy(0, 2500)"),
                        PageMethod("wait_for_timeout", 2000),
                        PageMethod("evaluate", "window.scrollBy(0, 2500)"),
                    ],
                },
                errback=self.errback_close_spider,
            )
    
    async def parse(self, response):
        page = response.meta.get("playwright_page")
        logger.info(f"📷 Parsing Instagram: {response.url}")
        
        try:
            await page.evaluate("""async () => {
                for (let i = 0; i < 5; i++) {
                    window.scrollBy(0, 2200);
                    await new Promise(r => setTimeout(r, 1600));
                }
            }""")
            
            # Extract posts using JS evaluation
            posts = await page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll('a[href*="/p/"], article a').forEach((el, idx) => {
                        const href = el.href || '';
                        if (href.includes('/p/')) {
                            const captionEl = el.querySelector('span, div[role="button"]') || el;
                            const text = captionEl.innerText ? captionEl.innerText.trim() : 'Instagram post';
                            results.push({url: href, text: text.substring(0, 500), index: idx});
                        }
                    });
                    return results.slice(0, 8);
                }
            """)
            
            author = response.url.rstrip('/').split('/')[-1]
            
            for post in posts:
                post_id = make_post_id("instagram", post['url'], str(post['index']))
                
                # Extract comments via Playwright JS
                comments = []
                try:
                    comments = await page.evaluate("""
                        () => Array.from(document.querySelectorAll('ul li span'))
                            .map(el => ({text: el.innerText.trim()}))
                            .filter(c => c.text.length > 5)
                            .slice(0, 10)
                    """)
                except:
                    pass
                
                item = build_post_item(
                    source="instagram",
                    url=post['url'],
                    post_id=post_id,
                    author=author,
                    text=post['text'],
                    comments=comments,
                    media_type="image"
                )
                
                yield item
        
        except Exception as e:
            logger.error(f"❌ Instagram parse error on {response.url}: {e}")
        finally:
            if page:
                await page.close()
    
    def errback_close_spider(self, failure):
        logger.error(f"❌ Instagram request failed: {failure.getErrorMessage()}")

# ════════════════════════════════════════════════════════════════════════════════
# SCRAPY SETTINGS
# ════════════════════════════════════════════════════════════════════════════════

SCRAPY_SETTINGS = {
    'BOT_NAME': 'behaviorlens',
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    
    'DOWNLOAD_HANDLERS': {
        'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
    },
    
    'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
    
    'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
    'PLAYWRIGHT_LAUNCH_OPTIONS': {
        'headless': True,
        'args': ['--disable-blink-features=AutomationControlled', '--no-sandbox'],
    },
    
    # Build contexts dynamically at spider runtime
    # 'PLAYWRIGHT_CONTEXTS' is now built in _build_contexts()
    
    'DOWNLOAD_DELAY': 3,
    'AUTOTHROTTLE_ENABLED': True,
    'CONCURRENT_REQUESTS': 1,
    'ROBOTSTXT_OBEY': False,
    
    'ITEM_PIPELINES': {
        '__main__.TunisianFilterPipeline': 200,
        '__main__.DeduplicationPipeline': 300,
        '__main__.SQLitePipeline': 400,
    },
    
    'FEEDS': {
        OUTPUT_FILE: {'format': 'jsonl'},
    },
    
    'LOG_LEVEL': 'INFO',
}

# ════════════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════════

def save_session(platform: str):
    """Save browser session for authenticated scraping"""
    
    platform_config = {
        "facebook": {
            "url": "https://www.facebook.com/login",
            "file": f"{SESSIONS_DIR}/facebook_session.json"
        },
        "tiktok": {
            "url": "https://www.tiktok.com/login",
            "file": f"{SESSIONS_DIR}/tiktok_session.json"
        },
        "instagram": {
            "url": "https://www.instagram.com/accounts/login",
            "file": f"{SESSIONS_DIR}/instagram_session.json"
        }
    }
    
    if platform not in platform_config:
        logger.error(f"❌ Unknown platform: {platform}")
        return
    
    config = platform_config[platform]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        logger.info(f"🔐 Opening {platform.upper()} login...")
        page.goto(config["url"])
        
        input("\n✋ Log in manually in the browser window, then press Enter here...")
        
        # Save session
        context.storage_state(path=config["file"])
        logger.info(f"✅ Session saved: {config['file']}")
        
        browser.close()

# ════════════════════════════════════════════════════════════════════════════════
# FASTAPI SERVER
# ════════════════════════════════════════════════════════════════════════════════

app = FastAPI(title="BehaviorLens Social Intelligence API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """Get database connection"""
    return sqlite3.connect(DB_NAME)

@app.get("/api/posts")
async def get_posts(
    source: Optional[str] = Query(None),
    post_type: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    is_tunisian: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    """Get filtered posts"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM posts WHERE 1=1"
    params = []
    
    if source:
        query += " AND source = ?"
        params.append(source)
    
    if post_type:
        query += " AND post_type = ?"
        params.append(post_type)
    
    if sentiment:
        query += " AND sentiment = ?"
        params.append(sentiment)
    
    if is_tunisian is not None:
        query += " AND is_tunisian = ?"
        params.append(1 if is_tunisian else 0)
    
    query += " ORDER BY scraped_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    posts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {"total": len(posts), "posts": posts}

@app.get("/api/posts/recent")
async def get_recent_posts(limit: int = Query(20, ge=1, le=100)):
    """Get most recent posts"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM posts ORDER BY scraped_at DESC LIMIT ?",
        (limit,)
    )
    posts = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {"total": len(posts), "posts": posts}

@app.get("/api/comments")
async def get_comments(
    post_id: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500)
):
    """Get filtered comments"""
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM comments WHERE 1=1"
    params = []
    
    if post_id:
        query += " AND post_id = ?"
        params.append(post_id)
    
    if sentiment:
        query += " AND sentiment = ?"
        params.append(sentiment)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cursor.execute(query, params)
    comments = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return {"total": len(comments), "comments": comments}

@app.get("/api/stats")
async def get_stats():
    """Get statistics about scraped data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total posts
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_posts = cursor.fetchone()[0]
    
    # Posts by source
    cursor.execute("SELECT source, COUNT(*) FROM posts GROUP BY source")
    posts_by_source = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Posts by type
    cursor.execute("SELECT post_type, COUNT(*) FROM posts GROUP BY post_type")
    posts_by_type = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Posts by sentiment
    cursor.execute("SELECT sentiment, COUNT(*) FROM posts GROUP BY sentiment")
    posts_by_sentiment = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Tunisian posts count
    cursor.execute("SELECT COUNT(*) FROM posts WHERE is_tunisian = 1")
    tunisian_posts = cursor.fetchone()[0]
    
    # Posts in last 24h
    cursor.execute("""
        SELECT COUNT(*) FROM posts 
        WHERE scraped_at > datetime('now', '-1 day')
    """)
    posts_last_24h = cursor.fetchone()[0]
    
    # Top hashtags
    cursor.execute("""
        SELECT hashtags_json FROM posts
        WHERE hashtags_json IS NOT NULL
        ORDER BY scraped_at DESC
        LIMIT 100
    """)
    
    hashtag_counter = {}
    for row in cursor.fetchall():
        try:
            tags = json.loads(row[0])
            for tag in tags:
                hashtag_counter[tag] = hashtag_counter.get(tag, 0) + 1
        except:
            pass
    
    top_hashtags = sorted(hashtag_counter.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Average likes
    cursor.execute("SELECT AVG(likes) FROM posts WHERE likes > 0")
    avg_likes = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_posts": total_posts,
        "tunisian_posts": tunisian_posts,
        "posts_last_24h": posts_last_24h,
        "posts_by_source": posts_by_source,
        "posts_by_type": posts_by_type,
        "posts_by_sentiment": posts_by_sentiment,
        "top_hashtags": [{"tag": tag, "count": count} for tag, count in top_hashtags],
        "avg_likes": round(avg_likes, 2),
    }

def run_api():
    """Run FastAPI server"""
    logger.info("🚀 Starting BehaviorLens API on http://localhost:8000")
    logger.info("📊 Stats: http://localhost:8000/api/stats")
    logger.info("📮 Posts: http://localhost:8000/api/posts?limit=50")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# ════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

def run_spiders(spider_names: Optional[List[str]] = None):
    """Run Scrapy spiders"""
    
    init_database()
    
    if not spider_names:
        spider_names = ["facebook_tn", "tiktok_tn", "instagram_tn"]
    
    process = CrawlerProcess(SCRAPY_SETTINGS)
    
    for spider_name in spider_names:
        if spider_name == "facebook_tn":
            process.crawl(FacebookTNSpider)
        elif spider_name == "tiktok_tn":
            process.crawl(TikTokTNSpider)
        elif spider_name == "instagram_tn":
            process.crawl(InstagramTNSpider)
    
    logger.info(f"🕷️  Starting spiders: {', '.join(spider_names)}")
    process.start()
    
    logger.info("✅ Scraping complete!")

def main():
    parser = argparse.ArgumentParser(
        description="BehaviorLens Social Media Intelligence Pipeline"
    )
    parser.add_argument(
        "--save-session",
        type=str,
        choices=["facebook", "tiktok", "instagram"],
        help="Save login session for a platform"
    )
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run FastAPI server"
    )
    parser.add_argument(
        "--spider",
        type=str,
        help="Run specific spider (facebook_tn, tiktok_tn, instagram_tn)"
    )
    
    args = parser.parse_args()
    
    if args.save_session:
        save_session(args.save_session)
    elif args.api:
        run_api()
    elif args.spider:
        run_spiders([args.spider])
    else:
        run_spiders()

if __name__ == "__main__":
    main()
