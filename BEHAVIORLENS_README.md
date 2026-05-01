# 🌍 BehaviorLens Social Intelligence Pipeline

**Complete Tunisian social media data collection and analysis system in a single Python file**

---

## 📋 What's Included

✅ **3 Scrapy Spiders** (Scrapy + Playwright)
- Facebook: Scrapes Tunisian pages (Mosaique, Shems, Attessia, TAP TNA, Jarra)
- TikTok: Scrapes Tunisian hashtags (#tunisie, #tunis, #تونس, etc.)
- Instagram: Scrapes Tunisian accounts (@mosaiquefm, @shemsfm, etc.)

✅ **Intelligent Classification**
- Post type: complaint, opinion, news, humor, promotion, question, event, general
- Sentiment: positive, negative, neutral
- Language: arabic, french, tunisian_dialect, mixed
- Tunisian detection: geographic markers, dialect words, institutions, hashtags

✅ **Data Storage**
- SQLite database (behaviorlens.db)
- Automatic deduplication
- Comprehensive schema for posts + comments

✅ **FastAPI Dashboard**
- `/api/posts` - Filter by source, type, sentiment
- `/api/stats` - Aggregated insights (top hashtags, sentiment distribution, etc.)

✅ **Session Management**
- Save browser login sessions for authenticated scraping
- Pre-configured contexts for each platform

---

## 🚀 Installation

```bash
# Install dependencies
pip install scrapy scrapy-playwright playwright fastapi uvicorn aiofiles

# Download Chromium
playwright install chromium

# Create sessions folder
mkdir sessions
```

---

## 📖 Usage

### 1. **Run All Spiders (Default)**
```bash
python behaviorlens_social.py
```
Runs Facebook, TikTok, and Instagram spiders sequentially. Outputs to `behaviorlens_output.jsonl` and SQLite.

### 2. **Save Login Sessions** (Optional for authenticated scraping)
```bash
# Facebook
python behaviorlens_social.py --save-session facebook
# Login in the browser, then press Enter

# TikTok
python behaviorlens_social.py --save-session tiktok

# Instagram
python behaviorlens_social.py --save-session instagram
```

Sessions are saved to `sessions/{platform}_session.json` for future authenticated access.

### 3. **Run Specific Spider**
```bash
python behaviorlens_social.py --spider facebook_tn
python behaviorlens_social.py --spider tiktok_tn
python behaviorlens_social.py --spider instagram_tn
```

### 4. **Start API Server**
```bash
python behaviorlens_social.py --api
```

Access on `http://localhost:8000`

#### API Endpoints:

**Get Posts**
```bash
curl "http://localhost:8000/api/posts?limit=50"
curl "http://localhost:8000/api/posts?source=facebook&sentiment=positive&limit=20"
```

**Get Statistics**
```bash
curl "http://localhost:8000/api/stats"
```

Response:
```json
{
  "total_posts": 152,
  "posts_by_source": {
    "facebook": 87,
    "tiktok": 45,
    "instagram": 20
  },
  "posts_by_sentiment": {
    "positive": 65,
    "negative": 42,
    "neutral": 45
  },
  "top_hashtags": [
    {"tag": "#tunisie", "count": 45},
    {"tag": "#tunis", "count": 32}
  ],
  "avg_likes": 234.5
}
```

---

## 🗄️ Database Schema

### posts table
```
- id: PRIMARY KEY
- source: "facebook" | "tiktok" | "instagram"
- url: Post URL
- post_id: Unique identifier
- author: Account/page name
- text: Full caption/body
- media_type: "text" | "image" | "video" | "reel" | "carousel"
- hashtags_json: JSON array of hashtags
- likes: Integer
- shares: Integer
- comments_count: Integer
- post_type: Classification
- sentiment: Classification
- is_tunisian: Boolean
- language: "arabic" | "french" | "tunisian_dialect" | "mixed"
- scraped_at: ISO timestamp
```

### comments table
```
- id: PRIMARY KEY
- post_id: Foreign key to posts
- text: Comment body
- likes: Integer
- sentiment: Classification
- is_tunisian: Boolean
- hashtags_json: JSON array
```

---

## 🎯 Classification Rules

### Post Types (Priority Order)
1. **complaint** - keywords: مشكل, problème, catastrophe, غالي, kharba, hchouma
2. **opinion** - keywords: اعتقد, برأيي, je pense, mon avis
3. **news** - keywords: عاجل, breaking, خبر, officiel, annonce
4. **humor** - keywords: 😂, hhhh, lol, مضحك, tawa
5. **promotion** - keywords: solde, promo, تخفيض, discount, gratuit
6. **question** - keywords: ?, ؟, كيف, comment, why, متى
7. **event** - keywords: حفل, concert, festival, soirée
8. **general** - fallback

### Sentiment
- **positive** - keywords: برشا مليح, super, excellent, bravo, شكرا, ❤️, mabrouk
- **negative** - keywords: مشكل, كارثة, hchouma, غالي, corruption, 😡, non
- **neutral** - fallback

### Language Detection
- **tunisian_dialect** - contains dialect markers (barcha, بhiya, manich, etc.)
- **arabic** - >40% Arabic characters
- **french** - >40% Latin characters
- **mixed** - otherwise

### Tunisian Detection
Returns `True` if text contains:
- Geographic: tunisie, tunis, sfax, sousse, تونس, صفاقس
- Dialect: barcha, برشا, bch, behi, yezzi, manich
- Institutions: mosaique, shems, jawhara, attessia, tap
- Hashtags: #tunisie, #تونس, #تونسي

---

## 📊 Example Workflow

### Hackathon Demo
```bash
# 1. Run spiders once to collect data (takes 10-30 minutes)
python behaviorlens_social.py

# 2. In your demo, start the API
python behaviorlens_social.py --api

# 3. Query the dashboard
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/posts?source=facebook&sentiment=positive

# 4. Show real-time insights
# - "52 Tunisian posts collected"
# - "42% positive sentiment"
# - "Top hashtag: #tunisie (45 mentions)"
```

---

## 🔧 Configuration

Edit these at the top of `behaviorlens_social.py`:

**Target Pages**
```python
# Facebook spiders
start_urls = [
    "https://www.facebook.com/Mosaique.fm",
    # Add more pages here
]

# TikTok hashtags
start_urls = [
    "https://www.tiktok.com/tag/tunisie",
    # Add more hashtags here
]

# Instagram profiles
start_urls = [
    "https://www.instagram.com/mosaiquefm",
    # Add more profiles here
]
```

**Classification Keywords**
Add/edit keywords in the `KEYWORDS` dictionary to customize classifications.

**Scraping Limits**
```python
# Limit posts per page
posts = response.css("...")[:5]  # Change 5 to your limit

# Limit comments per post
comments = post.css("...")[:15]  # Change 15 to your limit
```

---

## ⚡ Performance Tips

1. **Session Files** - Save sessions to avoid repeated login
   ```bash
   python behaviorlens_social.py --save-session facebook
   ```

2. **Parallel Spiders** - Modify CONCURRENT_REQUESTS in SCRAPY_SETTINGS
   ```python
   'CONCURRENT_REQUESTS': 2,  # Run 2 spiders in parallel
   ```

3. **Database Queries** - Use API filters
   ```bash
   # Faster than getting all posts
   curl "http://localhost:8000/api/posts?source=facebook&limit=10"
   ```

---

## 🚨 Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
playwright install chromium
```

### "Session file not found"
- Save session first: `python behaviorlens_social.py --save-session facebook`
- Or remove session requirement from SCRAPY_SETTINGS

### "Database locked"
- Multiple instances running
- Close all Python processes and try again
- Or delete `behaviorlens.db` and start fresh

### "No posts scraped"
- Check that URLs are correct
- Verify internet connection
- Try without Playwright headless: change `'headless': False`
- Check browser logs in terminal

### "Posts being filtered"
- Spiders have TunisianFilterPipeline enabled
- To include all posts, remove from ITEM_PIPELINES
- Or modify `detect_tunisian()` function to be more lenient

---

## 📁 Output Files

- `behaviorlens.db` - SQLite database (posts + comments)
- `behaviorlens_output.jsonl` - JSON Lines format (one post per line)
- `sessions/facebook_session.json` - Saved browser session
- `sessions/tiktok_session.json` - Saved browser session
- `sessions/instagram_session.json` - Saved browser session

---

## 🎓 Hackathon Checklist

- [ ] Install dependencies
- [ ] Download Chromium browsers
- [ ] Run spiders to collect data
- [ ] Start API server
- [ ] Verify data in SQLite or API
- [ ] Create dashboard (use /api/stats)
- [ ] Demo live filtering (/api/posts?sentiment=positive)
- [ ] Show classification results
- [ ] Explain Tunisian detection logic
- [ ] Show bot detection (if integrated)

---

## 📚 Integration with Your Pipeline

### Feed to Bot Detector
```python
import sqlite3
import json

conn = sqlite3.connect("behaviorlens.db")
cursor = conn.cursor()
cursor.execute("SELECT text FROM posts WHERE is_tunisian = 1")

for row in cursor:
    post_text = row[0]
    bot_score = your_bot_detector(post_text)
    print(f"Bot score: {bot_score}")
```

### Feed to Sentiment Analyzer
```python
cursor.execute("SELECT text, sentiment FROM posts")
for post_text, existing_sentiment in cursor:
    enhanced_sentiment = your_sentiment_analyzer(post_text)
    # Compare with existing classification
```

### Feed to LLM
```python
cursor.execute("SELECT text, post_type FROM posts ORDER BY likes DESC")
for post_text, post_type in cursor:
    insights = your_llm_model(post_text)
    # Generate insights from top posts
```

---

## 📞 Support

For issues:
1. Check logs: Look at terminal output
2. Verify URLs: Are target pages still available?
3. Check internet: Can you access the URLs in browser?
4. Try specific spider: `python behaviorlens_social.py --spider facebook_tn`

---

## ⚖️ Legal Notice

- ✅ Scraping public pages is generally legal
- ✅ Respect `robots.txt` and rate limits
- ⚠️ Check platform ToS before deployment
- ⚠️ Don't scrape private content
- ⚠️ Use responsibly and ethically

---

## 🎉 Ready to Launch

You now have a **production-grade Tunisian social media intelligence system**. Use it to:

- Collect real Tunisian opinion data
- Analyze sentiment and post types
- Detect bot activity (integrate your detector)
- Generate insights with LLM
- Dashboard visualization
- Real-time monitoring

**All in one file!** 🚀

---

**Happy scraping!** 🕷️
