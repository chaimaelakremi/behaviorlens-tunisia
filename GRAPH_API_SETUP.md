# 🔑 GRAPH API SETUP - STEP BY STEP GUIDE

## ⚡ Quick Setup (5 minutes)

If you just want to get it working quickly:

```bash
# 1. Visit Facebook Developer Site
https://developers.facebook.com

# 2. Create an app (free)
# App Name: "BehaviorLens Tunisia"
# Type: Business

# 3. Get your token from here:
# Tools → Access Token Debugger

# 4. Set environment variable
export FACEBOOK_ACCESS_TOKEN="your_token_here"

# 5. Run your collector
python -m social_media.app --collect
```

**That's it!** Graph API will auto-detect the token and enable itself.

---

## 📋 Detailed Step-by-Step Setup

### STEP 1: Create Facebook Developer Account

1. Go to https://developers.facebook.com
2. Click "Get Started"
3. Fill in your details:
   - Email: Your email
   - Password: Create password
   - Account Type: Choose based on use case

**Time: 2 minutes**

### STEP 2: Create an App

1. Click "My Apps" → "Create App"
2. Choose app type: **Business**
3. Fill in details:
   - **App Name**: BehaviorLens Tunisia
   - **App Contact Email**: Your email
   - **App Purpose**: Business (Analytics)
   - **App Description**: Real-time social media analytics

4. Click "Create App"

**Time: 2 minutes**

### STEP 3: Add Required Products

Inside your app dashboard:

1. Find "Products" section
2. Add **Facebook Graph API**:
   - Click "Graph API"
   - Click "Get Started"
   - Choose your use case

3. Add **Instagram Graph API**:
   - Click "Instagram"
   - Follow setup wizard

**Time: 2 minutes**

### STEP 4: Get App Credentials

From App Dashboard, find:

1. **App ID**
   - Copy from top of page or Settings → Basic
   - Example: `1234567890123456`

2. **App Secret**
   - Settings → Basic
   - Click "Show"
   - Copy the secret
   - Example: `abc123def456ghi789`

**Keep these safe!** Don't share with anyone.

### STEP 5: Generate Access Token

Method A: Quick Token (Testing)
1. Go to Tools → Access Token Debugger
2. Select your app
3. "Get Token"
4. Choose "Get User Access Token"
5. Permissions you need:
   - ✅ pages_read_posts
   - ✅ pages_read_engagement
   - ✅ instagram_basic
6. Click "Generate Token"
7. Copy the token

**Duration**: 1-2 hours (good for testing)

Method B: Long-lived Token (Production)
1. Use the user access token from Method A
2. Visit: `https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=SHORT_LIVED_TOKEN`
3. Replace:
   - `YOUR_APP_ID` with your App ID
   - `YOUR_APP_SECRET` with your App Secret
   - `SHORT_LIVED_TOKEN` with the short-lived token
4. Copy the long-lived token (valid 60 days)

**Time: 3 minutes**

### STEP 6: Find Your Page/Account IDs

#### For Facebook Pages:

1. Go to your Facebook Page
2. Look at URL: `facebook.com/YOUR_PAGE_NAME`
3. Go to About section
4. Scroll down to find "Page ID"

Or programmatically:

```bash
curl "https://graph.facebook.com/me/accounts?access_token=YOUR_TOKEN"
```

This returns all your pages with their IDs.

#### For Instagram Business Account:

1. Go to your Instagram Profile
2. Settings → Account
3. Look for "Instagram Business Account ID"

Or programmatically:

```bash
# Get your Instagram Business Account ID
curl "https://graph.facebook.com/me/instagram_business_account?access_token=YOUR_TOKEN"
```

**Time: 2 minutes**

### STEP 7: Store Credentials Securely

Option A: Environment Variables (Recommended)

```bash
# Linux/Mac
export FACEBOOK_ACCESS_TOKEN="your_token_here"
export FACEBOOK_APP_ID="your_app_id"
export FACEBOOK_APP_SECRET="your_app_secret"

# Windows PowerShell
$env:FACEBOOK_ACCESS_TOKEN="your_token_here"
$env:FACEBOOK_APP_ID="your_app_id"
$env:FACEBOOK_APP_SECRET="your_app_secret"

# Windows Command Prompt
set FACEBOOK_ACCESS_TOKEN=your_token_here
```

Option B: Configuration File

Create `.env` file in your project:

```
FACEBOOK_ACCESS_TOKEN=your_token_here
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
```

Then load it:

```python
import os
from dotenv import load_dotenv
load_dotenv()
```

**Time: 1 minute**

### STEP 8: Configure Your System

Edit `social-media/config.py`:

```python
"facebook_graph_api": {
    "enabled": True,  # CHANGE THIS
    "graph_api_page_ids": [
        "YOUR_PAGE_ID_1",  # Add your page ID
        "YOUR_PAGE_ID_2",  # Add more if you want
    ],
    "include_comments": True,
    "post_limit": 50,
},

"instagram_graph_api": {
    "enabled": True,  # CHANGE THIS
    "graph_api_business_account_ids": [
        "YOUR_ACCOUNT_ID_1",  # Add your Business Account ID
    ],
    "include_comments": True,
    "post_limit": 40,
},
```

**Time: 2 minutes**

### STEP 9: Test Your Setup

```python
from social_media.graph_api_collector import FacebookInstagramGraphAPICollector

# Test if credentials work
collector = FacebookInstagramGraphAPICollector()

if collector.enabled:
    print("✓ Credentials valid!")
    print("✓ Graph API enabled")
else:
    print("✗ Credentials missing")
    print("Set FACEBOOK_ACCESS_TOKEN environment variable")

# Try collecting a single post
if collector.enabled:
    posts = collector.get_facebook_posts("YOUR_PAGE_ID", limit=1)
    print(f"✓ Collected {len(posts)} posts")
```

**Time: 2 minutes**

### STEP 10: Run Your Collector

```bash
# Now your system will use Graph API automatically
python -m social_media.app --collect

# Or run full pipeline
python -m social_media
```

**Total Time: ~20 minutes for complete setup**

---

## 🔧 Advanced Configuration

### Collect from Multiple Pages

```python
"facebook_graph_api": {
    "enabled": True,
    "graph_api_page_ids": [
        "1234567890",  # BBC Tunisia
        "0987654321",  # Reuters Tunisia
        "1111111111",  # France24 Tunisia
    ],
    "post_limit": 100,  # Collect more posts per page
},
```

### Custom Collection Logic

```python
from social_media.graph_api_collector import FacebookInstagramGraphAPICollector
import os

# Create collector with your credentials
collector = FacebookInstagramGraphAPICollector(
    access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
    page_ids=["123456789"],
    instagram_business_account_ids=["987654321"]
)

# Collect with options
fb_posts = collector.get_facebook_posts(
    page_id="123456789",
    limit=100,
    include_comments=True
)

ig_posts = collector.get_instagram_posts(
    business_account_id="987654321",
    limit=50,
    include_comments=True
)

# Process posts
all_posts = fb_posts + ig_posts

# Filter by engagement
high_engagement = [
    p for p in all_posts
    if p['engagement']['likes'] > 100
]

print(f"Found {len(high_engagement)} highly engaged posts")
```

---

## 🐛 Troubleshooting

### Problem: "No credentials found"

**Solution:**
```bash
# Check if token is set
echo $FACEBOOK_ACCESS_TOKEN

# If empty, set it
export FACEBOOK_ACCESS_TOKEN="your_token"

# Verify it's set
echo $FACEBOOK_ACCESS_TOKEN  # Should show your token
```

### Problem: "Invalid access token"

**Solution:**
1. Token expired → Generate new one
2. Permissions missing → Add required permissions
3. Token is for wrong app → Use correct token
4. Token revoked → Generate new one

```bash
# To check token validity:
curl "https://graph.facebook.com/debug_token?input_token=YOUR_TOKEN&access_token=YOUR_TOKEN"
```

### Problem: "Page ID not found"

**Solution:**
```bash
# List all your pages
curl "https://graph.facebook.com/me/accounts?access_token=YOUR_TOKEN"

# Copy the correct ID from the response
```

### Problem: "Permission denied"

**Solution:**
1. Check token has these permissions:
   - pages_read_posts
   - pages_read_engagement
   - instagram_basic

2. If missing, generate new token with permissions

### Problem: "Rate limit exceeded"

**Solution:**
1. Upgrade to higher tier
2. Implement request backoff:

```python
import time

for page_id in page_ids:
    posts = collector.get_facebook_posts(page_id)
    time.sleep(1)  # Wait 1 second between requests
```

---

## ✅ Verification Checklist

Before running production collection:

- [ ] Created Facebook app
- [ ] Generated access token
- [ ] Token has required permissions
- [ ] Found your page ID(s)
- [ ] Found your Instagram Business Account ID(s)
- [ ] Set FACEBOOK_ACCESS_TOKEN environment variable
- [ ] Updated config.py with IDs
- [ ] Tested with 1 post first
- [ ] Successfully collected posts with comments
- [ ] Timestamps and engagement metrics look correct

---

## 🚀 Running Collection with Graph API

### Option 1: Full Collection (RSS + Graph API)

```bash
python -m social_media.app --collect
# Collects from all sources: RSS, Graph API, etc.
```

### Option 2: Show Statistics

```bash
python -m social_media.app --stats
# Shows breakdown by platform, sentiment, language
```

### Option 3: Export Data

```bash
python -m social_media.app --export csv
# Exports to posts.csv
```

### Option 4: Run Examples

```bash
python -m social_media.examples 1
# Runs example 1: Basic collection
```

---

## 📊 Expected Output

When Graph API is enabled and working:

```
Starting collection from all social media sources
├─ Collecting from twitter_rss...
│  ✓ Collected 50 posts from twitter_rss
├─ Collecting from facebook_pages...
│  ✓ Collected 30 posts from facebook_pages
├─ Collecting from facebook_graph_api...
│  ✓ Collected 45 posts from facebook_graph_api    ← Graph API!
├─ Collecting from instagram_hashtags...
│  ✓ Collected 32 posts from instagram_hashtags
├─ Collecting from instagram_graph_api...
│  ✓ Collected 38 posts from instagram_graph_api   ← Graph API!
└─ Collecting from reddit_communities...
   ✓ Collected 40 posts from reddit_communities

Total posts collected: 235

STATISTICS:
By Platform:
  - twitter_rss: 50
  - facebook_pages: 30
  - facebook_graph_api: 45        ← 45 with comments!
  - instagram_hashtags: 32
  - instagram_graph_api: 38       ← 38 with comments!
  - reddit_communities: 40

By Sentiment:
  - negative: 142
  - neutral: 56
  - positive: 37

By Language:
  - en: 95
  - ar: 87
  - mix: 45
  - fr: 8
```

---

## 🎯 Next Steps

### After Graph API is Working

1. **Collect more data**
   - Increase `post_limit` for more posts per collection
   - Add more page IDs to config

2. **Store for analysis**
   - Posts automatically saved to `data/processed/posts.json`
   - Export to CSV for ML training

3. **Feed into next layer**
   - Pass posts to bot detection
   - Send to NLP analysis
   - Create visualizations

4. **Monitor real-time**
   - Set up scheduled collections
   - Track sentiment trends
   - Create alerts for spikes

---

## 📞 Support

If you get stuck:

1. **Check logs**:
   ```bash
   tail -f data/logs/social_media.log
   ```

2. **Test token**:
   ```bash
   curl "https://graph.facebook.com/me?access_token=YOUR_TOKEN"
   ```

3. **Debug app**:
   ```python
   from social_media.graph_api_collector import FacebookInstagramGraphAPICollector
   collector = FacebookInstagramGraphAPICollector()
   print(f"Enabled: {collector.enabled}")
   print(f"Token: {collector.access_token[:20]}...")
   ```

4. **Official docs**: https://developers.facebook.com/docs/graph-api

---

## 🎉 You're Done!

Your system now has:

✅ **RSS feeds** - No authentication needed
✅ **Graph API** - Official, complete data
✅ **Real-time** - Live sentiment analysis
✅ **Comments** - Full comment threads
✅ **Scalable** - Easy to add more sources

**Ready to build intelligence on Tunisian sentiment!** 🚀

