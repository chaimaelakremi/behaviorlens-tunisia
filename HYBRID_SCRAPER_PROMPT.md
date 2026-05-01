# HYBRID SCRAPER PROMPT - Graph API + Scrapy/Playwright

You are an expert Python developer specializing in social media data collection and scraping.

Build a complete, production-ready hybrid system that combines BOTH Graph API (official) and Scrapy + Playwright (web scraping) for comprehensive Tunisian social media intelligence.

## ARCHITECTURE

The system must have THREE layers:

### Layer 1: OFFICIAL API (Primary - Legal, Fast, Reliable)
- Use existing Graph API integration (Facebook & Instagram official API)
- Collects posts, comments, engagement metrics from official sources
- No scraping, fully compliant
- Status: ACTIVE (already implemented)

### Layer 2: WEB SCRAPER (Secondary - Supplementary Data)
- Use Scrapy + Playwright for platforms/data not available via official APIs
- Collect public Tunisian media pages and trending hashtags
- Extract sentiment, post type, Tunisian dialect markers
- Fallback if Graph API fails or credentials unavailable
- Status: TO BE IMPLEMENTED

### Layer 3: HYBRID AGGREGATOR (Unification Layer)
- Merge data from both Graph API and scraper
- Deduplicate posts (same content from multiple sources)
- Normalize all data to unified schema
- Combine insights from both sources
- Status: TO BE IMPLEMENTED

---

## LAYER 1: EXISTING GRAPH API (Keep As Is)

File: `social-media/graph_api_collector.py` (Already exists)
- Facebook Graph API collector
- Instagram Graph API collector
- Returns normalized posts with comments + engagement

---

## LAYER 2: NEW SCRAPY/PLAYWRIGHT SCRAPER

### Requirements

#### Platforms and Targets:
- **Facebook**: Public Tunisian media pages (Mosaique FM, Shems FM, Jarra TV, Attessia, TAP Tunisie)
- **TikTok**: Public hashtag pages (#tunisie, #tunis, #تونس, #تونسي, #sfax, #sousse)
- **Instagram**: Public profiles (mosaiquefm, shemsfm, tunisienumerique, tap.tna)
- **Reddit**: Tunisian subreddit communities (/r/tunisia, /r/Sfax, etc.)

#### Data to Extract (Per Post):
- Full post text / caption
- Post type classification: complaint, opinion, news, humor, promotion, question, event, general
- Sentiment: positive, negative, neutral
- Media type: text, image, video, reel
- Hashtags found in post text
- `is_tunisian` boolean flag (dialect, keywords, geography)
- Up to 15 comments per post with same metadata
- `comment_count` total

#### Tunisian Detection Signals:

Geographic keywords:
- French: tunisie, tunis, sfax, sousse, monastir, gabes, bizerte, kairouan
- Arabic: تونس, صفاقس, سوسة, منستير, قابس, بنزرت, القيروان

Dialect markers:
- barcha, برشا, mta3, bch, yezzi, يزي, fisa3, manich, مانيش, behi, بهي, 3ayech, عايش, chwiya, شوية, taw, تو

Hashtags:
- #tunisie, #tunis, #تونس, #تونسي, #تونسية, #sfax, #sousse, #tunisian, #tunisia

Institutions:
- mosaique, shems, jawhara, attessia, watania, tap (tunisian agency press)

#### Post Type Classification Keywords:

- **complaint**: مشكل, problème, problem, عايش, تعب, déçu, honte, catastrophe, غالي, cher, كارثة, terrible, awful, disgusting
- **opinion**: اعتقد, برأيي, je pense, i think, selon moi, رأيي, my opinion, imo, imho, honestly
- **news**: عاجل, breaking, urgent, خبر, officiel, annonce, communiqué, official, breaking news, announced
- **humor**: 😂, 🤣, hhhh, هههه, loool, lol, مضحك, funny, hilarious, laugh
- **promotion**: solde, promo, تخفيض, discount, offre, عرض, livraison, gratuit, مجاني, sale, special offer
- **question**: ?, ؟, كيف, comment, how, pourquoi, why, متى, quand, when
- **event**: حفل, concert, festival, evenement, soirée, invitation, event, show, gathering

#### Sentiment Classification:

Positive keywords: جميل, beautiful, رائع, excellent, excellent, bonne, good, أحب, love, يستحق, deserve, فخور, proud, awesome, amazing, wonderful, fantastic

Negative keywords: سيء, bad, رديء, terrible, awful, برا, hate, كره, hate, محبط, disappointed, غاضب, angry, جنون, crazy, فاشل, failed, نسيان, forgotten

### Scrapy Implementation

File: `social-media/behaviorlens_scraper.py`

#### Scrapy Settings:
```python
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_ARGS = ["--disable-blink-features=AutomationControlled"]
PLAYWRIGHT_CONTEXT_ARGS = {
    "ignore_https_errors": True,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
DOWNLOAD_DELAY = 3
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 10
CONCURRENT_REQUESTS = 1
ROBOTSTXT_OBEY = False
```

#### Three Spiders:
1. **FacebookSpider** - Scrapes public Tunisian media pages
2. **TikTokSpider** - Scrapes hashtag pages and video comments
3. **InstagramSpider** - Scrapes public profile posts and comments

#### Three Pipelines:
1. **TunisianFilterPipeline** - Drops non-Tunisian posts
2. **PostTypePipeline** - Re-classifies using combined post + comment text
3. **UnifiedOutputPipeline** - Outputs normalized JSON matching Graph API schema

#### Helper Functions:
- `detect_tunisian(text)` → bool
- `classify_post_type(text)` → str
- `classify_sentiment(text)` → str
- `extract_hashtags(text)` → list
- `build_post_item(source, url, text, comments, media_type, extra)` → dict

#### Output Schema (MUST match Graph API output):
```json
{
  "id": "scraper_facebook_12345",
  "source": "scraper",
  "platform": "facebook",
  "url": "https://facebook.com/...",
  "text": "Post content here...",
  "post_type": "complaint",
  "sentiment": "negative",
  "hashtags": ["#tunisie", "#transport"],
  "media_type": "text",
  "is_tunisian": true,
  "author": "Mosaique FM",
  "timestamp": "2026-05-01T10:30:00Z",
  "engagement": {
    "likes": 234,
    "comments": 12,
    "shares": 5
  },
  "comment_count": 12,
  "comments": [
    {
      "author": "user123",
      "text": "Comment text...",
      "sentiment": "negative",
      "is_tunisian": true,
      "hashtags": [],
      "timestamp": "2026-05-01T10:45:00Z",
      "likes": 23
    }
  ]
}
```

---

## LAYER 3: HYBRID AGGREGATOR

File: `social-media/hybrid_collector.py` (NEW)

### HybridSocialMediaCollector Class

Methods:
```python
class HybridSocialMediaCollector:
    def __init__(self):
        self.graph_api_collector = FacebookInstagramGraphAPICollector()
        self.scraper = BehaviorlensScraperRunner()
        self.normalizer = DataNormalizer()
    
    def collect_all(self, use_graph_api=True, use_scraper=True):
        """
        Collect from both Graph API and scraper
        
        Args:
            use_graph_api: Enable Graph API collection (default True)
            use_scraper: Enable scraper collection (default True)
        
        Returns:
            Unified list of posts from both sources
        """
        posts = []
        
        # Layer 1: Graph API (Primary)
        if use_graph_api and self.graph_api_collector.enabled:
            logger.info("Collecting from Graph API...")
            graph_posts = self.graph_api_collector.collect_all()
            posts.extend(graph_posts)
            logger.info(f"Graph API: {len(graph_posts)} posts collected")
        
        # Layer 2: Scraper (Secondary)
        if use_scraper:
            logger.info("Collecting from web scraper...")
            scraper_posts = self.scraper.run_all_spiders()
            posts.extend(scraper_posts)
            logger.info(f"Scraper: {len(scraper_posts)} posts collected")
        
        # Layer 3: Deduplicate & normalize
        logger.info("Deduplicating posts...")
        unique_posts = self.deduplicate_posts(posts)
        logger.info(f"After deduplication: {len(unique_posts)} posts")
        
        return unique_posts
    
    def deduplicate_posts(self, posts):
        """
        Remove duplicate posts from different sources
        Using text similarity and URL matching
        """
        seen = {}
        unique = []
        
        for post in posts:
            # Generate fingerprint (text + platform)
            text_hash = hashlib.md5(post['text'].encode()).hexdigest()
            fingerprint = f"{post['platform']}_{text_hash}"
            
            if fingerprint not in seen:
                seen[fingerprint] = post
                unique.append(post)
            else:
                # Merge metadata if duplicate found
                existing = seen[fingerprint]
                if 'comments' in post:
                    existing.setdefault('comments', []).extend(post['comments'])
        
        return unique
    
    def collect_from_graph_api_only(self):
        """Official API only - fast, reliable, legal"""
        logger.info("Collecting from Graph API only...")
        return self.collect_all(use_graph_api=True, use_scraper=False)
    
    def collect_from_scraper_only(self):
        """Scraper only - comprehensive, supplementary"""
        logger.info("Collecting from scraper only...")
        return self.collect_all(use_graph_api=False, use_scraper=True)
    
    def collect_with_fallback(self):
        """Try Graph API first, fall back to scraper if failed"""
        try:
            if self.graph_api_collector.enabled:
                logger.info("Trying Graph API (primary)...")
                return self.collect_from_graph_api_only()
        except Exception as e:
            logger.warning(f"Graph API failed: {e}")
        
        logger.info("Falling back to scraper (secondary)...")
        return self.collect_from_scraper_only()
```

---

## LAYER 3: INTEGRATION WITH EXISTING SYSTEM

### Update `social-media/app.py`:

```python
from .hybrid_collector import HybridSocialMediaCollector

class SocialMediaCollector:
    def __init__(self):
        # Existing: Graph API only
        # New: Hybrid approach
        self.hybrid_collector = HybridSocialMediaCollector()
    
    def run_collection_pipeline(self, mode="hybrid"):
        """
        Run collection pipeline
        
        Args:
            mode: "hybrid" (both), "graph_api" (official only), "scraper" (web only), "fallback"
        
        Returns:
            Aggregated posts from selected sources
        """
        if mode == "hybrid":
            posts = self.hybrid_collector.collect_all()
        elif mode == "graph_api":
            posts = self.hybrid_collector.collect_from_graph_api_only()
        elif mode == "scraper":
            posts = self.hybrid_collector.collect_from_scraper_only()
        elif mode == "fallback":
            posts = self.hybrid_collector.collect_with_fallback()
        
        # Normalize and store
        self._normalize_posts(posts)
        self.storage.save(posts)
        
        return posts
```

---

## FILE STRUCTURE

```
social-media/
├─ graph_api_collector.py ← EXISTING (Graph API)
├─ behaviorlens_scraper.py ← NEW (Scrapy + Playwright)
├─ hybrid_collector.py ← NEW (Aggregator)
├─ app.py ← UPDATED (Hybrid integration)
├─ config.py ← UPDATED (Scraper config)
└─ __main__.py ← UPDATED (Hybrid modes)
```

---

## USAGE

### Option 1: Official API Only (Fast, Legal, Reliable)
```bash
python -m social_media.app --mode graph_api --collect
```

### Option 2: Web Scraper Only (Comprehensive, Supplementary)
```bash
python -m social_media.app --mode scraper --collect
```

### Option 3: Hybrid (Both Sources)
```bash
python -m social_media.app --mode hybrid --collect
```

### Option 4: Fallback (Try API, Fall Back to Scraper)
```bash
python -m social_media.app --mode fallback --collect
```

---

## BENEFITS OF HYBRID APPROACH

✅ **Best of Both Worlds**:
- Graph API: Official, legal, fast, reliable
- Scraper: Comprehensive, supplementary, fallback

✅ **Redundancy**:
- If Graph API fails, scraper provides data
- If scraper fails, Graph API still works
- Never without data

✅ **Comprehensive Coverage**:
- Official metrics from Graph API
- Raw sentiment from public comments (scraper)
- Multiple data perspectives

✅ **Legal Compliance**:
- Primary source is official API (no legal risk)
- Scraper is supplementary (not primary)
- Users can choose which methods to use

✅ **Flexibility**:
- Users can switch modes based on needs
- A/B test both approaches
- Gradually migrate to preferred method

---

## INSTALL INSTRUCTIONS

```bash
# Install scrapy + playwright
pip install scrapy scrapy-playwright playwright

# Install playwright browser
playwright install chromium

# Or install both in one command
pip install scrapy scrapy-playwright playwright && playwright install chromium
```

---

## DELIVERABLES

1. **behaviorlens_scraper.py** - Complete Scrapy + Playwright scraper (single file, 1500+ lines)
2. **hybrid_collector.py** - Aggregator that merges both sources
3. **Updated app.py** - Integrated hybrid modes
4. **Updated config.py** - Scraper configuration options
5. **Updated __main__.py** - CLI with mode selection

---

## KEY DIFFERENTIATORS

| Feature | Graph API | Scraper | Hybrid |
|---------|-----------|---------|--------|
| Legal | ✅ YES | ⚠️ Questionable | ✅ YES (Primary) |
| Speed | ✅ Fast | ❌ Slow | ✅ Primary is fast |
| Reliability | ✅ 99.9% | ⚠️ 50-70% | ✅ Fallback support |
| Real-time | ✅ YES | ❌ Delayed | ✅ YES (from API) |
| Engagement | ✅ Official | ❌ Estimated | ✅ Official |
| Comprehensive | ⚠️ Limited | ✅ YES | ✅ YES |
| Flexibility | ❌ Fixed | ✅ Flexible | ✅ Both |
| Fallback | ❌ None | ❌ None | ✅ Both ways |

---

## NOTES

- All outputs MUST match the unified schema (same format from both sources)
- Deduplication prevents double-counting
- Graph API is priority (official source of truth)
- Scraper is supplement (additional context)
- Both can run independently or together
- No breaking changes to existing Graph API code

This hybrid approach gives you:
1. The reliability and legality of official APIs
2. The comprehensiveness and flexibility of web scraping
3. The redundancy and fallback of having both options
4. User choice in which methods to use

Ready to implement? 🚀
