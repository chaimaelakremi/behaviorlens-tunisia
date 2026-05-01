# Complete Guide: Install & Configure Scrapy + Playwright

## 📋 Table of Contents
1. Prerequisites (C++ Build Tools)
2. Install Scrapy & Playwright
3. Configure for InsightTN
4. Test Installation
5. Hybrid Mode Setup

---

## PART 1: Install C++ Build Tools (Prerequisites)

**Required because:** Scrapy needs cffi which needs C++ compiler

### Step 1.1: Download Visual Studio Build Tools

**Option A: Direct Link (Recommended)**
- URL: https://aka.ms/vs/17/release/vs_BuildTools.exe
- Size: ~1.5GB
- Save to: `C:\Users\aziz\Downloads\vs_BuildTools.exe`

**Option B: Via Website**
1. Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Click blue "Download" button
3. Wait for download

### Step 1.2: Run Installer as Administrator

1. **Right-click** `vs_BuildTools.exe`
2. Select **"Run as Administrator"**
3. Wait for installer to load (1-2 minutes)

### Step 1.3: Select Components

In the installer window:
1. Check: **"Desktop development with C++"**
2. Also check: 
   - ✓ MSVC v143 (latest C++ compiler)
   - ✓ Windows 10/11 SDK
   - ✓ CMake tools for Windows
3. Click **"Install"** (bottom right)
4. **Wait 10-15 minutes** for installation

### Step 1.4: Restart (if prompted)

- If asked to restart, restart your computer
- If not asked, you're done with C++ tools

---

## PART 2: Install Scrapy & Playwright

### Step 2.1: Open PowerShell (Regular, not Admin)

```powershell
# Navigate to project
cd C:\Users\aziz\Desktop\projects\behaviorlens-tunisia
```

### Step 2.2: Install Scrapy

**Try with pre-built wheels first (fastest):**
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy --only-binary :all:
```

**If that fails, try without wheel restriction:**
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy
```

**Expected time:** 2-5 minutes
**Output should end with:** `Successfully installed scrapy-2.x.x`

### Step 2.3: Install Scrapy-Playwright

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy-playwright
```

**Expected time:** 1-2 minutes

### Step 2.4: Install Playwright

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install playwright
```

**Expected time:** 1-2 minutes

### Step 2.5: Verify Installation

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy, playwright; print('✅ Scrapy:', scrapy.__version__); print('✅ Playwright installed')"
```

**Expected output:**
```
✅ Scrapy: 2.x.x
✅ Playwright installed
```

---

## PART 3: Configure Scrapy for InsightTN

### Step 3.1: Create Scrapy Project Structure

If you want to use Scrapy scraper, create this structure:

```powershell
# Create spider directory
mkdir social_media\spiders
```

### Step 3.2: Create Settings File

Create: `social_media\scrapy_settings.py`

```python
# Scrapy settings for InsightTN

BOT_NAME = 'behaviorlens'

SPIDER_MODULES = ['social_media.spiders']
NEWSPIDER_MODULE = 'social_media.spiders'

# Obey robots.txt
ROBOTSTXT_OBEY = True

# Download delay
DOWNLOAD_DELAY = 2

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Middleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_playwright.downloadermiddleware.ScrapyPlaywrightDownloaderMiddleware': 585,
}

# Playwright settings
PLAYWRIGHT_BROWSER_TYPE = 'chromium'
PLAYWRIGHT_LAUNCH_ARGS = {
    'headless': True,
}

# Pipelines
ITEM_PIPELINES = {
    'social_media.pipelines.DuplicatePipeline': 100,
    'social_media.pipelines.SentimentPipeline': 200,
    'social_media.pipelines.StoragePipeline': 300,
}

# Logging
LOG_LEVEL = 'INFO'
```

### Step 3.3: Create Example Spider

Create: `social_media\spiders\instagram_spider.py`

```python
import scrapy
from scrapy_playwright.page import PageMethod

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    
    def __init__(self, profile='*', *args, **kwargs):
        self.profile = profile
        self.start_urls = [f'https://www.instagram.com/{profile}']
        super().__init__(*args, **kwargs)
    
    meta = {
        'playwright': True,
        'playwright_include_page': True,
        'playwright_context_args': {
            'ignore_https_errors': True,
        },
    }
    
    async def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta=self.meta,
            )
    
    async def parse(self, response):
        self.logger.info(f'Scraping {response.url}')
        
        # Extract posts
        posts = response.css('article')
        for post in posts:
            yield {
                'url': response.url,
                'title': post.css('h1::text').get(),
                'content': post.css('div::text').getall(),
            }
```

Create: `social_media\spiders\facebook_spider.py`

```python
import scrapy
from scrapy_playwright.page import PageMethod

class FacebookSpider(scrapy.Spider):
    name = 'facebook'
    
    def __init__(self, page='*', *args, **kwargs):
        self.page = page
        self.start_urls = [f'https://www.facebook.com/{page}']
        super().__init__(*args, **kwargs)
    
    meta = {
        'playwright': True,
        'playwright_include_page': True,
    }
    
    async def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta=self.meta,
            )
    
    async def parse(self, response):
        # Extract posts and comments
        posts = response.css('[data-testid="feed_story_container"]')
        for post in posts:
            yield {
                'author': post.css('[data-testid="actor_name"]::text').get(),
                'content': post.css('[data-testid="post_message"]::text').get(),
                'likes': post.css('[aria-label*="people reacted"]::text').get(),
            }
```

---

## PART 4: Test Installation

### Test 4.1: Verify Imports

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -c "from scrapy import Spider; from scrapy_playwright.page import PageMethod; print('✅ All imports working')"
```

### Test 4.2: List Available Spiders

```powershell
cd social_media
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy list
```

**Expected output:**
```
facebook
instagram
```

### Test 4.3: Test Instagram Spider (Dry Run)

```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy crawl instagram -a profile=instagram --dry-run
```

### Test 4.4: Create Scrapy Project (Optional)

If you want full Scrapy project structure:

```powershell
cd ..
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy startproject behaviorlens_scrapy
```

---

## PART 5: Integrate with InsightTN

### Step 5.1: Update config.py

Edit: `social_media/config.py`

Add Scrapy configuration:

```python
SCRAPY_CONFIG = {
    "enabled": True,
    "settings_module": "social_media.scrapy_settings",
    "spiders": {
        "facebook": {
            "enabled": True,
            "pages": ["Mosaique", "TAP_Tunisia"],
            "limit": 10
        },
        "instagram": {
            "enabled": True,
            "profiles": ["tunisienumerique", "tunisia"],
            "limit": 10
        }
    }
}
```

### Step 5.2: Create Scrapy Collector

Create: `social_media/scrapy_collector.py`

```python
"""
Scrapy-based web scraper integration for InsightTN
"""
import asyncio
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from social_media.config import SOCIAL_MEDIA_CONFIG

class ScrapyCollector:
    def __init__(self):
        self.settings = get_project_settings()
        self.process = None
    
    def collect_instagram(self, profile, limit=10):
        """Collect posts from Instagram profile"""
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 2,
        })
        
        from social_media.spiders.instagram_spider import InstagramSpider
        process.crawl(InstagramSpider, profile=profile)
        process.start()
    
    def collect_facebook(self, page, limit=10):
        """Collect posts from Facebook page"""
        process = CrawlerProcess({
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 2,
        })
        
        from social_media.spiders.facebook_spider import FacebookSpider
        process.crawl(FacebookSpider, page=page)
        process.start()
    
    def collect_all(self):
        """Collect from all configured sources"""
        config = SOCIAL_MEDIA_CONFIG.get('scrapy', {})
        
        if not config.get('enabled'):
            print("Scrapy disabled in config")
            return []
        
        posts = []
        
        # Instagram
        for profile in config.get('spiders', {}).get('instagram', {}).get('profiles', []):
            print(f"Collecting from Instagram: {profile}")
            posts.extend(self.collect_instagram(profile))
        
        # Facebook
        for page in config.get('spiders', {}).get('facebook', {}).get('pages', []):
            print(f"Collecting from Facebook: {page}")
            posts.extend(self.collect_facebook(page))
        
        return posts

if __name__ == "__main__":
    collector = ScrapyCollector()
    collector.collect_all()
```

### Step 5.3: Update app.py

Add to `social_media/app.py`:

```python
from social_media.scrapy_collector import ScrapyCollector

# In SocialMediaCollector class:
def collect_with_scrapy(self):
    """Collect data using Scrapy web scraper"""
    scraper = ScrapyCollector()
    posts = scraper.collect_all()
    
    # Normalize posts
    normalized = self._normalize_posts(posts, 'scraper')
    return normalized

# Add to menu:
elif choice == 4:
    print("\n🕷️  Starting Scrapy collection...")
    posts = self.collect_with_scrapy()
    print(f"✅ Collected {len(posts)} posts via Scrapy")
    print(f"Saved to: data/extracted/scraper_posts.json")
```

---

## PART 6: Use in Hybrid Mode

### Command to Collect with Both APIs & Scraper

```powershell
# Graph API only
python -m social_media.app --collect --mode graph_api

# Scrapy only
python -m social_media.app --collect --mode scrapy

# Hybrid (Graph API + Scrapy)
python -m social_media.app --collect --mode hybrid

# With fallback
python -m social_media.app --collect --mode fallback
```

---

## PART 7: Troubleshooting

### "cffi wheel not available"
**Solution:** Install C++ Build Tools (Part 1)

### "Playwright not found"
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install --upgrade playwright
```

### "Spider not found"
**Check:** Spiders are in `social_media/spiders/` directory

### "Can't build cffi"
**Try:** Use pre-built wheels
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy --only-binary :all:
```

### "ModuleNotFoundError: no module named 'scrapy'"
```powershell
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy scrapy-playwright
```

---

## PART 8: Quick Reference Commands

```powershell
# Install all
C:/Users/aziz/.local/bin/python3.15.exe -m pip install scrapy scrapy-playwright playwright

# Verify
C:/Users/aziz/.local/bin/python3.15.exe -c "import scrapy; print(scrapy.__version__)"

# List spiders
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy list

# Test spider
C:/Users/aziz/.local/bin/python3.15.exe -m scrapy crawl instagram -a profile=test

# Run collection
python -m social_media.app --collect --mode hybrid

# Check logs
tail -f logs/collection.log
```

---

## Summary

**Total Time Required:**
- C++ Build Tools: 15-20 minutes
- Scrapy installation: 5 minutes
- Configuration: 10 minutes
- **Total: ~30-35 minutes**

**After completion, you'll have:**
✅ Scrapy web scraping framework
✅ Playwright browser automation
✅ Instagram spider
✅ Facebook spider
✅ Hybrid collection mode
✅ Full integration with InsightTN

---

**Ready to proceed? Start with Part 1!** 🚀

