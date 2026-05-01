"""
Configuration for Social Media Collection System
Defines all data sources, keywords, and platform-specific settings
"""

import os
from datetime import datetime, timedelta

# ============================================================================
# SOCIAL MEDIA PLATFORMS & KEYWORDS
# ============================================================================

SOCIAL_MEDIA_CONFIG = {
    # Twitter/X - Simulation mode (using RSS fallback)
    "twitter_rss": {
        "enabled": True,
        "platform": "twitter_rss",
        "description": "Twitter trending topics via RSS feeds",
        "urls": [
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://feeds.reuters.com/reuters/businessNews",
        ],
        "keywords": [
            "tunisia", "tunisie", "tunis",
            "fuel prices", "transport", "economy",
            "job market", "unemployment", "salary"
        ],
        "update_interval": 300,  # 5 minutes
        "post_limit": 50,
    },
    
    # Facebook - Using public pages RSS
    "facebook_pages": {
        "enabled": True,
        "platform": "facebook_pages",
        "description": "Facebook public pages (news organizations, NGOs)",
        "pages": [
            "Tunisia News",
            "BBC Tunisia",
            "Reuters Tunisia",
            "France24 Tunisia"
        ],
        "keywords": [
            "economic crisis", "inflation", "prices",
            "transportation", "public services",
            "social issues", "government"
        ],
        "update_interval": 600,  # 10 minutes
        "post_limit": 50,
    },
    
    # Facebook - Using Graph API (official, requires credentials)
    "facebook_graph_api": {
        "enabled": False,  # Requires FACEBOOK_ACCESS_TOKEN env var
        "platform": "facebook_graph_api",
        "description": "Facebook official Graph API (requires authorization)",
        "graph_api_page_ids": [],  # Add your page IDs here
        "include_comments": True,  # Collect comment threads
        "post_limit": 50,
        "note": "Set FACEBOOK_ACCESS_TOKEN environment variable to enable"
    },
    
    # Instagram - Legal alternative (hashtag RSS feeds)
    "instagram_hashtags": {
        "enabled": True,
        "platform": "instagram_hashtags",
        "description": "Instagram public hashtags via RSS (legal method)",
        "hashtags": [
            "#tunisia",
            "#tunisie",
            "#tunis",
            "#tunisianproblems",
            "#tunisiaeconomy",
            "#transport",
            "#fuel"
        ],
        "keywords": [
            "problems", "issues", "crisis", "expensive",
            "shortage", "broken", "need", "help"
        ],
        "update_interval": 300,
        "post_limit": 40,
    },
    
    # Instagram - Using Graph API (official, requires credentials)
    "instagram_graph_api": {
        "enabled": False,  # Requires FACEBOOK_ACCESS_TOKEN env var
        "platform": "instagram_graph_api",
        "description": "Instagram official Graph API (requires authorization)",
        "graph_api_business_account_ids": [],  # Add your Business Account IDs
        "include_comments": True,  # Collect comment threads
        "post_limit": 40,
        "note": "Set FACEBOOK_ACCESS_TOKEN environment variable to enable"
    },
    
    # TikTok - Using trending hashtags RSS
    "tiktok_trends": {
        "enabled": True,
        "platform": "tiktok_trends",
        "description": "TikTok trending sounds/hashtags (via public data feeds)",
        "hashtags": [
            "#tunisiatrending",
            "#tunisianchallenge",
            "#tunisiavoice"
        ],
        "keywords": [
            "day in my life", "problems", "struggle",
            "expensive", "can't afford", "angry"
        ],
        "update_interval": 600,
        "post_limit": 30,
    },
    
    # LinkedIn - Professional sentiment
    "linkedin_posts": {
        "enabled": False,  # Requires API key
        "platform": "linkedin_posts",
        "description": "LinkedIn posts on business/economy (via RSS where available)",
        "urls": [],
        "keywords": [
            "tunisia business", "startup", "employment",
            "career", "economy", "market"
        ],
        "post_limit": 25,
    },
    
    # Reddit - Public subreddits (RSS)
    "reddit_communities": {
        "enabled": True,
        "platform": "reddit_communities",
        "description": "Reddit r/Tunisia and related communities",
        "subreddits": [
            "Tunisia",
            "northafrica",
            "MENA"
        ],
        "keywords": [
            "tunisia", "economy", "problems",
            "government", "transport", "prices"
        ],
        "post_limit": 40,
    },
    
    # YouTube - Trending in Tunisia
    "youtube_comments": {
        "enabled": False,  # Requires API
        "platform": "youtube_comments",
        "description": "YouTube trending video comments (Tunisia region)",
        "keywords": [
            "tunisia", "economy", "government", "social"
        ],
    },
}

# ============================================================================
# SENTIMENT & EMOTION KEYWORDS
# ============================================================================

SENTIMENT_KEYWORDS = {
    "positive": [
        "love", "great", "excellent", "amazing", "thank",
        "happy", "good", "wonderful", "proud", "success",
        "beautiful", "best", "brilliant", "awesome"
    ],
    "negative": [
        "hate", "bad", "terrible", "awful", "angry",
        "sad", "disappointed", "disgusted", "upset",
        "problem", "issue", "crisis", "failed", "worst",
        "expensive", "overpriced", "broken", "corrupt"
    ],
    "urgent": [
        "emergency", "crisis", "urgent", "immediate",
        "now", "immediately", "asap", "help", "please",
        "need", "must", "can't", "no more"
    ],
    "social_media_specific": [
        "viral", "trending", "repost", "share", "like",
        "comment", "tag", "mention", "follow", "subscribe"
    ]
}

# ============================================================================
# TOPIC CATEGORIES (Tunisian Context)
# ============================================================================

TOPIC_CATEGORIES = {
    "economic": [
        "prices", "inflation", "economy", "market", "business",
        "investment", "financial", "money", "currency", "dinar",
        "expensive", "cost", "afford", "budget"
    ],
    "transport": [
        "transport", "bus", "train", "taxi", "traffic",
        "road", "fuel", "gas", "petrol", "car", "drive",
        "metro", "public transport", "travel"
    ],
    "employment": [
        "job", "work", "employment", "unemployment", "salary",
        "wage", "income", "career", "business", "startup",
        "hire", "fired", "layoff", "contract"
    ],
    "government": [
        "government", "politics", "law", "parliament", "president",
        "minister", "policy", "regulation", "decision", "reform",
        "corruption", "election", "vote"
    ],
    "social": [
        "education", "health", "hospital", "school", "university",
        "student", "teacher", "doctor", "medicine", "insurance"
    ],
    "security": [
        "security", "safety", "crime", "theft", "police",
        "terrorist", "attack", "violence", "dangerous"
    ],
}

# ============================================================================
# LANGUAGE DETECTION
# ============================================================================

LANGUAGE_SETTINGS = {
    "primary": ["ar", "fr", "en"],  # Arabic, French, English
    "supported": ["ar", "fr", "en", "mix"],
    "arabic_keywords": {
        "Modern_Standard": ["في", "من", "هذا", "الذي", "التي"],
        "Tunisian_Dialect": ["نحني", "شنوة", "برك", "حاجة", "والو"],
        "French": ["le", "la", "et", "de", "à"],
        "English": ["the", "and", "or", "is", "has"],
    }
}

# ============================================================================
# STORAGE & DATA PATHS
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR]:
    os.makedirs(directory, exist_ok=True)

DATA_FILES = {
    "raw": os.path.join(RAW_DATA_DIR, "raw_posts.json"),
    "processed": os.path.join(PROCESSED_DATA_DIR, "processed_posts.json"),
    "sentiment": os.path.join(PROCESSED_DATA_DIR, "sentiment_analysis.json"),
    "trends": os.path.join(PROCESSED_DATA_DIR, "trends.json"),
    "statistics": os.path.join(PROCESSED_DATA_DIR, "statistics.json"),
}

# ============================================================================
# COLLECTION SETTINGS
# ============================================================================

COLLECTION_SETTINGS = {
    "batch_size": 50,
    "max_posts_per_source": 100,
    "dedup_by": ["text", "author"],  # Fields to check for duplicates
    "min_text_length": 10,  # Minimum characters for valid post
    "max_text_length": 500,  # Truncate longer posts
    "default_language": "ar",
    "confidence_threshold": 0.5,  # Minimum confidence to include
    "refresh_interval": 300,  # Seconds between collection cycles
}

# ============================================================================
# TIME WINDOWS FOR TREND ANALYSIS
# ============================================================================

TIME_WINDOWS = {
    "real_time": timedelta(minutes=1),
    "short": timedelta(minutes=5),
    "medium": timedelta(minutes=30),
    "long": timedelta(hours=1),
    "daily": timedelta(hours=24),
}

# ============================================================================
# ALERTS & THRESHOLDS
# ============================================================================

ALERT_CONFIG = {
    "sentiment_spike": {
        "enabled": True,
        "threshold": 0.7,  # 70% negative sentiment
        "window": TIME_WINDOWS["short"],
        "min_posts": 10,
    },
    "volume_spike": {
        "enabled": True,
        "threshold": 200,  # 200% increase
        "window": TIME_WINDOWS["short"],
    },
    "topic_emergence": {
        "enabled": True,
        "threshold": 50,  # 50 posts about new topic
        "window": TIME_WINDOWS["medium"],
    },
}

# ============================================================================
# HASHTAG MONITORING
# ============================================================================

MONITORED_HASHTAGS = {
    "tunisian_related": [
        "#tunisia", "#tunisie", "#tunis",
        "#tunisianproblems", "#tunisiavoice",
        "#tunisiatrending", "#ilovetunisia"
    ],
    "economic_related": [
        "#economy", "#prices", "#inflation",
        "#costoflivingcrisis", "#expensive", "#inflation"
    ],
    "transport_related": [
        "#transport", "#fuel", "#traffic",
        "#publictransport", "#fuel_shortage"
    ],
    "employment_related": [
        "#job", "#unemployment", "#tunisiajobs",
        "#hiring", "#careerchange"
    ],
}

# ============================================================================
# BOT DETECTION SETTINGS
# ============================================================================

BOT_DETECTION = {
    "enabled": True,
    "check_posting_patterns": True,
    "check_content_similarity": True,
    "check_engagement_ratio": True,
    "thresholds": {
        "posting_frequency": 10,  # Posts per hour
        "similarity_threshold": 0.9,  # 90% identical content
        "engagement_ratio": 0.01,  # Min engagement ratio
    }
}

# ============================================================================
# EXTERNAL INTEGRATIONS (Optional)
# ============================================================================

EXTERNAL_APIS = {
    "twitter_api": {
        "enabled": False,
        "api_key": os.getenv("TWITTER_API_KEY", ""),
        "api_secret": os.getenv("TWITTER_API_SECRET", ""),
        "note": "Only for authorized production use"
    },
    "facebook_api": {
        "enabled": False,
        "app_id": os.getenv("FB_APP_ID", ""),
        "app_secret": os.getenv("FB_APP_SECRET", ""),
        "note": "Only for authorized production use"
    },
}

# ============================================================================
# LOGGING
# ============================================================================

LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "file": os.path.join(DATA_DIR, "logs", "social_media.log"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_size": 10485760,  # 10MB
    "backup_count": 5,
}

# ============================================================================
# SUMMARY
# ============================================================================

def get_config_summary():
    """Return a summary of the current configuration"""
    enabled_platforms = [
        p for p, cfg in SOCIAL_MEDIA_CONFIG.items()
        if cfg.get("enabled", False)
    ]
    
    return {
        "description": "Social Media Intelligence Collection System",
        "version": "1.0.0",
        "enabled_platforms": enabled_platforms,
        "total_sources": len(SOCIAL_MEDIA_CONFIG),
        "supported_languages": LANGUAGE_SETTINGS["supported"],
        "categories": list(TOPIC_CATEGORIES.keys()),
        "data_dir": DATA_DIR,
        "collection_interval": COLLECTION_SETTINGS["refresh_interval"],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_config_summary(), indent=2))
