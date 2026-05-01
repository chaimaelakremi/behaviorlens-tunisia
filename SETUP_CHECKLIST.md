# InsightTN - Setup Checklist

Complete this checklist to get your system fully running. Copy & check off as you go!

## Phase 1: Verify System (5 minutes)

- [ ] Python installed: `C:/Users/aziz/.local/bin/python3.15.exe --version`
- [ ] Run: `python demo_extraction.py` (should see 5 sample posts)
- [ ] Run: `python graph_api_demo.py` (should see setup guide)
- [ ] Run: `python setup_and_status.py` (should show missing packages)

**Result:** All 3 scripts run successfully ✅

---

## Phase 2: Install Core Packages (5 minutes)

**Windows PowerShell:**
```powershell
uv pip install feedparser requests pandas python-dotenv
```

**Or run script:**
```powershell
.\install_all.ps1
```

- [ ] Install started
- [ ] Wait for completion (may take 2-3 minutes)
- [ ] Installation successful (no errors)
- [ ] Verify: `python setup_and_status.py` (should show packages installed)

**Result:** All core packages installed ✅

---

## Phase 3: Get Facebook Graph API Credentials (5 minutes)

### Step 1: Create Facebook App

- [ ] Go to: https://developers.facebook.com
- [ ] Log in with Facebook account
- [ ] Click "Create App"
- [ ] Select "Business" as app type
- [ ] Name it: "BehaviorLens Tunisia"
- [ ] Click "Create"

### Step 2: Get App ID & Secret

- [ ] Go to: Settings → Basic
- [ ] Copy "App ID" → save somewhere safe
- [ ] Copy "App Secret" → save somewhere safe

### Step 3: Generate Access Token

- [ ] Go to: Tools → Access Token Debugger
- [ ] Click "Debug Tool"
- [ ] Generate token with permissions:
  - [ ] pages_read_posts ✓
  - [ ] pages_read_engagement ✓
  - [ ] instagram_basic ✓
- [ ] Copy the token → save somewhere safe
- [ ] Token format: `abc123...` (about 200 characters)

### Step 4: Set Environment Variable

**PowerShell:**
```powershell
$env:FACEBOOK_ACCESS_TOKEN = "paste_your_token_here"
$env:FACEBOOK_APP_ID = "paste_your_app_id_here"
$env:FACEBOOK_APP_SECRET = "paste_your_app_secret_here"
```

- [ ] Environment variables set
- [ ] Verify: `echo $env:FACEBOOK_ACCESS_TOKEN` (should show token)

**Result:** Credentials configured ✅

---

## Phase 4: Configure Your Data Sources (Optional, 5 minutes)

### Add Facebook Page IDs

If you have a Facebook page you want to monitor:

1. Go to your page: https://facebook.com/yourpage
2. Copy the page ID (usually long number after `/`)
3. Edit: `social_media/config.py`
4. Find: `"graph_api_page_ids"`
5. Add your page ID:
   ```python
   "graph_api_page_ids": ["YOUR_PAGE_ID"],
   ```

- [ ] Facebook page IDs added
- [ ] Or skip (will use default pages)

### Add Instagram Account IDs

If you have an Instagram business account:

1. Get your Instagram Business Account ID
2. Edit: `social_media/config.py`
3. Find: `"graph_api_business_account_ids"`
4. Add your account ID:
   ```python
   "graph_api_business_account_ids": ["YOUR_ACCOUNT_ID"],
   ```

- [ ] Instagram account IDs added
- [ ] Or skip (will use default accounts)

**Result:** Data sources configured ✅

---

## Phase 5: Test Collection (5 minutes)

### Quick Test

Run:
```bash
python test_collection.py
```

- [ ] Test collection started
- [ ] Check for errors
- [ ] If successful: data saved to `data/extracted/`

### Full Collection

Or run:
```bash
python -m social_media.app --collect
```

- [ ] Collection started
- [ ] Monitor progress in console
- [ ] Watch for any errors
- [ ] Data saved to `data/` directory

- [ ] Collection completed successfully
- [ ] No errors in output
- [ ] Data files created

**Result:** Data collection working ✅

---

## Phase 6: View Your Data (2 minutes)

### Check What Was Collected

```bash
# See what files were created
dir data/

# View collected posts
python -c "import json; print(json.dumps(json.load(open('data/extracted/posts.json')), indent=2, ensure_ascii=False))"
```

- [ ] Data directory has files
- [ ] Can see posts in JSON files
- [ ] Posts contain author, text, sentiment, comments

**Result:** Data extraction verified ✅

---

## Phase 7: (Optional) Install Web Scraper (10 minutes)

For supplementary data collection from any website:

### Install Scrapy

**Option A: Pre-built wheels (easiest)**
```powershell
uv pip install scrapy scrapy-playwright --only-binary :all:
```

**Option B: With C++ Build Tools**
1. Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Install Visual C++ Build Tools
3. Run: `uv pip install scrapy scrapy-playwright playwright`

- [ ] Scrapy installation attempted
- [ ] Installation successful (no errors)

### Configure Scraper

Edit `social_media/config.py` to enable scraper:

```python
"scraper": {
    "enabled": True,  # Set to True
    "sites": [...],
}
```

- [ ] Scraper enabled in config
- [ ] Sites configured

### Test Hybrid Collection

```bash
python -m social_media.app --collect --mode hybrid
```

- [ ] Hybrid collection started
- [ ] Runs both Graph API and Scraper
- [ ] Data from both sources collected

**Result:** Web scraper working (optional) ✅

---

## Phase 8: Set Up Scheduling (Optional, for production)

For automatic hourly collection:

### Windows Task Scheduler

1. Open: Task Scheduler
2. Create Basic Task
3. Name: "BehaviorLens Collection"
4. Trigger: Repeat every 1 hour
5. Action: Run program
   - Program: `C:/Users/aziz/.local/bin/python3.15.exe`
   - Arguments: `c:\Users\aziz\Desktop\projects\behaviorlens-tunisia\social_media\app.py --collect`
6. Save

- [ ] Task created
- [ ] Task enabled
- [ ] Task runs at scheduled time

### Or use cron (Linux/Mac)

```bash
crontab -e
# Add: 0 * * * * cd /path/to/behaviorlens-tunisia && python -m social_media.app --collect
```

**Result:** Scheduling configured (optional) ✅

---

## Final Status Checklist

### ✅ System Ready When:

- [x] Python 3.8+ installed
- [ ] Core packages installed (feedparser, requests, pandas, python-dotenv)
- [ ] Facebook app created with Graph API access
- [ ] Access token generated with correct permissions
- [ ] Environment variables set
- [ ] Page IDs configured
- [ ] First collection run successful
- [ ] Data files created and populated
- [ ] Posts visible with sentiment analysis
- [ ] Comments extracted successfully

### 🎯 Total Setup Time: ~30 minutes

- Phase 1 (Verify): 5 min
- Phase 2 (Install): 5 min
- Phase 3 (Credentials): 5 min
- Phase 4 (Config): 5 min
- Phase 5 (Test): 5 min
- Phase 6 (Verify): 2 min

### 📊 Success Indicators

**You're done when you see:**

```
✅ Collection completed: 15 posts extracted
✅ Comments: 87 total (3-15 per post)
✅ Sentiment breakdown: 12 negative, 2 positive, 1 neutral
✅ Data saved to: data/extracted/posts.json
✅ Analysis complete: Hashtags, mentions, bot scores calculated
```

---

## 🆘 Stuck? Quick Fixes

### Can't install packages?
```powershell
# Use pre-built wheels
uv pip install --only-binary :all: feedparser requests pandas
```

### "Token not set"?
```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_from_developers.facebook.com"
echo $env:FACEBOOK_ACCESS_TOKEN  # Verify it's set
```

### "No module" error?
```powershell
python setup_and_status.py  # See exactly what's missing
```

### Graph API returns 400?
- Check token is valid
- Verify page ID is correct and public
- Ensure token has correct permissions
- Try: https://developers.facebook.com/tools/accesstoken/

### Still need help?
1. Check: [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
2. Check: [GRAPH_API_SETUP.md](GRAPH_API_SETUP.md)
3. Check: [SYSTEM_STATUS.md](SYSTEM_STATUS.md)

---

## 🎉 Congratulations!

Once you've checked everything, you're ready to:

✅ Collect real Tunisian social media data
✅ Analyze sentiment and emotions
✅ Track trending topics
✅ Monitor public opinion
✅ Detect emerging crises
✅ Export data for analysis
✅ Build dashboards and visualizations

**Your InsightTN system is production-ready!** 🚀

---

## 📝 Notes

Use this space to track your progress:

```
Started: _________________
Graph API token created: _________________
First collection run: _________________
Status: _________________
Comments: _________________
```

---

## 📞 Need Help?

- **Quick questions?** Check [QUICK_START.py](QUICK_START.py)
- **Setup problems?** Check [GRAPH_API_SETUP.md](GRAPH_API_SETUP.md)
- **System overview?** Check [SYSTEM_STATUS.md](SYSTEM_STATUS.md)
- **Complete guide?** Check [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)

**Good luck!** 🇹🇳 💪

