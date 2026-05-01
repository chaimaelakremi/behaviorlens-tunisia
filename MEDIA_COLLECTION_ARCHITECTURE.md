# 📡 MEDIA COLLECTION LAYER - STRUCTURED ARCHITECTURE

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────┐
│           MEDIA SOURCES (3 Types)                  │
├─────────────────────────────────────────────────────┤
│  1️⃣ RSS Feeds       2️⃣ User Input      3️⃣ Datasets │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│    UNIFIED COLLECTOR (normalize all)    │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│    STANDARDIZED DATA SCHEMA             │
│  (consistent format for all sources)    │
└────────────────────┬────────────────────┘
                     │
┌────────────────────▼────────────────────┐
│    STORAGE LAYER                        │
│  (JSON / MongoDB / Database)            │
└─────────────────────────────────────────┘
```

---

## 📋 UNIFIED DATA SCHEMA (CRITICAL)

All data must follow this structure:

```json
{
  "id": "unique_identifier",
  "text": "actual content text",
  "source": "rss|user_input|dataset",
  "platform": "news|manual|kaggle",
  "author": "optional author/source name",
  "timestamp": "2026-05-01T10:30:00Z",
  "url": "optional link to original",
  "metadata": {
    "category": "transport|prices|jobs|general",
    "language": "ar|fr|mix",
    "confidence": 0.95
  }
}
```

---

## 📁 FOLDER STRUCTURE

```
behaviorlens-tunisia/
│
├── backend/
│   ├── media_collection/              # 📡 MEDIA LAYER
│   │   ├── __init__.py
│   │   ├── sources/
│   │   │   ├── __init__.py
│   │   │   ├── rss_collector.py       # 📰 RSS feeds
│   │   │   ├── user_input_collector.py # 👤 User input
│   │   │   └── dataset_loader.py       # 📊 Datasets
│   │   ├── normalizer.py              # 🔄 Standardize all
│   │   ├── config.py                  # ⚙️ Configuration
│   │   └── storage.py                 # 💾 Save data
│   │
│   ├── bot_detection/
│   ├── nlp_analysis/
│   ├── analytics/
│   └── main.py
│
├── data/
│   ├── raw/                           # Raw collected data
│   │   ├── rss/
│   │   ├── user_input/
│   │   └── datasets/
│   ├── processed/                     # After normalization
│   └── feeds_config.json              # RSS sources list
│
└── README.md
```

---

## ⚙️ CONFIGURATION FILE

Create `backend/media_collection/config.py`:

```python
# RSS FEEDS CONFIGURATION
RSS_FEEDS = {
    "news_world": {
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "general",
        "language": "en"
    },
    "news_economy": {
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
        "category": "prices",
        "language": "en"
    },
    "tunisia_news": {
        "url": "https://www.tap.info.tn/fr/rss",
        "category": "general",
        "language": "fr"
    }
}

# USER INPUT SOURCES
USER_INPUT_ENABLED = True
USER_INPUT_CHANNELS = ["cli", "web_form", "telegram_bot"]  # Future expansion

# DATASET SOURCES
DATASETS = {
    "kaggle_twitter_sentiment": {
        "path": "data/raw/datasets/twitter_sentiment.csv",
        "type": "csv",
        "columns": ["text", "sentiment"]
    },
    "arabic_dialect_corpus": {
        "path": "data/raw/datasets/arabic_dialect.csv",
        "type": "csv",
        "columns": ["text", "dialect"]
    }
}

# STORAGE
STORAGE_TYPE = "json"  # json | mongodb | postgresql
STORAGE_PATH = "data/processed/posts.json"

# COLLECTION INTERVAL
RSS_FETCH_INTERVAL = 300  # seconds (5 minutes)
USER_INPUT_REALTIME = True
```

---

## 🔧 SOURCE 1: RSS COLLECTOR

File: `backend/media_collection/sources/rss_collector.py`

```python
import feedparser
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSCollector:
    """Collects data from RSS feeds (news sources)"""
    
    def __init__(self, feeds_config: Dict):
        self.feeds = feeds_config
        self.collected_posts = []
    
    def collect_from_feed(self, feed_name: str, feed_url: str) -> List[Dict]:
        """
        Fetch posts from a single RSS feed
        """
        try:
            logger.info(f"Fetching RSS feed: {feed_name}")
            feed = feedparser.parse(feed_url)
            
            posts = []
            
            for entry in feed.entries[:50]:  # Limit to 50 per feed
                post = {
                    "id": f"rss_{feed_name}_{entry.get('id', entry['link'])}",
                    "text": self._clean_text(entry.title, entry.get("summary", "")),
                    "source": "rss",
                    "platform": feed_name,
                    "author": entry.get("author", "Unknown"),
                    "timestamp": self._parse_date(entry.get("published", "")),
                    "url": entry.get("link", ""),
                    "metadata": {
                        "category": "general",
                        "language": "en",
                        "confidence": 0.9
                    }
                }
                posts.append(post)
            
            logger.info(f"Collected {len(posts)} posts from {feed_name}")
            return posts
        
        except Exception as e:
            logger.error(f"Error fetching {feed_name}: {str(e)}")
            return []
    
    def collect_all(self) -> List[Dict]:
        """
        Collect from all configured feeds
        """
        all_posts = []
        
        for feed_name, feed_config in self.feeds.items():
            posts = self.collect_from_feed(feed_name, feed_config["url"])
            all_posts.extend(posts)
        
        self.collected_posts = all_posts
        return all_posts
    
    @staticmethod
    def _clean_text(title: str, summary: str) -> str:
        """Clean and combine title + summary"""
        text = f"{title} {summary}".strip()
        # Remove HTML tags if any
        import re
        text = re.sub(r"<[^>]+>", "", text)
        return text[:500]  # Limit to 500 chars
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Parse date to ISO format"""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()


# USAGE EXAMPLE
if __name__ == "__main__":
    from config import RSS_FEEDS
    
    collector = RSSCollector(RSS_FEEDS)
    posts = collector.collect_all()
    
    print(f"Collected {len(posts)} RSS posts")
    for post in posts[:3]:
        print(f"  - {post['text'][:100]}...")
```

---

## 👤 SOURCE 2: USER INPUT COLLECTOR

File: `backend/media_collection/sources/user_input_collector.py`

```python
from datetime import datetime
from typing import List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserInputCollector:
    """Collects opinions directly from users"""
    
    def __init__(self):
        self.posts = []
        self.input_methods = ["cli", "web_form"]
    
    def collect_from_cli(self, batch_size: int = 5) -> List[Dict]:
        """
        Interactive CLI input (for demo / manual testing)
        """
        logger.info(f"Collecting {batch_size} opinions from CLI...")
        
        posts = []
        
        print("\n" + "="*60)
        print("🎤 OPINION COLLECTOR - Type your thoughts (empty line to skip)")
        print("="*60)
        
        for i in range(batch_size):
            print(f"\nOpinion #{i+1}:")
            print("Topics: transport, prices, jobs, politics, education")
            print("> ", end="")
            
            text = input().strip()
            
            if not text:
                continue
            
            # Auto-detect category (simple heuristic)
            category = self._detect_category(text)
            
            post = {
                "id": f"user_input_{datetime.now().timestamp()}_{i}",
                "text": text,
                "source": "user_input",
                "platform": "cli",
                "author": "user",
                "timestamp": datetime.now().isoformat(),
                "url": None,
                "metadata": {
                    "category": category,
                    "language": self._detect_language(text),
                    "confidence": 0.8
                }
            }
            posts.append(post)
        
        self.posts.extend(posts)
        logger.info(f"Collected {len(posts)} user opinions")
        return posts
    
    def collect_from_web_form(self, form_data: Dict) -> Dict:
        """
        Collect from web form submission
        
        Expected form_data:
        {
            "text": "opinion text",
            "category": "transport",
            "location": "Tunis"
        }
        """
        post = {
            "id": f"user_input_{datetime.now().timestamp()}",
            "text": form_data.get("text", ""),
            "source": "user_input",
            "platform": "web_form",
            "author": form_data.get("name", "anonymous"),
            "timestamp": datetime.now().isoformat(),
            "url": None,
            "metadata": {
                "category": form_data.get("category", "general"),
                "language": self._detect_language(form_data.get("text", "")),
                "location": form_data.get("location"),
                "confidence": 0.85
            }
        }
        
        self.posts.append(post)
        return post
    
    @staticmethod
    def _detect_category(text: str) -> str:
        """Simple keyword-based category detection"""
        keywords = {
            "transport": ["transport", "bus", "louage", "metro", "taxi", "route"],
            "prices": ["prix", "prix", "inflation", "cher", "expensive", "coûte"],
            "jobs": ["emploi", "job", "travail", "chômage", "unemployment", "work"],
            "politics": ["politique", "government", "ministre", "politique", "loi"],
            "education": ["école", "université", "education", "enseignement"]
        }
        
        text_lower = text.lower()
        
        for category, kwords in keywords.items():
            if any(kword in text_lower for kword in kwords):
                return category
        
        return "general"
    
    @staticmethod
    def _detect_language(text: str) -> str:
        """Simple language detection"""
        # Basic heuristic
        if any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
            return "ar"  # Arabic
        return "fr"  # Assume French otherwise


# USAGE EXAMPLE
if __name__ == "__main__":
    collector = UserInputCollector()
    posts = collector.collect_from_cli(batch_size=3)
    
    for post in posts:
        print(f"\nCollected: {post['text']}")
        print(f"Category: {post['metadata']['category']}")
```

---

## 📊 SOURCE 3: DATASET LOADER

File: `backend/media_collection/sources/dataset_loader.py`

```python
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads historical data from CSV/Kaggle datasets"""
    
    def __init__(self, datasets_config: Dict):
        self.datasets = datasets_config
        self.posts = []
    
    def load_dataset(self, dataset_name: str) -> List[Dict]:
        """
        Load a single dataset file
        """
        try:
            if dataset_name not in self.datasets:
                logger.error(f"Dataset {dataset_name} not found in config")
                return []
            
            config = self.datasets[dataset_name]
            file_path = config["path"]
            
            logger.info(f"Loading dataset: {dataset_name} from {file_path}")
            
            # Load CSV
            df = pd.read_csv(file_path, encoding='utf-8')
            
            posts = []
            
            for idx, row in df.iterrows():
                # Create consistent timestamp spread over past 30 days
                days_ago = random.randint(0, 30)
                timestamp = (datetime.now() - timedelta(days=days_ago)).isoformat()
                
                post = {
                    "id": f"dataset_{dataset_name}_{idx}",
                    "text": str(row.get("text", row.get("content", ""))),
                    "source": "dataset",
                    "platform": dataset_name,
                    "author": str(row.get("author", "dataset_user")),
                    "timestamp": timestamp,
                    "url": None,
                    "metadata": {
                        "category": str(row.get("category", "general")),
                        "language": self._detect_language_from_text(str(row.get("text", ""))),
                        "original_sentiment": row.get("sentiment", None),
                        "confidence": 0.75
                    }
                }
                posts.append(post)
            
            logger.info(f"Loaded {len(posts)} posts from {dataset_name}")
            self.posts.extend(posts)
            return posts
        
        except FileNotFoundError:
            logger.error(f"Dataset file not found: {file_path}")
            return []
        except Exception as e:
            logger.error(f"Error loading dataset {dataset_name}: {str(e)}")
            return []
    
    def load_all(self) -> List[Dict]:
        """Load all configured datasets"""
        all_posts = []
        
        for dataset_name in self.datasets.keys():
            posts = self.load_dataset(dataset_name)
            all_posts.extend(posts)
        
        return all_posts
    
    def load_sample(self, sample_size: int = 100) -> List[Dict]:
        """Load random sample for quick demo"""
        all_posts = self.load_all()
        return random.sample(all_posts, min(sample_size, len(all_posts)))
    
    @staticmethod
    def _detect_language_from_text(text: str) -> str:
        """Detect language from text content"""
        if any(ord(c) >= 0x0600 and ord(c) <= 0x06FF for c in text):
            return "ar"
        return "fr"


# USAGE EXAMPLE
if __name__ == "__main__":
    from config import DATASETS
    
    loader = DatasetLoader(DATASETS)
    posts = loader.load_sample(sample_size=50)
    
    print(f"Loaded {len(posts)} sample posts")
    for post in posts[:3]:
        print(f"  - {post['text'][:80]}...")
```

---

## 🔄 NORMALIZER (Unifies all sources)

File: `backend/media_collection/normalizer.py`

```python
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataNormalizer:
    """
    Standardizes all posts from different sources
    into a unified schema
    """
    
    REQUIRED_FIELDS = [
        "id", "text", "source", "platform",
        "author", "timestamp", "url", "metadata"
    ]
    
    @staticmethod
    def normalize(posts: List[Dict]) -> List[Dict]:
        """
        Ensure all posts match the schema
        """
        normalized = []
        
        for post in posts:
            try:
                normalized_post = DataNormalizer._validate_post(post)
                normalized.append(normalized_post)
            except Exception as e:
                logger.warning(f"Skipping invalid post: {str(e)}")
                continue
        
        logger.info(f"Normalized {len(normalized)} posts")
        return normalized
    
    @staticmethod
    def _validate_post(post: Dict) -> Dict:
        """
        Validate and fill missing fields
        """
        validated = {}
        
        # Required fields
        for field in DataNormalizer.REQUIRED_FIELDS:
            if field not in post:
                if field == "metadata":
                    validated[field] = {"category": "general", "language": "unknown"}
                else:
                    validated[field] = None
            else:
                validated[field] = post[field]
        
        # Validate text is not empty
        if not validated["text"] or len(str(validated["text"]).strip()) < 5:
            raise ValueError("Text too short")
        
        # Ensure metadata is dict
        if not isinstance(validated["metadata"], dict):
            validated["metadata"] = {"category": "general", "language": "unknown"}
        
        return validated
    
    @staticmethod
    def deduplicate(posts: List[Dict]) -> List[Dict]:
        """
        Remove duplicate posts (same text)
        """
        seen = set()
        unique = []
        
        for post in posts:
            text_hash = hash(post["text"])
            
            if text_hash not in seen:
                seen.add(text_hash)
                unique.append(post)
        
        logger.info(f"Removed {len(posts) - len(unique)} duplicates")
        return unique


# USAGE EXAMPLE
if __name__ == "__main__":
    sample_posts = [
        {"text": "hello", "source": "rss"},
        {"text": "world", "source": "user"},
    ]
    
    normalized = DataNormalizer.normalize(sample_posts)
    unique = DataNormalizer.deduplicate(normalized)
    
    print(f"Final: {len(unique)} unique posts")
```

---

## 💾 STORAGE LAYER

File: `backend/media_collection/storage.py`

```python
import json
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageManager:
    """Handles data persistence"""
    
    def __init__(self, storage_type: str = "json", path: str = "data/processed/posts.json"):
        self.storage_type = storage_type
        self.path = path
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
    
    def save(self, posts: List[Dict]):
        """Save posts to storage"""
        if self.storage_type == "json":
            self._save_json(posts)
        else:
            logger.error(f"Unsupported storage type: {self.storage_type}")
    
    def load(self) -> List[Dict]:
        """Load posts from storage"""
        if self.storage_type == "json":
            return self._load_json()
        return []
    
    def _save_json(self, posts: List[Dict]):
        """Save to JSON file"""
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(posts)} posts to {self.path}")
        except Exception as e:
            logger.error(f"Error saving JSON: {str(e)}")
    
    def _load_json(self) -> List[Dict]:
        """Load from JSON file"""
        try:
            if not Path(self.path).exists():
                logger.warning(f"File not found: {self.path}")
                return []
            
            with open(self.path, 'r', encoding='utf-8') as f:
                posts = json.load(f)
            logger.info(f"Loaded {len(posts)} posts from {self.path}")
            return posts
        except Exception as e:
            logger.error(f"Error loading JSON: {str(e)}")
            return []
```

---

## 🎯 MAIN ORCHESTRATOR

File: `backend/media_collection/__init__.py`

```python
from .sources.rss_collector import RSSCollector
from .sources.user_input_collector import UserInputCollector
from .sources.dataset_loader import DatasetLoader
from .normalizer import DataNormalizer
from .storage import StorageManager
from .config import RSS_FEEDS, DATASETS, STORAGE_TYPE, STORAGE_PATH
import logging

logger = logging.getLogger(__name__)


class MediaCollectionPipeline:
    """
    Main orchestrator for all media collection
    """
    
    def __init__(self):
        self.rss_collector = RSSCollector(RSS_FEEDS)
        self.user_collector = UserInputCollector()
        self.dataset_loader = DatasetLoader(DATASETS)
        self.storage = StorageManager(STORAGE_TYPE, STORAGE_PATH)
    
    def collect_all(self, include_user_input=True):
        """
        Collect from all sources
        """
        logger.info("=" * 60)
        logger.info("STARTING MEDIA COLLECTION PIPELINE")
        logger.info("=" * 60)
        
        # Collect from RSS
        rss_posts = self.rss_collector.collect_all()
        logger.info(f"✅ RSS: {len(rss_posts)} posts")
        
        # Collect from user (if enabled)
        user_posts = []
        if include_user_input:
            user_posts = self.user_collector.collect_from_cli(batch_size=2)
            logger.info(f"✅ User Input: {len(user_posts)} posts")
        
        # Load from datasets
        dataset_posts = self.dataset_loader.load_sample(sample_size=100)
        logger.info(f"✅ Datasets: {len(dataset_posts)} posts")
        
        # Combine all
        all_posts = rss_posts + user_posts + dataset_posts
        logger.info(f"\n📊 Total posts before normalization: {len(all_posts)}")
        
        # Normalize
        normalized_posts = DataNormalizer.normalize(all_posts)
        
        # Deduplicate
        unique_posts = DataNormalizer.deduplicate(normalized_posts)
        logger.info(f"📊 Final posts after deduplication: {len(unique_posts)}")
        
        # Save
        self.storage.save(unique_posts)
        
        logger.info("=" * 60)
        logger.info("✅ MEDIA COLLECTION COMPLETE")
        logger.info("=" * 60)
        
        return unique_posts
    
    def get_posts(self):
        """Load previously collected posts"""
        return self.storage.load()


# QUICK START
if __name__ == "__main__":
    pipeline = MediaCollectionPipeline()
    posts = pipeline.collect_all(include_user_input=False)  # Skip user input for demo
    
    # Show samples
    print("\n" + "="*60)
    print("SAMPLE POSTS")
    print("="*60)
    for post in posts[:3]:
        print(f"\n📝 {post['source'].upper()}")
        print(f"Text: {post['text'][:100]}...")
        print(f"Category: {post['metadata']['category']}")
```

---

## 📊 SCHEMA VISUALIZATION

```
┌─────────────────────────────────────────────────────┐
│         POST OBJECT STRUCTURE                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ✓ id (string)                                      │
│    └─ unique identifier per post                   │
│                                                     │
│  ✓ text (string)                                    │
│    └─ main content (500 chars max)                 │
│                                                     │
│  ✓ source (enum)                                    │
│    └─ ["rss", "user_input", "dataset"]             │
│                                                     │
│  ✓ platform (string)                                │
│    └─ where it came from (bbci, user, kaggle)      │
│                                                     │
│  ✓ author (string)                                  │
│    └─ who wrote/posted it                          │
│                                                     │
│  ✓ timestamp (ISO 8601)                             │
│    └─ when it was created                          │
│                                                     │
│  ✓ url (string, nullable)                           │
│    └─ link to original content                     │
│                                                     │
│  ✓ metadata (object)                                │
│    ├─ category: string                              │
│    ├─ language: string (ar|fr|en)                   │
│    ├─ confidence: float (0-1)                       │
│    └─ extra fields per source                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 QUICK SETUP GUIDE

### 1. Install dependencies
```bash
pip install feedparser pandas
```

### 2. Create folder structure
```bash
mkdir -p backend/media_collection/sources
mkdir -p data/raw/{rss,user_input,datasets}
mkdir -p data/processed
```

### 3. Create configuration
```bash
# Copy config.py to backend/media_collection/
```

### 4. Run collection
```bash
python -m backend.media_collection
```

---

## 📌 KEY FEATURES

✅ **Multi-source collection** (RSS + user + datasets)

✅ **Unified schema** (all data normalized)

✅ **Legal & safe** (no scraping/API restrictions)

✅ **Scalable** (add new sources easily)

✅ **Real-time ready** (streams + batch)

✅ **Deduplication** (no duplicate posts)

---

## 🔗 INTEGRATION POINTS

This feeds into:
- 🤖 **Bot Detection Layer** (next step)
- 🧠 **NLP Analysis** (sentiment, topics)
- 📊 **Analytics Engine** (trends, alerts)
- 📺 **Dashboard** (visualization)
