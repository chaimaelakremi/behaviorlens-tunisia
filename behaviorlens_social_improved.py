#!/usr/bin/env python3
"""
BehaviorLens Social Media Intelligence Pipeline
Tunisian social media data collection and analysis for hackathon

Install:
    pip install scrapy scrapy-playwright playwright fastapi uvicorn aiofiles
    pip install fastapi[standard]
    playwright install chromium
    mkdir sessions

Usage:
    python behaviorlens_social.py                         # Run all spiders
    python behaviorlens_social.py --save-session facebook
    python behaviorlens_social.py --save-session tiktok
    python behaviorlens_social.py --save-session instagram
    python behaviorlens_social.py --api                   # Start FastAPI server
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
from typing import Dict, List, Optional
from urllib.parse import urljoin

# Scrapy & Playwright
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DropItem
from scrapy_playwright.page import PageMethod

# Playwright for session management
from playwright.sync_api import sync_playwright

# FastAPI
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

DB_NAME = "behaviorlens.db"
SESSIONS_DIR = "sessions"
OUTPUT_FILE = "behaviorlens_output.jsonl"

Path(SESSIONS_DIR).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

# ════════════════════════════════════════════════════════════════════════════════
# CLASSIFICATION KEYWORDS
# ════════════════════════════════════════════════════════════════════════════════

KEYWORDS = {
    "complaint": [
        "مشكل", "مشاكل", "problème", "problèmes", "catastrophe", "غالي", "cher",
        "kharba", "خربة", "hchouma", "تعب", "تعبان", "déçu", "honte", "مخزي",
        "كارثة", "ظلم", "غالي جدا", "سيء", "وجع", "ألم", "فضيحة", "نحرق",
    ],
    "opinion": [
        "اعتقد", "أعتقد", "برأيي", "je pense", "selon moi", "mon avis",
        "رأيي", "personnellement", "في رأيي", "نحسبو", "نقول",
    ],
    "news": [
        "عاجل", "breaking", "urgent", "خبر", "أخبار", "officiel", "annonce",
        "communiqué", "déclaration", "جديد", "أخير", "إعلان", "تصريح", "نبأ",
        "وزير", "رئيس", "حكومة", "رسمي",
    ],
    "humor": [
        "😂", "🤣", "hhhh", "هههه", "loool", "lol", "مضحك", "طريف",
        "باهي يعيش", "واش", "نكتة", "ههههه", "😁", "😆", "xD",
    ],
    "promotion": [
        "solde", "promo", "تخفيض", "discount", "offre", "عرض", "livraison",
        "gratuit", "مجاني", "commander", "اشتري", "شراء", "بيع", "توصيل",
        "نقص من السعر", "prix", "سعر",
    ],
    "question": [
        "كيف", "comment faire", "pourquoi", "why", "متى",
        "quand", "شكون", "وين", "أين", "شنوة", "إش",
    ],
    "event": [
        "حفل", "concert", "festival", "soirée", "invitation", "موعد", "inscription",
        "حفلة", "تجمع", "ملتقى", "اجتماع", "دعوة",
    ],
}

POSITIVE_KEYWORDS = [
    "برشا مليح", "بارك", "تمام", "super", "excellent", "bravo", "شكرا",
    "شكراً", "مرحبا", "نجاح", "فرحة", "فرحان", "😍", "❤️", "👍", "🎉",
    "mabrouk", "مبروك", "ألف مبروك", "yesss", "yeah", "والله يفرجها",
    "بالتوفيق", "جميل", "راهو حسن", "شنيع",
]

NEGATIVE_KEYWORDS = [
    "مشكل", "كارثة", "hchouma", "مخزي", "غالي", "barrani", "ظلم", "corruption",
    "فساد", "😡", "😢", "💔", "لا", "ما تمام", "سيء",
    "خطير", "وجع", "ألم", "مقرف", "فاشل", "ما بهيش",
]

TUNISIAN_GEOGRAPHIC = [
    "tunisie", "tunis", "sfax", "sousse", "monastir", "gabes", "bizerte",
    "kairouan", "gafsa", "jendouba", "kef", "kasserine", "sidi bouzid",
    "تونس", "صفاقس", "سوسة", "منستير", "قابس", "بنزرت", "القيروان",
    "قفصة", "جندوبة", "الكاف", "القصرين", "سيدي بوزيد",
]

TUNISIAN_DIALECT = [
    "barcha", "برشا", "mta3", "متاع", "yezzi", "يزي", "fisa3",
    "manich", "مانيش", "behi", "بهي", "3ayech", "عايش", "chwiya", "شوية",
    "taw", "تو", "wallah", "وللاه", "weld", "bneta",
    "nheb", "نحب", "maak", "نحي", "ahna", "بالزوز",
]

TUNISIAN_INSTITUTIONS = [
    "mosaique", "shems", "jawhara", "attessia", "watania", "express.fm",
    "tap tna", "مساء", "شمس", "جوهرة", "الوطنية",
]

TUNISIAN_HASHTAG_PATTERNS = [
    "tunisie", "tunis", "تونس", "تونسي", "تونسية", "sfax", "sousse", "tunisian",
]

# ════════════════════════════════════════════════════════════════════════════════
# DATABASE
# ════════════════════════════════════════════════════════════════════════════════

def init_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            url TEXT,
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
            is_tunisian INTEGER,
            language TEXT,
            scraped_at TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            text TEXT,
            likes INTEGER DEFAULT 0,
            sentiment TEXT,
            is_tunisian INTEGER,
            hashtags_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info(f"✅ Database ready: {DB_NAME}")


def post_exists(post_id: str) -> bool:
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id FROM posts WHERE post_id = ?", (post_id,))
        found = c.fetchone() is not None
        conn.close()
        return found
    except Exception:
        return False


def insert_post(post: Dict) -> bool:
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("""
            INSERT INTO posts
            (source, url, post_id, author, text, media_type, hashtags_json,
             likes, shares, comments_count, post_type, sentiment, is_tunisian, language, scraped_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            post.get("source"), post.get("url"), post.get("post_id"),
            post.get("author"), post.get("text"), post.get("media_type"),
            json.dumps(post.get("hashtags", [])),
            post.get("likes", 0), post.get("shares", 0),
            post.get("comments_count", 0), post.get("post_type"),
            post.get("sentiment"), int(post.get("is_tunisian", False)),
            post.get("language"), post.get("scraped_at"),
        ))
        for comment in post.get("comments", []):
            c.execute("""
                INSERT INTO comments (post_id, text, likes, sentiment, is_tunisian, hashtags_json)
                VALUES (?,?,?,?,?,?)
            """, (
                post.get("post_id"), comment.get("text"), comment.get("likes", 0),
                comment.get("sentiment"), int(comment.get("is_tunisian", False)),
                json.dumps(comment.get("hashtags", [])),
            ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # duplicate
    except Exception as e:
        logger.error(f"DB insert error: {e}")
        return False

# ════════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def extract_hashtags(text: str) -> List[str]:
    if not text:
        return []
    return list(set(re.findall(r'#\S+', text)))


def detect_tunisian(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for kw in TUNISIAN_GEOGRAPHIC + TUNISIAN_DIALECT + TUNISIAN_INSTITUTIONS:
        if kw.lower() in text_lower:
            return True
    # Check hashtags in text against patterns
    for tag in extract_hashtags(text):
        tag_lower = tag.lower().lstrip('#')
        if any(p in tag_lower for p in TUNISIAN_HASHTAG_PATTERNS):
            return True
    return False


def detect_language(text: str) -> str:
    if not text:
        return "unknown"
    text_lower = text.lower()
    if any(m in text_lower for m in TUNISIAN_DIALECT):
        return "tunisian_dialect"
    arabic = len(re.findall(r'[\u0600-\u06FF]', text))
    latin = len(re.findall(r'[a-zA-Z]', text))
    total = len(text) or 1
    if arabic / total > 0.4:
        return "arabic"
    if latin / total > 0.4:
        return "french"
    return "mixed"


def classify_post_type(text: str) -> str:
    if not text:
        return "general"
    text_lower = text.lower()
    for post_type, keywords in KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return post_type
    return "general"


def classify_sentiment(text: str) -> str:
    if not text:
        return "neutral"
    text_lower = text.lower()
    pos = sum(1 for kw in POSITIVE_KEYWORDS if kw in text_lower)
    neg = sum(1 for kw in NEGATIVE_KEYWORDS if kw in text_lower)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def extract_number(text: str) -> int:
    if not text:
        return 0
    text = text.upper().replace("K", "000").replace("M", "000000")
    m = re.search(r'\d+', text)
    return int(m.group()) if m else 0


def make_post_id(source: str, url: str, extra: str = "") -> str:
    raw = f"{source}_{url}_{extra}"
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def build_post_item(
    source: str, url: str, post_id: str, author: str,
    text: str, comments: List[Dict], media_type: str = "text",
    likes: int = 0, shares: int = 0,
) -> Dict:
    combined = text + " " + " ".join(c.get("text", "") for c in comments)
    return {
        "source": source,
        "url": url,
        "post_id": post_id,
        "author": author,
        "text": text,
        "media_type": media_type,
        "hashtags": extract_hashtags(text),
        "likes": likes,
        "shares": shares,
        "comments_count": len(comments),
        "post_type": classify_post_type(combined),
        "sentiment": classify_sentiment(combined),
        "is_tunisian": detect_tunisian(combined),
        "language": detect_language(combined),
        "scraped_at": datetime.now().isoformat(),
        "comments": [
            {
                "text": c.get("text", ""),
                "likes": c.get("likes", 0),
                "sentiment": classify_sentiment(c.get("text", "")),
                "is_tunisian": detect_tunisian(c.get("text", "")),
                "hashtags": extract_hashtags(c.get("text", "")),
            }
            for c in comments
        ],
    }

# ════════════════════════════════════════════════════════════════════════════════
# PIPELINES
# ════════════════════════════════════════════════════════════════════════════════

class TunisianFilterPipeline:
    def process_item(self, item, spider):
        if item.get("is_tunisian"):
            return item
        if any(c.get("is_tunisian") for c in item.get("comments", [])):
            return item
        hashtags_lower = " ".join(item.get("hashtags", [])).lower()
        if any(p in hashtags_lower for p in TUNISIAN_HASHTAG_PATTERNS):
            return item
        raise DropItem(f"Non-Tunisian: {item.get('post_id')}")


class DeduplicationPipeline:
    def process_item(self, item, spider):
        if post_exists(item.get("post_id", "")):
            raise DropItem(f"Duplicate: {item.get('post_id')}")
        return item


class SQLitePipeline:
    def process_item(self, item, spider):
        if insert_post(item):
            logger.info(f"✅ Saved [{item.get('source')}] {item.get('post_id')} — {item.get('post_type')} / {item.get('sentiment')}")
        return item

# ════════════════════════════════════════════════════════════════════════════════
# SPIDER HELPERS
# ════════════════════════════════════════════════════════════════════════════════

def _context_meta(context_name: str, session_file: str, extra_methods: list = None) -> Dict:
    """Build playwright meta dict, with session if file exists"""
    meta = {
        "playwright": True,
        "playwright_include_page": True,
        "playwright_page_methods": extra_methods or [],
    }
    if Path(session_file).exists():
        meta["playwright_context"] = context_name
    return meta

# ════════════════════════════════════════════════════════════════════════════════
# SPIDERS
# ════════════════════════════════════════════════════════════════════════════════

class FacebookTNSpider(scrapy.Spider):
    name = "facebook_tn"
    custom_settings = {"PLAYWRIGHT_CONTEXTS": _build_contexts()}

    TARGET_PAGES = [
        "https://www.facebook.com/Mosaique.fm",
        "https://www.facebook.com/shemsfm.tunisie",
        "https://www.facebook.com/JarraTv",
        "https://www.facebook.com/attessia.tv",
        "https://www.facebook.com/tap.tna",
    ]

    def start_requests(self):
        session_file = f"{SESSIONS_DIR}/facebook_session.json"
        for url in self.TARGET_PAGES:
            meta = {
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 4000),
                    PageMethod("evaluate", "window.scrollBy(0, 2000)"),
                    PageMethod("wait_for_timeout", 2000),
                    PageMethod("evaluate", "window.scrollBy(0, 2000)"),
                    PageMethod("wait_for_timeout", 2000),
                ],
            }
            if Path(session_file).exists():
                meta["playwright_context"] = "facebook"
            yield scrapy.Request(url, meta=meta, errback=self.errback)

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        logger.info(f"📘 Facebook: {response.url}")

        try:
            # Try multiple selector strategies for post text
            selectors = [
                "div[data-ad-comet-preview='message']",
                "div[data-ad-preview='message']",
                "[data-testid='post_message']",
                "div.xdj266r",          # current FB class
                "div[dir='auto'] span",
            ]

            posts_data = []
            for sel in selectors:
                elements = response.css(f"{sel}")
                if elements:
                    for i, el in enumerate(elements[:8]):
                        text = " ".join(el.css("::text").getall()).strip()
                        if text and len(text) > 10:
                            posts_data.append((i, text))
                    if posts_data:
                        break

            # If CSS selectors fail, use Playwright to extract via JS
            if not posts_data and page:
                try:
                    texts = await page.evaluate("""
                        () => {
                            const els = document.querySelectorAll('[dir="auto"]');
                            return Array.from(els)
                                .map(e => e.innerText.trim())
                                .filter(t => t.length > 20)
                                .slice(0, 8);
                        }
                    """)
                    posts_data = [(i, t) for i, t in enumerate(texts)]
                except Exception as e:
                    logger.warning(f"JS extraction failed: {e}")

            author = response.url.split("/")[-1] or "facebook_page"

            for idx, text in posts_data:
                post_id = make_post_id("facebook", response.url, str(idx))

                # Try to extract comments via playwright
                comments = []
                if page:
                    try:
                        comment_texts = await page.evaluate("""
                            () => {
                                const els = document.querySelectorAll('[aria-label*="Comment"] [dir="auto"]');
                                return Array.from(els)
                                    .map(e => e.innerText.trim())
                                    .filter(t => t.length > 3)
                                    .slice(0, 15);
                            }
                        """)
                        comments = [{"text": t, "likes": 0} for t in comment_texts if t]
                    except Exception:
                        pass

                # Detect media type
                has_video = bool(response.css("video"))
                has_img = bool(response.css("img[src*='scontent']"))
                media_type = "video" if has_video else ("image" if has_img else "text")

                item = build_post_item(
                    source="facebook",
                    url=response.url,
                    post_id=post_id,
                    author=author,
                    text=text,
                    comments=comments,
                    media_type=media_type,
                )
                yield item

        except Exception as e:
            logger.error(f"❌ Facebook parse error: {e}")
        finally:
            if page:
                await page.close()

    def errback(self, failure):
        logger.error(f"❌ Facebook request failed: {failure.getErrorMessage()}")


class TikTokTNSpider(scrapy.Spider):
    name = "tiktok_tn"

    TARGET_HASHTAGS = [
        "https://www.tiktok.com/tag/tunisie",
        "https://www.tiktok.com/tag/tunis",
        "https://www.tiktok.com/tag/تونس",
        "https://www.tiktok.com/tag/تونسي",
        "https://www.tiktok.com/tag/sfax",
        "https://www.tiktok.com/tag/sousse",
    ]

    def start_requests(self):
        session_file = f"{SESSIONS_DIR}/tiktok_session.json"
        for url in self.TARGET_HASHTAGS:
            meta = {
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 5000),
                    PageMethod("evaluate", "window.scrollBy(0, 4000)"),
                    PageMethod("wait_for_timeout", 3000),
                ],
            }
            if Path(session_file).exists():
                meta["playwright_context"] = "tiktok"
            yield scrapy.Request(url, meta=meta, errback=self.errback)

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        logger.info(f"🎵 TikTok: {response.url}")

        try:
            # Collect video hrefs
            video_links = []
            selectors = [
                "a[href*='/video/']",
                "[data-e2e='challenge-item'] a",
                "div[class*='DivWrapper'] a",
            ]
            for sel in selectors:
                links = response.css(f"{sel}::attr(href)").getall()
                if links:
                    video_links = list(set(links))[:10]
                    break

            if not video_links and page:
                try:
                    video_links = await page.evaluate("""
                        () => [...document.querySelectorAll('a[href*="/video/"]')]
                            .map(a => a.href)
                            .filter((v, i, a) => a.indexOf(v) === i)
                            .slice(0, 10)
                    """)
                except Exception:
                    pass

            hashtag = response.url.split("/tag/")[-1] if "/tag/" in response.url else "tunisie"

            for idx, href in enumerate(video_links):
                video_url = href if href.startswith("http") else urljoin("https://www.tiktok.com", href)
                video_id = href.split("/video/")[-1].split("?")[0] if "/video/" in href else make_post_id("tiktok", href, "")

                # Try to get caption text from the page
                caption_parts = response.css("[data-e2e='video-desc']::text, .video-meta-caption::text").getall()
                text = " ".join(caption_parts).strip() or f"#{hashtag} TikTok video"

                likes_text = response.css(f"[data-e2e='like-count']::text").get() or "0"

                item = build_post_item(
                    source="tiktok",
                    url=video_url,
                    post_id=f"tiktok_{video_id}",
                    author=f"tiktok_creator_{idx}",
                    text=text,
                    comments=[],  # would need individual video visit for comments
                    media_type="video",
                    likes=extract_number(likes_text),
                )
                yield item

        except Exception as e:
            logger.error(f"❌ TikTok parse error: {e}")
        finally:
            if page:
                await page.close()

    def errback(self, failure):
        logger.error(f"❌ TikTok request failed: {failure.getErrorMessage()}")


class InstagramTNSpider(scrapy.Spider):
    name = "instagram_tn"

    TARGET_PROFILES = [
        "https://www.instagram.com/mosaiquefm/",
        "https://www.instagram.com/shemsfm/",
        "https://www.instagram.com/tunisienumerique/",
        "https://www.instagram.com/tap.tna/",
    ]

    def start_requests(self):
        session_file = f"{SESSIONS_DIR}/instagram_session.json"
        for url in self.TARGET_PROFILES:
            meta = {
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_timeout", 4000),
                    PageMethod("evaluate", "window.scrollBy(0, 3000)"),
                    PageMethod("wait_for_timeout", 2000),
                ],
            }
            if Path(session_file).exists():
                meta["playwright_context"] = "instagram"
            yield scrapy.Request(url, meta=meta, errback=self.errback)

    async def parse(self, response):
        page = response.meta.get("playwright_page")
        logger.info(f"📷 Instagram: {response.url}")

        try:
            # Collect post hrefs
            post_links = response.css("a[href*='/p/']::attr(href)").getall()

            if not post_links and page:
                try:
                    post_links = await page.evaluate("""
                        () => [...document.querySelectorAll('a[href*="/p/"]')]
                            .map(a => a.getAttribute('href'))
                            .filter((v, i, a) => a.indexOf(v) === i)
                            .slice(0, 8)
                    """)
                except Exception:
                    pass

            author = response.url.rstrip("/").split("/")[-1]

            for idx, href in enumerate(post_links[:8]):
                post_url = urljoin("https://www.instagram.com", href)
                post_short = href.split("/p/")[-1].strip("/") if "/p/" in href else make_post_id("ig", href, "")

                # Caption from the page (partial — full caption needs visiting post URL)
                caption_parts = response.css("article span::text").getall()
                text = " ".join(caption_parts[:50]).strip() or f"Tunisian Instagram post by @{author}"

                # Detect media type
                has_video = bool(response.css("video"))
                media_type = "video" if has_video else "image"

                # Extract visible comments
                comment_texts = response.css("ul li span::text").getall()
                comments = [{"text": t.strip(), "likes": 0} for t in comment_texts if len(t.strip()) > 3][:15]

                item = build_post_item(
                    source="instagram",
                    url=post_url,
                    post_id=f"ig_{post_short}_{idx}",
                    author=author,
                    text=text,
                    comments=comments,
                    media_type=media_type,
                )
                yield item

        except Exception as e:
            logger.error(f"❌ Instagram parse error: {e}")
        finally:
            if page:
                await page.close()

    def errback(self, failure):
        logger.error(f"❌ Instagram request failed: {failure.getErrorMessage()}")

# ════════════════════════════════════════════════════════════════════════════════
# SCRAPY SETTINGS
# ════════════════════════════════════════════════════════════════════════════════

def _build_contexts() -> Dict:
    """Build PLAYWRIGHT_CONTEXTS only for session files that exist"""
    contexts = {}
    for platform in ["facebook", "tiktok", "instagram"]:
        sf = f"{SESSIONS_DIR}/{platform}_session.json"
        if Path(sf).exists():
            contexts[platform] = {"storage_state": sf}
    return contexts


SCRAPY_SETTINGS = {
    "BOT_NAME": "behaviorlens",
    "USER_AGENT": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "DOWNLOAD_HANDLERS": {
        "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    },
    "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    "PLAYWRIGHT_BROWSER_TYPE": "chromium",
    "PLAYWRIGHT_LAUNCH_OPTIONS": {
        "headless": True,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    },
    "PLAYWRIGHT_CONTEXTS": _build_contexts(),
    "DOWNLOAD_DELAY": 3,
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
    "CONCURRENT_REQUESTS": 1,
    "ROBOTSTXT_OBEY": False,
    "ITEM_PIPELINES": {
        "__main__.TunisianFilterPipeline": 200,
        "__main__.DeduplicationPipeline": 300,
        "__main__.SQLitePipeline": 400,
    },
    "FEEDS": {
        OUTPUT_FILE: {"format": "jsonl"},
    },
    "LOG_LEVEL": "INFO",
}

# ════════════════════════════════════════════════════════════════════════════════
# SESSION SAVE UTILITY
# ════════════════════════════════════════════════════════════════════════════════

PLATFORM_URLS = {
    "facebook": "https://www.facebook.com/login",
    "tiktok":   "https://www.tiktok.com/login",
    "instagram": "https://www.instagram.com/accounts/login",
}

def save_session(platform: str):
    if platform not in PLATFORM_URLS:
        logger.error(f"Unknown platform: {platform}. Choose facebook, tiktok or instagram.")
        return

    session_file = f"{SESSIONS_DIR}/{platform}_session.json"
    login_url = PLATFORM_URLS[platform]

    print(f"\n🔐  Opening {platform.upper()} login page...")
    print("   Log in manually in the browser window that opens.")
    print("   Once you are fully logged in and see your feed, come back here.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(login_url)

        input("✋  Press Enter here once you are logged in...")

        context.storage_state(path=session_file)
        browser.close()

    print(f"✅  Session saved → {session_file}")
    print(f"    Run spiders now with: python behaviorlens_social.py --spider {platform}_tn\n")

# ════════════════════════════════════════════════════════════════════════════════
# FASTAPI — with CORS for React frontend
# ════════════════════════════════════════════════════════════════════════════════

app = FastAPI(title="BehaviorLens Social Intelligence API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # React dev server can call freely
    allow_methods=["*"],
    allow_headers=["*"],
)


def db_rows(query: str, params: tuple = ()) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def db_scalar(query: str, params: tuple = ()):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(query, params)
    val = c.fetchone()
    conn.close()
    return val[0] if val else None


@app.get("/api/posts")
async def get_posts(
    source: Optional[str] = Query(None),
    post_type: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    is_tunisian: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    query = "SELECT * FROM posts WHERE 1=1"
    params: list = []
    if source:
        query += " AND source=?"; params.append(source)
    if post_type:
        query += " AND post_type=?"; params.append(post_type)
    if sentiment:
        query += " AND sentiment=?"; params.append(sentiment)
    if is_tunisian is not None:
        query += " AND is_tunisian=?"; params.append(int(is_tunisian))
    query += " ORDER BY scraped_at DESC LIMIT ?"
    params.append(limit)
    posts = db_rows(query, tuple(params))
    return {"total": len(posts), "posts": posts}


@app.get("/api/posts/recent")
async def get_recent(limit: int = Query(20, ge=1, le=100)):
    posts = db_rows("SELECT * FROM posts ORDER BY scraped_at DESC LIMIT ?", (limit,))
    return {"total": len(posts), "posts": posts}


@app.get("/api/stats")
async def get_stats():
    total = db_scalar("SELECT COUNT(*) FROM posts") or 0

    by_source = {r["source"]: r["cnt"] for r in db_rows(
        "SELECT source, COUNT(*) AS cnt FROM posts GROUP BY source")}

    by_type = {r["post_type"]: r["cnt"] for r in db_rows(
        "SELECT post_type, COUNT(*) AS cnt FROM posts GROUP BY post_type")}

    by_sentiment = {r["sentiment"]: r["cnt"] for r in db_rows(
        "SELECT sentiment, COUNT(*) AS cnt FROM posts GROUP BY sentiment")}

    tunisian_count = db_scalar("SELECT COUNT(*) FROM posts WHERE is_tunisian=1") or 0

    # Top hashtags
    hashtag_rows = db_rows("SELECT hashtags_json FROM posts WHERE hashtags_json IS NOT NULL LIMIT 200")
    counter: Dict[str, int] = {}
    for row in hashtag_rows:
        try:
            for tag in json.loads(row["hashtags_json"]):
                counter[tag] = counter.get(tag, 0) + 1
        except Exception:
            pass
    top_hashtags = sorted(counter.items(), key=lambda x: x[1], reverse=True)[:10]

    avg_likes = db_scalar("SELECT AVG(likes) FROM posts WHERE likes > 0") or 0

    # Posts per hour (last 24h)
    since = (datetime.now() - timedelta(hours=24)).isoformat()
    recent_count = db_scalar("SELECT COUNT(*) FROM posts WHERE scraped_at >= ?", (since,)) or 0

    return {
        "total_posts": total,
        "tunisian_posts": tunisian_count,
        "posts_by_source": by_source,
        "posts_by_type": by_type,
        "posts_by_sentiment": by_sentiment,
        "top_hashtags": [{"tag": t, "count": c} for t, c in top_hashtags],
        "avg_likes": round(avg_likes, 2),
        "posts_last_24h": recent_count,
    }


@app.get("/api/comments")
async def get_comments(post_id: Optional[str] = Query(None), limit: int = Query(50)):
    query = "SELECT * FROM comments"
    params: list = []
    if post_id:
        query += " WHERE post_id=?"; params.append(post_id)
    query += " ORDER BY created_at DESC LIMIT ?"; params.append(limit)
    rows = db_rows(query, tuple(params))
    return {"total": len(rows), "comments": rows}


@app.get("/")
async def root():
    return {
        "name": "BehaviorLens Social Intelligence API",
        "endpoints": ["/api/stats", "/api/posts", "/api/posts/recent", "/api/comments"],
        "docs": "/docs",
    }


def run_api():
    init_database()
    logger.info("🚀  API starting at http://localhost:8000")
    logger.info("📊  Stats → http://localhost:8000/api/stats")
    logger.info("📮  Posts → http://localhost:8000/api/posts")
    logger.info("📖  Docs  → http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# ════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════════

SPIDER_MAP = {
    "facebook_tn": FacebookTNSpider,
    "tiktok_tn":   TikTokTNSpider,
    "instagram_tn": InstagramTNSpider,
}


def run_spiders(names: Optional[List[str]] = None):
    init_database()
    names = names or list(SPIDER_MAP.keys())
    # Refresh contexts in case sessions were just saved
    SCRAPY_SETTINGS["PLAYWRIGHT_CONTEXTS"] = _build_contexts()
    process = CrawlerProcess(SCRAPY_SETTINGS)
    for name in names:
        cls = SPIDER_MAP.get(name)
        if cls:
            process.crawl(cls)
        else:
            logger.warning(f"Unknown spider: {name}")
    logger.info(f"🕷️  Running: {', '.join(names)}")
    process.start()
    logger.info("✅  Scraping complete!")


def main():
    parser = argparse.ArgumentParser(description="BehaviorLens Social Media Pipeline")
    parser.add_argument("--save-session", choices=list(PLATFORM_URLS.keys()),
                        help="Save login session for a platform")
    parser.add_argument("--api", action="store_true", help="Start FastAPI server")
    parser.add_argument("--spider", choices=list(SPIDER_MAP.keys()),
                        help="Run a single spider")
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
