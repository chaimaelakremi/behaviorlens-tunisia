# Quick Commands - Scrapy & Playwright Installation

Copy and paste these commands in order. They're ready to use!

---

## 📋 Prerequisites

### Step 1: Download C++ Build Tools
```
URL: https://aka.ms/vs/17/release/vs_BuildTools.exe
```

Then:
1. Right-click the downloaded file
2. Select "Run as Administrator"
3. Check "Desktop development with C++"
4. Click Install
5. Wait 10-15 minutes
6. **Restart computer if prompted**

---

## 🐍 Python Package Installation

### Step 2: Install Scrapy

Open PowerShell and run:
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy
```

**Wait 2-5 minutes** for completion.

---

### Step 3: Install Scrapy-Playwright

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy-playwright
```

**Wait 1-2 minutes** for completion.

---

### Step 4: Install Playwright

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install playwright
```

**Wait 1-2 minutes** for completion.

---

## ✅ Verification Commands

### Verify All Packages Installed

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy, playwright; print('✅ Scrapy:', scrapy.__version__); print('✅ Playwright installed')"
```

**Expected output:**
```
✅ Scrapy: 2.x.x
✅ Playwright installed
```

---

### Check System Status

```powershell
C:/Users/aziz/.local/bin/python3.15.exe setup_and_status.py
```

This will show all installed packages.

---

## 🕷️ Scrapy Commands

### List Available Spiders

```powershell
cd social_media
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy list
```

---

### Create New Spider

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy genspider mytarget example.com
```

---

### Test Spider (Dry Run)

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy crawl myspider --dry-run
```

---

### Run Spider

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy crawl myspider -o output.json
```

---

## 📊 InsightTN Commands

### Collect with Graph API Only

```powershell
python -m social_media.app --collect --mode graph_api
```

---

### Collect with Scrapy Only

```powershell
python -m social_media.app --collect --mode scrapy
```

---

### Collect with Hybrid (Graph API + Scrapy)

```powershell
python -m social_media.app --collect --mode hybrid
```

---

### Collect with Fallback (Try API, use Scraper if needed)

```powershell
python -m social_media.app --collect --mode fallback
```

---

### Interactive Menu

```powershell
python -m social_media.app
```

---

## 📁 File Operations

### Create Spider Directory

```powershell
mkdir social_media\spiders
```

---

### Check Data Directory

```powershell
dir data\
```

---

### View Latest JSON Results

```powershell
cat data\extracted\posts.json
```

---

### Count Posts in JSON

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "import json; posts = json.load(open('data/extracted/posts.json')); print(f'Total posts: {len(posts)}')"
```

---

### Check Data Sources

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "import json; posts = json.load(open('data/extracted/posts.json')); sources = set(p['source'] for p in posts); print(f'Sources: {sources}')"
```

---

## 🔧 Configuration Commands

### Set Graph API Token

```powershell
$env:FACEBOOK_ACCESS_TOKEN = "your_token_here_paste_between_quotes"
```

Then verify:
```powershell
echo $env:FACEBOOK_ACCESS_TOKEN
```

---

### Create .env File

Create file: `.env` in project root

Add:
```
FACEBOOK_ACCESS_TOKEN=your_token_here
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
```

---

## 🧪 Testing Commands

### Test Python Import

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy; print('Scrapy imported successfully')"
```

---

### Test Playwright

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "from playwright.sync_api import sync_playwright; print('Playwright imported successfully')"
```

---

### Test Full Collection Pipeline

```powershell
python test_collection.py
```

---

### Run Demo

```powershell
python demo_extraction.py
```

---

## 📊 Debugging Commands

### View Python Version

```powershell
C:/Users/aziz/.local/bin/python3.15.exe --version
```

---

### List All Installed Packages

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip list
```

---

### Check If Scrapy is Installed

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip show scrapy
```

---

### Uninstall & Reinstall Scrapy

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip uninstall scrapy -y
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy
```

---

### View Collection Logs

```powershell
tail -f data\logs\collection.log
```

---

## 🚀 Complete Installation Sequence (Copy & Run)

Paste this entire sequence into PowerShell to install everything:

```powershell
# Navigate to project
cd C:\Users\aziz\Desktop\projects\behaviorlens-tunisia

# Install Scrapy
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy

# Install Scrapy-Playwright
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy-playwright

# Install Playwright
C:/Users/aziz/.local/bin/python3.15.exe -m pip install playwright

# Verify installation
C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy, playwright; print('✅ All packages installed'); print('Scrapy:', scrapy.__version__)"
```

---

## 📝 Workflow: From Install to Collection

```powershell
# 1. Install (done above)
# 2. Set token
$env:FACEBOOK_ACCESS_TOKEN = "your_token"

# 3. Test with demo
python demo_extraction.py

# 4. Test with Graph API
python -m social_media.app --collect --mode graph_api

# 5. Test with Scrapy
python -m social_media.app --collect --mode scrapy

# 6. Hybrid mode
python -m social_media.app --collect --mode hybrid

# 7. View results
cat data\extracted\posts.json

# 8. Check statistics
C:/Users/aziz/.local/bin/python3.15.exe setup_and_status.py
```

---

## ⚠️ Common Issues & Fixes

### "Module not found" error
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install --upgrade scrapy
```

---

### "C++ compiler required"
- Download and run C++ Build Tools from: https://aka.ms/vs/17/release/vs_BuildTools.exe
- Restart computer
- Run pip install again

---

### "Permission denied"
```powershell
# Don't use Admin PowerShell
# Use regular PowerShell instead
# Close and reopen PowerShell (not Admin)
```

---

### "Playwright browser not found"
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m playwright install
```

---

## 📞 Need Help?

- **Full Guide:** Read `SCRAPY_PLAYWRIGHT_COMPLETE_GUIDE.md`
- **Checklist:** Follow `SCRAPY_INSTALLATION_CHECKLIST.md`
- **Status:** Run `python setup_and_status.py`
- **Demo:** Run `python demo_extraction.py`

---

**Ready? Start with the C++ Build Tools download above!** 🚀

