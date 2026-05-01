# 📱 Facebook & Instagram Collection - Best Methods

## ✅ The Truth About Unofficial Libraries

**Instagrapi and similar libraries:**
- ❌ Instagram actively blocks them
- ❌ Your account can get banned
- ❌ Compatibility issues (like we just saw)
- ❌ Violates Terms of Service
- ❌ No official support

**Official Graph API:**
- ✅ Legal and supported
- ✅ No account risk
- ✅ Official rate limits
- ✅ Better data quality
- ✅ Takes 5 minutes to setup

---

## 🚀 The Easy Way: Official Graph API

### **Method 1: Facebook Business Pages (Free)**

**Step 1: Create Meta App (2 minutes)**
```
1. Go to: https://developers.facebook.com
2. Click: My Apps → Create App
3. Choose: Business
4. Name it: "BehaviorLens" (or any name)
```

**Step 2: Get Access Token (2 minutes)**
```
1. Settings → Basic (copy App ID)
2. Tools → Access Token Debugger
3. Generate token with permissions:
   ✓ pages_read_posts
   ✓ pages_read_engagement
   ✓ instagram_basic
```

**Step 3: Collect Data (1 minute)**
```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_here"
python graph_api_demo.py

# You get: Facebook posts + Instagram content + Comments
# All real data, no account ban risk!
```

### **Permissions You Can Get:**
- `pages_read_posts` - Read posts from pages
- `pages_read_engagement` - Like counts, comments
- `instagram_basic` - Instagram media
- `instagram_manage_insights` - Analytics

---

## 📊 Comparison: Official vs Unofficial

| Feature | Official API | Instagrapi | Browser |
|---------|--------------|-----------|---------|
| **Legal** | ✅ Yes | ❌ No | ❌ No |
| **Account Risk** | ✅ None | ❌ Ban Risk | ❌ Ban Risk |
| **Setup Time** | ⚡ 5 min | ⚡ 5 min | ⚡ 5 min |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Rate Limits** | 200 req/hr | 100 req/hr | 10 req/hr |
| **Support** | ✅ Official | ❌ None | ❌ None |
| **Data Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |

---

## 🎯 Quick Start with Official API

### **Copy-Paste These Commands:**

```powershell
# 1. Create FREE developer account
# Go to: https://developers.facebook.com
# Follow Step 1 and 2 above

# 2. Set your token (replace YOUR_TOKEN)
$env:FACEBOOK_ACCESS_TOKEN = "YOUR_TOKEN_HERE"

# 3. Run the demo
python graph_api_demo.py

# You'll see:
# ✓ How to get real data
# ✓ Sample data format
# ✓ Next steps
```

---

## 📝 What You Can Collect with Official API

### **From Facebook Pages:**
```json
{
  "posts": [
    {
      "text": "Breaking news...",
      "author": "Page Name",
      "engagement": {
        "likes": 1234,
        "comments": 87,
        "shares": 45
      },
      "comments": [
        {"author": "User", "text": "...", "sentiment": "..."}
      ]
    }
  ]
}
```

### **From Instagram Business Accounts:**
```json
{
  "media": [
    {
      "caption": "Photo caption...",
      "likes": 5678,
      "comments": 234,
      "hashtags": ["#tunisia", "#news"]
    }
  ]
}
```

---

## 🔐 How to Get Your Token (Step-by-Step)

### **Step 1: Create Meta Developer Account**
1. Visit: https://developers.facebook.com
2. Click: Sign Up (top right)
3. Enter your email
4. Verify (check your email)
5. Create account

### **Step 2: Create an App**
1. Click: My Apps (left menu)
2. Click: Create App
3. Choose: Business
4. Fill in:
   - App Name: "BehaviorLens Tunisia"
   - App Purpose: "Manage social media"
5. Click: Create App

### **Step 3: Get Access Token**
1. In your app, go to: Tools → Access Token Debugger
2. Click: Get Token
3. Select permissions:
   - ✓ pages_read_posts
   - ✓ pages_read_engagement
   - ✓ instagram_basic
4. Click: Generate Token
5. Copy the token (it's long)

### **Step 4: Use in Your Code**
```powershell
# Save token as environment variable
$env:FACEBOOK_ACCESS_TOKEN = "paste_your_token_here"

# Then run any collection script:
python graph_api_demo.py
```

---

## 💡 Why Official API is Better

✅ **Legal**
- Complies with ToS
- No risk of account ban
- Official support from Meta

✅ **Reliable**
- Works consistently
- Official rate limits
- Historical data available

✅ **Easy Setup**
- Takes 5 minutes
- Just copy-paste your token
- No complex configuration

✅ **Better Data**
- More complete information
- Comment threads included
- Engagement metrics accurate

✅ **Free**
- No costs
- High rate limits (200 requests/hour)
- Unlimited data access

---

## 📊 Alternatives if You Really Want Account-Based

If you absolutely need account-based scraping:

### **Option 1: Professional Services**
- **Apify.com** - Cloud scraper ($), good for Instagram
- **ScraperAPI.com** - Proxy service ($), avoids blocks
- **Bright Data** - Enterprise solution

### **Option 2: Browser Automation**
- Selenium + Firefox
- Playwright + Chromium
- But: Slow, unreliable, can get blocked

### **Option 3: Academic Research**
- If you're a researcher, apply for:
  - Twitter Academic Research (free)
  - Facebook Research programs
  - Better data access

---

## 🎓 My Recommendation

**Do this now (5 minutes):**

1. Go to: https://developers.facebook.com
2. Create free app
3. Get access token
4. Run:
   ```powershell
   python graph_api_demo.py
   ```

**Why?**
- Fastest to setup
- Safest for your accounts
- Best data quality
- Zero risk
- Actually easier than unofficial libraries!

---

## 📞 Summary

| Need | Solution |
|------|----------|
| News sites | `python simple_web_scraper.py` ✅ |
| Reddit | `python social_media_scraper.py` ✅ |
| Facebook/Instagram | `python graph_api_demo.py` (5 min setup) ✅ |
| Twitter | Get API key from Twitter (free) ✅ |
| Other social media | Use third-party services |

**Start here:** [graph_api_demo.py](graph_api_demo.py)

Good luck! 🚀
