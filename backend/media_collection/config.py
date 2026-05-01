# ⚙️ MEDIA COLLECTION CONFIGURATION

# 📰 RSS FEEDS CONFIGURATION
RSS_FEEDS = {
    "bbc_world": {
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "general",
        "language": "en"
    },
    "reuters_business": {
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "category": "prices",
        "language": "en"
    },
    "google_news_tunisia": {
        "url": "https://news.google.com/rss/search?q=Tunisia&hl=en",
        "category": "general",
        "language": "en"
    },
    "france24_africa": {
        "url": "https://www.france24.com/fr/afrique/rss",
        "category": "general",
        "language": "fr"
    }
}

# 👤 USER INPUT SOURCES
USER_INPUT_ENABLED = True
USER_INPUT_CHANNELS = ["cli", "web_form"]

# 📊 DATASET SOURCES
DATASETS = {
    "kaggle_twitter_sentiment": {
        "path": "data/raw/datasets/twitter_sentiment.csv",
        "type": "csv",
        "columns": ["text", "sentiment"],
        "enabled": False  # Set to True when you add the file
    },
    "arabic_dialect_corpus": {
        "path": "data/raw/datasets/arabic_dialect.csv",
        "type": "csv",
        "columns": ["text", "dialect"],
        "enabled": False
    }
}

# 💾 STORAGE CONFIGURATION
STORAGE_TYPE = "json"  # Options: json, mongodb, postgresql
STORAGE_PATH = "data/processed/posts.json"

# ⏱️ TIMING CONFIGURATION
RSS_FETCH_INTERVAL = 300  # seconds (5 minutes)
USER_INPUT_REALTIME = True
BATCH_SIZE_PER_SOURCE = 50

# 🏷️ CATEGORY KEYWORDS
CATEGORY_KEYWORDS = {
    "transport": [
        "transport", "bus", "louage", "metro", "taxi", "route",
        "traffic", "congestion", "vehicle", "driving"
    ],
    "prices": [
        "prix", "price", "inflation", "cher", "expensive", "coûte",
        "cost", "tarif", "essence", "fuel", "expensive"
    ],
    "jobs": [
        "emploi", "job", "travail", "chômage", "unemployment",
        "work", "career", "salaire", "wage", "salary"
    ],
    "politics": [
        "politique", "government", "ministre", "ministère",
        "politique", "loi", "president", "politics"
    ],
    "education": [
        "école", "université", "education", "enseignement",
        "school", "university", "student", "apprentissage"
    ]
}

# 🌍 LANGUAGE DETECTION
ARABIC_UNICODE_RANGE = (0x0600, 0x06FF)
