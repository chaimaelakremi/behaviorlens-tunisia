# InsightTN - Tunisian Opinion Intelligence Platform

**Real-time collection and analysis of Tunisian social media opinions using Graph API and web scraping.**

---

## 🎯 What This Does

InsightTN collects posts and comments from Facebook and Instagram about Tunisian topics, and analyzes them for:

- **Sentiment** (positive, negative, neutral)
- **Language** (Arabic, French, English, mixed)
- **Dialect** (Tunisian vs Standard Arabic)
- **Post type** (news, complaint, opinion, humor, etc.)
- **Bot behavior** (detects fake accounts)
- **Hashtags & mentions** (topic extraction)
- **Engagement** (likes, comments, shares)

Perfect for understanding public opinion, detecting emerging issues, and monitoring sentiment trends in Tunisia.

---

## 🚀 Quick Start (2 minutes)

### Run Demo (No Setup Needed)
```bash
python demo_extraction.py
python graph_api_demo.py
python setup_and_status.py
```

### Full Setup (20 minutes)
1. Get Facebook token → https://developers.facebook.com
2. Install packages → `uv pip install feedparser requests pandas python-dotenv`
3. Set environment → `$env:FACEBOOK_ACCESS_TOKEN = "your_token"`
4. Collect data → `python -m social_media.app --collect`

**See:** [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) for step-by-step guide

---

## 📂 Important Files

### 🚀 Start Here
- **[QUICK_START.py](QUICK_START.py)** - Display this guide: `python QUICK_START.py`
- **[SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)** - Step-by-step setup checklist
- **[COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)** - Full setup guide with all options

### 📊 See It Working
- **[demo_extraction.py](demo_extraction.py)** - See sample Tunisian social media posts (no setup needed)
- **[graph_api_demo.py](graph_api_demo.py)** - Learn how Graph API works (no setup needed)
- **[setup_and_status.py](setup_and_status.py)** - Check what's installed

### 📚 Documentation
- **[SYSTEM_STATUS.md](SYSTEM_STATUS.md)** - System overview and status
- **[GRAPH_API_SETUP.md](GRAPH_API_SETUP.md)** - Detailed Graph API setup
- **[FACEBOOK_INSTAGRAM_API_GUIDE.md](FACEBOOK_INSTAGRAM_API_GUIDE.md)** - Why Graph API is best
- **[HYBRID_SCRAPER_PROMPT.md](HYBRID_SCRAPER_PROMPT.md)** - Web scraper architecture
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - All documentation

### ⚙️ Core Code
- **[social_media/](social_media/)** - Main collection system
  - `app.py` - Collection orchestrator
  - `graph_api_collector.py` - Official Facebook/Instagram API
  - `config.py` - Configuration for all platforms
  - `utils.py` - Analysis and processing

- **[backend/media_collection/](backend/media_collection/)** - Data pipeline layer

---

## 📋 Architecture

### Two Collection Methods

```
┌─────────────────────────────────────────────────┐
│         InsightTN Collection System             │
├─────────────────────────────────────────────────┤
│                                                 │
│  ✅ Graph API (Official)      ⚙️ Web Scraper    │
│  • Facebook pages              • Supplementary  │
│  • Instagram business          • Any site       │
│  • 99.9% reliable              • Fallback       │
│  • Fast (100-500ms)            • Slower         │
│  • Legal ✓                     • Respectful     │
│                                                 │
│  ► Use this for production                      │
│                                                 │
└──────────┬───────────────────────────┬──────────┘
           │                           │
           └───────────┬───────────────┘
                       ▼
          ┌──────────────────────────┐
          │   Unified Processor      │
          │ • Normalize schema       │
          │ • Analyze sentiment      │
          │ • Extract hashtags       │
          │ • Detect language        │
          │ • Classify posts         │
          │ • Check for bots         │
          └──────────┬───────────────┘
                     ▼
          ┌──────────────────────────┐
          │    Data Storage (JSON)   │
          │ • Local files            │
          │ • MongoDB-ready format   │
          │ • Time-series support    │
          └──────────────────────────┘
```

---

## 💻 Usage Examples

### Collect All Data
```bash
# Using Graph API (official, recommended)
python -m social_media.app --collect

# Using web scraper (optional)
python -m social_media.app --collect --mode scraper

# Hybrid (both sources)
python -m social_media.app --collect --mode hybrid

# Fallback (try API, use scraper if needed)
python -m social_media.app --collect --mode fallback
```

### Interactive Menu
```bash
python -m social_media.app
# Shows menu to collect, view stats, export, etc.
```

### Test Before Full Setup
```bash
# Demo with sample data (no dependencies)
python demo_extraction.py

# See Graph API setup requirements
python graph_api_demo.py

# Check what's installed
python setup_and_status.py
```

---

## 📊 Data You Get

Each extracted post includes:

```json
{
  "id": "sm_fb_001",
  "source": "graph_api",
  "platform": "facebook",
  "author": "Mosaique FM",
  "text": "Post content in Arabic or French",
  "sentiment": "negative",
  "language": "ar",
  "is_tunisian": true,
  "post_type": "news",
  "hashtags": ["#tunisia", "#news"],
  "engagement": {
    "likes": 1234,
    "comments": 87,
    "shares": 45
  },
  "comments": [
    {
      "author": "Ahmed Ben Ali",
      "text": "Comment text",
      "sentiment": "negative",
      "likes": 234
    }
  ],
  "timestamp": "2026-05-01T10:30:00Z"
}
```

---

## 🔧 Installation

### Prerequisites
- Python 3.8+
- Internet connection
- ~500MB disk space

### Core Setup (5 minutes)
```bash
uv pip install feedparser requests pandas python-dotenv
```

### Optional: Web Scraper (10 minutes)
```bash
uv pip install scrapy scrapy-playwright --only-binary :all:
```

### Get Graph API Access (5 minutes)
1. Go to: https://developers.facebook.com
2. Create app → Choose "Business"
3. Get credentials
4. Set environment: `$env:FACEBOOK_ACCESS_TOKEN = "your_token"`

**Full guide:** [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)

---

## ✨ Key Features

### Collection
- ✅ Official Facebook Graph API (primary)
- ✅ Official Instagram Graph API (primary)
- ✅ RSS feed fallback
- ✅ Optional web scraping (Scrapy)
- ✅ Automatic deduplication
- ✅ Error handling & retries

### Analysis
- ✅ Sentiment detection (positive/negative/neutral)
- ✅ Language detection (Arabic/French/English/mixed)
- ✅ Tunisian dialect detection
- ✅ Post type classification (8 categories)
- ✅ Bot behavior detection
- ✅ Hashtag & mention extraction
- ✅ Urgency scoring

### Data
- ✅ JSON format output
- ✅ MongoDB-ready schema
- ✅ Full comment threads
- ✅ Engagement metrics
- ✅ Author information
- ✅ Timestamps & timezone handling

### Operations
- ✅ Single-command collection
- ✅ Interactive menu interface
- ✅ Logging & debugging
- ✅ Configurable settings
- ✅ Batch export
- ✅ Statistics & reporting

---

## 📈 Use Cases

### Real-Time Monitoring
Track what people are saying about your brand, topic, or organization right now.

### Crisis Detection
Automatically alert when negative sentiment spikes or critical issues emerge.

### Trend Analysis
See which topics are trending and how opinions are evolving over time.

### Public Opinion Polling
Understand what Tunisians think about policies, events, or products.

### Competitor Intelligence
Monitor mentions and sentiment for competitors or similar organizations.

### Research & Analytics
Collect data for academic research, business intelligence, or journalism.

---

## 🆘 Troubleshooting

### "No module named 'feedparser'"
```bash
uv pip install feedparser requests pandas python-dotenv
```

### "FACEBOOK_ACCESS_TOKEN not set"
```bash
$env:FACEBOOK_ACCESS_TOKEN = "your_token_from_developers.facebook.com"
```

### "Graph API returns 400 error"
- Verify token is valid (test at developers.facebook.com)
- Confirm page ID is correct and public
- Check token has correct permissions
- Ensure token hasn't expired

### "Can't install Scrapy (C++ error)"
```bash
# Try pre-built wheels (easiest)
uv pip install scrapy --only-binary :all:

# Or use Docker
docker run -it python:3.11 pip install scrapy
```

### More help?
1. Check [GRAPH_API_SETUP.md](GRAPH_API_SETUP.md) troubleshooting section
2. Run `python setup_and_status.py` to diagnose issues
3. Read [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)

---

## 📞 Support Resources

| Need | Go To |
|------|-------|
| Quick start | [QUICK_START.py](QUICK_START.py) |
| Setup steps | [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) |
| Full guide | [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md) |
| API details | [GRAPH_API_SETUP.md](GRAPH_API_SETUP.md) |
| Scraper info | [HYBRID_SCRAPER_PROMPT.md](HYBRID_SCRAPER_PROMPT.md) |
| System status | [SYSTEM_STATUS.md](SYSTEM_STATUS.md) |
| All docs | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |

---

## 🎯 Next Steps

### Right Now (5 minutes)
1. Run: `python demo_extraction.py` - See demo data
2. Run: `python graph_api_demo.py` - Learn setup
3. Run: `python setup_and_status.py` - Check status

### Then (20 minutes)
1. Install packages: `uv pip install feedparser requests pandas python-dotenv`
2. Get Graph API token from developers.facebook.com
3. Set environment: `$env:FACEBOOK_ACCESS_TOKEN = "your_token"`
4. Collect data: `python -m social_media.app --collect`

### Finally (Optional)
- Install web scraper for supplementary data
- Set up scheduled collection
- Build analytics dashboard
- Deploy to production

---

## 📄 License & Compliance

- ✅ Uses official Facebook Graph API (compliant)
- ✅ Uses official Instagram Graph API (compliant)
- ✅ Web scraper respects robots.txt
- ✅ Data usage complies with platform TOS
- ✅ GDPR-ready (includes data export)

---

## 🇹🇳 About Tunisia

Tunisia is a North African country with ~12 million people and a vibrant, politically active social media community. This system helps understand the public discourse, monitor emerging issues, and measure sentiment in real-time.

---

## 🚀 Ready to Start?

1. **Quick preview:** `python demo_extraction.py`
2. **Follow checklist:** [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md)
3. **Get data:** `python -m social_media.app --collect`

**That's it!** You now have real-time Tunisian social media intelligence. 🎉

---

## 📝 Version Info

- **System:** InsightTN v1.0
- **Last Updated:** May 2026
- **Status:** Production Ready ✅
- **Python:** 3.8+
- **Dependencies:** feedparser, requests, pandas, python-dotenv (optional: scrapy, playwright)

---

**Made with ❤️ for Tunisia**

