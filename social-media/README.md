# BehaviorLens Social Media Collection Layer

**Production-grade modular system for multi-platform Tunisian social media intelligence**

Version: 2.0.0 | Python 3.11+ | Async-First | Type-Annotated

---

## 📋 Overview

The social-media module provides a complete, extensible framework for collecting, processing, and storing social media data with focus on Tunisian content detection and classification.

**Key Features:**
- 🌐 **Multi-platform collection**: Facebook, Instagram, TikTok (via Scrapy), RSS feeds
- 🔗 **Hybrid strategy**: Graph API first, Playwright/Scraping fallback
- 🧠 **Intelligent classification**: Post types, sentiment, language, Tunisian detection
- 🔄 **Async throughout**: Full asyncio support for scalability
- 💾 **Pluggable storage**: SQLite default, PostgreSQL ready
- 🛡️ **Bot detection**: Advanced heuristics for spam/bot accounts
- 📊 **Rich analytics**: Comprehensive stats and metrics
- ⚙️ **Configurable**: Environment variables, settings per platform

---

## 🚀 Quick Start

### Installation

```bash
# Copy social-media folder to your project
cp -r social-media/ /path/to/your/project/

# Install dependencies
pip install pydantic pydantic-settings aiohttp feedparser scrapy scrapy-playwright
```

### Basic Usage

```python
import asyncio
from social_media import SocialMediaCollector

async def main():
    # Initialize collector
    collector = SocialMediaCollector()
    await collector.initialize()
    
    try:
        # Collect posts
        stats = await collector.collect(
            platforms=["facebook", "rss"],
            max_posts=100,
            process=True,
            store=True
        )
        
        print(f"Collected: {stats.total_posts} posts")
        print(f"Tunisian posts: {stats.tunisian_posts}")
        
        # Retrieve posts
        posts = await collector.get_posts(
            filters={"is_tunisian": True},
            limit=10
        )
        
        for post in posts:
            print(f"[@{post.author}] {post.text[:100]}...")
        
    finally:
        await collector.close()

asyncio.run(main())
```

---

## 🏗️ Architecture

### Module Structure

```
social-media/
├── core.py                  # Main orchestrator
├── config.py                # Settings & configuration
├── schemas.py               # Pydantic data models
├── exceptions.py            # Custom exceptions
│
├── collectors/              # Data collection layer
│   ├── base.py             # Abstract collector interface
│   ├── graph_api.py        # Facebook/Instagram Graph API
│   ├── rss.py              # RSS feed collector
│   ├── playwright.py       # Browser automation (Scrapy wrapper)
│   └── hybrid.py           # Smart routing & orchestration
│
├── processors/             # Data enrichment & classification
│   ├── classifier.py       # Post type, sentiment, language detection
│   ├── normalizer.py       # Deduplication and normalization
│   ├── sentiment.py        # Advanced Tunisian sentiment analysis
│   └── bot_detector.py     # Bot detection & spam scoring
│
├── storage/                # Persistence layer
│   ├── base.py             # Abstract storage interface
│   └── sqlite.py           # SQLite implementation
│
└── utils/                  # Utilities
    └── text.py             # Text processing (NER, classification)
```

### Component Interactions

```
User Code
   ↓
┌──────────────────────┐
│  SocialMediaCollector  │ (core.py)
│  - Orchestrator        │
│  - Process pipeline    │
└──────────┬─────────────┘
           ↓
      ┌─────────────────────────────┐
      │  HybridCollector            │ (collectors/hybrid.py)
      │  - Route between collectors │
      └──┬───────┬──────┬──────────┬┘
         ↓       ↓      ↓          ↓
    ┌────────┐ ┌───┐ ┌──────┐ ┌──────────┐
    │GraphAPI│ │RSS│ │Scrape│ │Playwright│
    │ (FB/IG)│ │   │ │      │ │(Browser) │
    └────────┘ └───┘ └──────┘ └──────────┘
           ↓       ↓      ↓          ↓
       Posts (Raw Data)
           ↓
┌──────────────────────────────────┐
│  Post Processing Pipeline        │
│  1. Normalizer (deduplicate)    │
│  2. Classifier (types/sentiment) │
│  3. Sentiment (dialect-aware)   │
│  4. Bot Detector                │
└──────────┬───────────────────────┘
           ↓
     Posts (Enriched)
           ↓
┌──────────────────────┐
│  SQLiteStorage       │
│  - Persist to DB     │
│  - Retrieve & query  │
└──────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# General
BEHAVIORLENS_LOG_LEVEL=INFO
BEHAVIORLENS_DEBUG=false

# Facebook Graph API
BEHAVIORLENS_FACEBOOK_ENABLED=true
BEHAVIORLENS_FACEBOOK_ACCESS_TOKEN=your_token_here
BEHAVIORLENS_FACEBOOK_PAGE_IDS=123456,789012

# Instagram Graph API
BEHAVIORLENS_INSTAGRAM_ENABLED=true
BEHAVIORLENS_INSTAGRAM_ACCESS_TOKEN=your_token_here
BEHAVIORLENS_INSTAGRAM_BUSINESS_ACCOUNT_IDS=111222,333444

# Playwright (Scrapy)
BEHAVIORLENS_PLAYWRIGHT_ENABLED=true
BEHAVIORLENS_PLAYWRIGHT_HEADLESS=true
BEHAVIORLENS_PLAYWRIGHT_TIMEOUT_SECONDS=30

# RSS Feeds
BEHAVIORLENS_RSS_ENABLED=true
BEHAVIORLENS_RSS_FEEDS=https://example.com/feed1,https://example.com/feed2

# Storage
BEHAVIORLENS_STORAGE_DATABASE_URL=sqlite:///behaviorlens.db
BEHAVIORLENS_STORAGE_OUTPUT_JSONL=behaviorlens_output.jsonl

# Classification
BEHAVIORLENS_CLASSIFICATION_DETECT_POST_TYPE=true
BEHAVIORLENS_CLASSIFICATION_DETECT_SENTIMENT=true
BEHAVIORLENS_CLASSIFICATION_DETECT_TUNISIAN=true
```

### Programmatic Configuration

```python
from social_media import Settings

settings = Settings(
    log_level="INFO",
    debug=False,
    max_posts_per_run=500,
    include_comments=True,
)

# Platform-specific
settings.facebook_graph.enabled = True
settings.facebook_graph.access_token = "your_token"
settings.facebook_graph.page_ids = ["123456", "789012"]

# Collectors
from social_media import SocialMediaCollector

collector = SocialMediaCollector(settings=settings)
```

---

## 🔌 Collectors

### Graph API (Facebook & Instagram)

**Best for:** Official accounts with API access, faster retrieval

```python
from social_media.collectors import GraphAPICollector

collector = GraphAPICollector(
    platform="facebook",
    access_token="your_token",
    accounts=["123456", "789012"],
    config={
        "enabled": True,
        "include_comments": True,
        "max_retries": 3,
        "timeout_seconds": 30,
    }
)

posts = await collector.collect()
```

### Playwright (Scrapy Wrapper)

**Best for:** Public accounts, no API needed, comprehensive data

```python
from social_media.collectors import PlaywrightCollector

collector = PlaywrightCollector(
    config={
        "enabled": True,
        "headless": True,
        "timeout_seconds": 30,
        "scroll_pause_ms": 1200,
    }
)

posts = await collector.collect()  # Reads from behaviorlens_output.jsonl
```

### RSS

**Best for:** News aggregation, fast updates

```python
from social_media.collectors import RSSCollector

collector = RSSCollector(
    feeds=[
        "https://mosaiquefm.net/feed",
        "https://shemsfm.net/feed",
    ],
    config={"timeout_seconds": 15}
)

posts = await collector.collect()
```

### Hybrid (Auto-routing)

**Recommended:** Combines all collectors with intelligent fallback

```python
from social_media.collectors import HybridCollector

hybrid = HybridCollector()

# Collect from all enabled sources
posts = await hybrid.collect()

# Collect from specific platforms
posts = await hybrid.collect(platforms=["facebook", "rss"])

# Limit total posts
posts = await hybrid.collect(max_total=100)
```

---

## 🧠 Processors

### Classification

Classifies posts by type, sentiment, language, and Tunisian relevance.

```python
from social_media.processors import PostClassifier

classifier = PostClassifier()

# Classify single post
classification = classifier.classify_post(
    text="Barcha mta3 el kher! 🇹🇳",
    source="facebook"
)

print(classification)
# {
#     'post_type': 'opinion',
#     'sentiment': 'positive',
#     'language': 'tunisian_dialect',
#     'is_tunisian': True,
#     'tunisian_score': 0.85,
#     'confidence': 0.85
# }
```

**Post Types:**
- `complaint`: Issues and problems
- `opinion`: Personal viewpoints
- `news`: News and updates
- `humor`: Funny content
- `question`: Questions and enquiries
- `promotion`: Sales and marketing
- `announcement`: Events and announcements

**Languages:**
- `arabic`: Modern Standard Arabic
- `french`: French
- `tunisian_dialect`: Tunisian Darija
- `mixed`: Multiple languages
- `english`: English

### Sentiment Analysis

Advanced Tunisian dialect sentiment detection.

```python
from social_media.processors import TunisianSentimentAnalyzer

analyzer = TunisianSentimentAnalyzer()

# Analyze with dialect support
result = analyzer.analyze(
    "ألف مبروك علي النتيجة! برشا برشا مليح! 🎉",
    language="tunisian_dialect"
)

print(result)
# {
#     'sentiment': 'positive',
#     'score': 0.95,
#     'confidence': 0.9,
#     'dialect_confidence': 0.95,
#     'matched_expressions': ['ألف مبروك', 'برشا', 'مليح']
# }
```

### Normalization

Deduplicates and cleans post data.

```python
from social_media.processors import PostNormalizer

normalizer = PostNormalizer()

# Check for duplicates
is_dup = normalizer.is_duplicate("Check out this cool link!")
# Fuzzy matching with configurable threshold

# Deduplicate batch
unique_posts = normalizer.deduplicate_posts(posts, threshold=0.85)

# Merge duplicates from multiple sources
merged = normalizer.merge_duplicates(posts)
```

### Bot Detection

Identifies suspicious patterns and bot accounts.

```python
from social_media.processors import BotDetectorAdvanced

detector = BotDetectorAdvanced()

# Score post for bot probability
score, details = detector.detect_bot_score({
    "text": "BUY NOW!!! http://bit.ly/xxx http://tinyurl.com/yyy #followback",
    "author": "user123456",
    "likes": 1000000,
    "shares": 500000,
    "comments_count": 10,
})

print(f"Bot probability: {score:.2%}")
print(f"Details: {details}")
# {
#     'url_spam': True,
#     'excessive_urls': True,
#     'repetitive_content': False,
#     'suspicious_engagement': True,
#     ...
# }
```

---

## 💾 Storage

### SQLite (Default)

```python
from social_media.storage import SQLiteStorage

storage = SQLiteStorage("sqlite:///behaviorlens.db")
await storage.initialize()

# Save posts
saved = await storage.save_posts(posts)

# Query with filters
posts = await storage.get_posts(
    filters={
        "source": "facebook",
        "is_tunisian": True,
        "sentiment": "positive",
        "date_from": datetime(2024, 1, 1),
    },
    limit=50,
    offset=0
)

# Get statistics
stats = await storage.get_stats()
print(f"Total posts: {stats['total_posts']}")
print(f"Tunisian posts: {stats['tunisian_posts']}")
print(f"Posts in last 24h: {stats['posts_last_24h']}")

# Cleanup old data
await storage.delete_old_posts(days=30)

# Close connection
await storage.close()
```

### Database Schema

**posts table:**
```sql
- id (PK)
- post_id (UNIQUE, indexed)
- source (indexed) - facebook, instagram, tiktok, rss
- url
- author
- text
- media_type - text, image, video, reel
- likes, shares, comments_count
- post_type, sentiment, language (indexed)
- is_tunisian (indexed), tunisian_score
- hashtags_json, mentions_json, entities_json
- created_at, scraped_at (indexed), updated_at
```

**comments table:**
```sql
- id (PK)
- post_id (FK, indexed)
- text, author, likes
- sentiment, is_tunisian, language
- hashtags_json
- created_at, scraped_at
```

---

## 📊 Usage Examples

### Complete Collection Pipeline

```python
import asyncio
from social_media import SocialMediaCollector

async def main():
    # Create collector with custom settings
    collector = SocialMediaCollector()
    
    try:
        # Initialize
        await collector.initialize()
        
        # Collect and process
        stats = await collector.collect(
            platforms=["facebook", "instagram", "rss"],
            max_posts=500,
            process=True,
            store=True
        )
        
        print(f"✅ Collection complete")
        print(f"  Total posts: {stats.total_posts}")
        print(f"  Tunisian posts: {stats.tunisian_posts}")
        print(f"  Duration: {stats.collection_duration_seconds:.1f}s")
        
        # Get statistics
        db_stats = await collector.get_stats()
        print(f"\n📊 Database Stats:")
        for source, count in db_stats["posts_by_source"].items():
            print(f"  {source}: {count}")
        
        # Query results
        print(f"\n🇹🇳 Recent Tunisian Posts:")
        posts = await collector.get_posts(
            filters={"is_tunisian": True},
            limit=5
        )
        
        for post in posts:
            print(f"  [{post.sentiment}] {post.text[:60]}...")
            
    finally:
        await collector.close()

asyncio.run(main())
```

### Custom Processing Pipeline

```python
from social_media import SocialMediaCollector
from social_media.processors import PostClassifier, TunisianSentimentAnalyzer

async def custom_pipeline(posts):
    """Custom post processing"""
    classifier = PostClassifier()
    sentiment_analyzer = TunisianSentimentAnalyzer()
    
    enriched = []
    
    for post in posts:
        # Classify
        classification = classifier.classify_post(post.text, post.source)
        
        # Advanced sentiment
        sentiment = sentiment_analyzer.analyze(
            post.text,
            language=classification["language"]
        )
        
        # Update post
        post.post_type = classification["post_type"]
        post.sentiment = sentiment["sentiment"]
        post.language = classification["language"]
        
        enriched.append(post)
    
    return enriched

# Use custom pipeline
collector = SocialMediaCollector()
await collector.initialize()

# Collect raw
raw_posts = await collector.hybrid_collector.collect()

# Apply custom processing
processed = await custom_pipeline(raw_posts)

# Store
await collector.storage.save_posts(processed)
```

### Integration with FastAPI

```python
from fastapi import FastAPI, Query
from social_media import get_collector

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Initialize collector on startup"""
    from social_media import initialize_collector
    await initialize_collector()

@app.get("/api/posts")
async def get_posts(
    source: str = Query(None),
    sentiment: str = Query(None),
    is_tunisian: bool = Query(None),
    limit: int = Query(50, ge=1, le=100),
):
    """Get posts with filters"""
    collector = await get_collector()
    
    filters = {}
    if source:
        filters["source"] = source
    if sentiment:
        filters["sentiment"] = sentiment
    if is_tunisian is not None:
        filters["is_tunisian"] = is_tunisian
    
    posts = await collector.get_posts(filters=filters, limit=limit)
    return [post.model_dump() for post in posts]

@app.post("/api/collect")
async def trigger_collection():
    """Manually trigger collection"""
    collector = await get_collector()
    stats = await collector.collect()
    return stats.model_dump()

@app.get("/api/stats")
async def get_stats():
    """Get collection statistics"""
    collector = await get_collector()
    return await collector.get_stats()

@app.get("/api/health")
async def health_check():
    """Check system health"""
    collector = await get_collector()
    return await collector.health_check()
```

---

## 🛠️ Advanced Topics

### Custom Collector

Implement your own collector for additional data sources:

```python
from social_media.collectors import BaseCollector

class MyCustomCollector(BaseCollector):
    async def collect(self):
        """Your collection logic"""
        posts = []
        # Fetch data...
        return posts
    
    async def health_check(self):
        """Check if collector is working"""
        return {
            "status": "healthy",
            "message": "Custom collector ready",
            "details": {}
        }
```

### Custom Storage Backend

```python
from social_media.storage import StorageBackend

class PostgresStorage(StorageBackend):
    async def initialize(self):
        # Connect to PostgreSQL
        pass
    
    async def save_post(self, post):
        # Insert into PostgreSQL
        pass
    
    # Implement other methods...
```

### Metrics & Monitoring

```python
from prometheus_client import Counter, Histogram

# Create metrics
posts_collected = Counter('posts_collected_total', 'Total posts collected')
tunisian_posts = Counter('tunisian_posts_total', 'Tunisian posts collected')
collection_duration = Histogram('collection_duration_seconds', 'Collection duration')

# In collection code
stats = await collector.collect()
posts_collected.inc(stats.total_posts)
tunisian_posts.inc(stats.tunisian_posts)
collection_duration.observe(stats.collection_duration_seconds)
```

---

## 📝 Database Queries

### Common Queries

```sql
-- Top sources
SELECT source, COUNT(*) as count FROM posts GROUP BY source ORDER BY count DESC;

-- Sentiment distribution
SELECT sentiment, COUNT(*) as count FROM posts GROUP BY sentiment;

-- Posts by language
SELECT language, COUNT(*) as count FROM posts WHERE language IS NOT NULL GROUP BY language;

-- Recent Tunisian content
SELECT * FROM posts WHERE is_tunisian = 1 ORDER BY scraped_at DESC LIMIT 10;

-- Most engaged posts
SELECT text, likes, shares, comments_count FROM posts ORDER BY (likes + shares + comments_count * 10) DESC LIMIT 20;

-- Posts with specific hashtag
SELECT * FROM posts WHERE hashtags_json LIKE '%#tunisie%' LIMIT 20;

-- Bot accounts
SELECT author, COUNT(*) as post_count FROM posts GROUP BY author HAVING post_count > 100 ORDER BY post_count DESC;
```

---

## ✅ Testing

```python
import pytest
from social_media import SocialMediaCollector, PostSchema

@pytest.mark.asyncio
async def test_collection():
    """Test collection pipeline"""
    collector = SocialMediaCollector()
    await collector.initialize()
    
    try:
        stats = await collector.collect(max_posts=10, store=False)
        assert stats.total_posts >= 0
    finally:
        await collector.close()

@pytest.mark.asyncio
async def test_classification():
    """Test post classification"""
    from social_media.processors import PostClassifier
    
    classifier = PostClassifier()
    classification = classifier.classify_post("Barcha mlieh! 🇹🇳")
    
    assert classification["is_tunisian"] == True
    assert classification["language"] in ["tunisian_dialect", "arabic"]

@pytest.mark.asyncio
async def test_storage():
    """Test database operations"""
    from social_media import SQLiteStorage
    
    storage = SQLiteStorage("sqlite:///:memory:")
    await storage.initialize()
    
    post = PostSchema(
        source="test",
        url="https://example.com/1",
        post_id="test_1",
        author="test_user",
        text="Test post"
    )
    
    saved = await storage.save_post(post)
    assert saved == True
    
    retrieved = await storage.get_post("test_1")
    assert retrieved is not None
    assert retrieved.text == "Test post"
```

---

## 🐛 Troubleshooting

### No posts collected

1. Check configuration and API tokens
2. Verify platform is enabled: `BEHAVIORLENS_{PLATFORM}_ENABLED=true`
3. Check collector health: `health = await collector.health_check()`
4. Review logs: Set `BEHAVIORLENS_LOG_LEVEL=DEBUG`

### High duplication rate

1. Adjust fuzzy matching threshold in `PostNormalizer`
2. Check for hash collisions in normalization
3. Verify deduplication is enabled

### Slow collection

1. Increase timeouts: `BEHAVIORLENS_PLAYWRIGHT_TIMEOUT_SECONDS=60`
2. Reduce scroll_pause_ms for faster browsing
3. Run async in parallel: `HybridCollector.collect()`

### Database errors

1. Ensure database directory is writable
2. Check disk space
3. Verify SQLite version >= 3.8

---

## 📚 References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)
- [Scrapy Documentation](https://docs.scrapy.org/)
- [Playwright Documentation](https://playwright.dev/python/)

---

## 📄 License

Part of BehaviorLens Tunisia project

---

## 👥 Contributing

Contributions welcome! Areas for enhancement:

- [ ] PostgreSQL storage backend
- [ ] ClickHouse analytics backend
- [ ] Advanced NLP (entity extraction, topic modeling)
- [ ] Real-time streaming collection
- [ ] Dashboard visualization
- [ ] Performance benchmarking
- [ ] Kubernetes deployment

