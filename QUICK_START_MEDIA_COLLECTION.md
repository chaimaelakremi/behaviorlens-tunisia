# 🚀 QUICK START GUIDE - MEDIA COLLECTION LAYER

## 📦 Installation

### 1. Install Dependencies
```bash
pip install feedparser pandas
```

### 2. Create Folder Structure
The structure will be created automatically, but you can manually create it:

```bash
mkdir -p backend/media_collection/sources
mkdir -p data/raw/rss
mkdir -p data/raw/user_input
mkdir -p data/raw/datasets
mkdir -p data/processed
```

### 3. Add Configuration
The config.py is already in place. Review it:

```python
backend/media_collection/config.py
```

---

## 🎯 Usage

### OPTION 1: Run the Full Pipeline (RECOMMENDED)

```bash
# From project root
python -m backend.media_collection
```

This will:
1. ✅ Fetch from all configured RSS feeds
2. ✅ Optionally collect user input (interactive)
3. ✅ Load sample from datasets (if available)
4. ✅ Normalize and deduplicate
5. ✅ Save to `data/processed/posts.json`

---

### OPTION 2: Programmatic Usage

```python
from backend.media_collection import MediaCollectionPipeline

# Create pipeline
pipeline = MediaCollectionPipeline()

# Collect data (no user input for automated)
posts = pipeline.collect_all(
    include_rss=True,
    include_user=False,
    include_datasets=True
)

# Get stats
stats = pipeline.get_stats()
print(f"Total posts: {stats['total_posts']}")

# Filter posts
transport_posts = pipeline.get_posts(filters={"category": "transport"})

# Export
pipeline.export("custom_output.json")
```

---

### OPTION 3: Use Individual Collectors

```python
from backend.media_collection.sources.rss_collector import RSSCollector
from backend.media_collection.config import RSS_FEEDS

# Collect from RSS only
collector = RSSCollector(RSS_FEEDS)
posts = collector.collect_all()

# or collect from specific feed
posts = collector.collect_from_feed("bbc_world", RSS_FEEDS["bbc_world"]["url"])
```

---

## 📊 Data Structure

Every post follows this structure:

```json
{
  "id": "rss_bbc_world_12345",
  "text": "News headline and summary...",
  "source": "rss",
  "platform": "bbc_world",
  "author": "BBC",
  "timestamp": "2026-05-01T10:30:00",
  "url": "https://...",
  "metadata": {
    "category": "transport",
    "language": "en",
    "confidence": 0.9
  }
}
```

---

## 🔄 Data Flow

```
┌─────────────────────────────┐
│   3 Data Sources            │
│ ✓ RSS Feeds                │
│ ✓ User Input               │
│ ✓ Datasets                 │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   Collector                 │
│ (gets raw data)             │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   Normalizer                │
│ (convert to schema)         │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   Deduplicator              │
│ (remove duplicates)         │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│   Storage                   │
│ (save to JSON/DB)           │
└─────────────────────────────┘
```

---

## 📝 Configuration

### Add RSS Feeds

Edit `backend/media_collection/config.py`:

```python
RSS_FEEDS = {
    "my_feed": {
        "url": "https://example.com/rss",
        "category": "prices",
        "language": "en"
    }
}
```

### Add Datasets

Place CSV files in `data/raw/datasets/` and update config:

```python
DATASETS = {
    "my_dataset": {
        "path": "data/raw/datasets/my_file.csv",
        "type": "csv",
        "enabled": True
    }
}
```

### Change Storage

```python
STORAGE_TYPE = "json"  # or "mongodb", "postgresql"
STORAGE_PATH = "data/processed/posts.json"
```

---

## 🧪 Testing

### Test RSS Collector
```bash
python -m backend.media_collection.sources.rss_collector
```

### Test User Collector
```bash
python -m backend.media_collection.sources.user_input_collector
```

### Test Dataset Loader
```bash
python -m backend.media_collection.sources.dataset_loader
```

### Test Normalizer
```bash
python -m backend.media_collection.normalizer
```

### Test Storage
```bash
python -m backend.media_collection.storage
```

---

## 📊 Query Collected Data

```python
from backend.media_collection.storage import StorageManager

storage = StorageManager()

# Load all posts
all_posts = storage.load()

# Get by source
rss_posts = storage.get_by_source("rss")
user_posts = storage.get_by_source("user_input")

# Get by category
transport = storage.get_by_category("transport")
prices = storage.get_by_category("prices")

# Get stats
stats = storage.get_stats()
print(stats)
```

---

## 🔗 Next Step: Feed into Pipelines

Your collected posts can now feed into:

### 🤖 Bot Detection
```python
from backend.bot_detection import BotDetector

posts = pipeline.get_posts()
bot_detector = BotDetector()
posts_with_scores = [bot_detector.analyze(p) for p in posts]
```

### 🧠 NLP Analysis
```python
from backend.nlp_analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer()
for post in posts:
    sentiment = analyzer.analyze(post["text"])
    print(sentiment)
```

---

## ⚠️ Troubleshooting

### "feedparser not installed"
```bash
pip install feedparser
```

### "File not found: RSS feed"
- Check internet connection
- Verify RSS feed URLs in config.py
- Some feeds may require User-Agent header

### "Dataset not found"
- Download dataset from Kaggle or other source
- Place CSV in `data/raw/datasets/`
- Enable in config.py: `"enabled": True`

### "Out of memory with large dataset"
- Use `dataset_loader.load_sample(sample_size=100)` for sampling
- Process in batches instead of loading all at once

---

## 📈 Performance Tips

1. **Limit RSS entries**: Change `feed.entries[:50]` to smaller number
2. **Batch processing**: Use `collect_from_list()` with chunks
3. **Incremental collection**: Use `collect_incremental()` for updates
4. **Caching**: Store raw data locally to avoid re-fetching

---

## 🎯 For Your Hackathon

**Step 1: Quick Demo**
```bash
python -m backend.media_collection
```
Run this once to generate `data/processed/posts.json`

**Step 2: Show Results**
```python
pipeline = MediaCollectionPipeline()
posts = pipeline.get_posts()
stats = pipeline.get_stats()
print(f"Collected {len(posts)} posts!")
print(f"Categories: {stats['by_category']}")
```

**Step 3: Feed to Next Layer**
Pass posts to your bot detection and sentiment analysis layers.

---

## 📞 Support

Issues? Check:
1. RSS feeds are valid and accessible
2. All files are in correct folders
3. Dependencies are installed: `pip install feedparser pandas`
4. config.py is properly configured

