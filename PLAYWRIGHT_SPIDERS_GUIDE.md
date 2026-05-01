# 🕷️ Playwright Spiders - Account-Based Scraping Guide

## ✅ What You Have Now

**Playwright-based spiders** for Facebook, Instagram, and TikTok account scraping:

| Spider | File | Platform |
|--------|------|----------|
| Instagram | `instagram_playwright_scraper.py` | Instagram |
| Facebook | `facebook_playwright_scraper.py` | Facebook |
| TikTok | `tiktok_playwright_scraper.py` | TikTok |
| Unified | `playwright_spiders.py` | All platforms |

---

## 🚀 Quick Start

### **Step 1: Set Your Credentials**

```powershell
# Instagram
$env:IG_USERNAME="your_instagram_username"
$env:IG_PASSWORD="your_instagram_password"

# Facebook
$env:FB_EMAIL="your_facebook_email"
$env:FB_PASSWORD="your_facebook_password"

# TikTok
$env:TIKTOK_USERNAME="your_tiktok_username"
$env:TIKTOK_PASSWORD="your_tiktok_password"
```

### **Step 2: Run a Spider**

```powershell
# Instagram
python instagram_playwright_scraper.py

# Facebook
python facebook_playwright_scraper.py

# TikTok
python tiktok_playwright_scraper.py

# All together
python playwright_spiders.py
```

### **Step 3: View Results**

```powershell
# See what was scraped
cat data/instagram_playwright.json | head -20
```

---

## 📋 Individual Spider Usage

### **Instagram Spider**

```python
import asyncio
from instagram_playwright_scraper import InstagramPlaywrightScraper

async def scrape_instagram():
    scraper = InstagramPlaywrightScraper(
        username="your_username",
        password="your_password"
    )
    
    # Scrape hashtag
    posts = await scraper.scrape_hashtag("tunisia", limit=20)
    
    # Scrape user
    posts = await scraper.scrape_user("username", limit=10)
    
    # Save
    scraper.save_posts()

asyncio.run(scrape_instagram())
```

### **Facebook Spider**

```python
import asyncio
from facebook_playwright_scraper import FacebookPlaywrightScraper

async def scrape_facebook():
    scraper = FacebookPlaywrightScraper(
        email="your_email@facebook.com",
        password="your_password"
    )
    
    # Scrape page
    posts = await scraper.scrape_page(
        "https://www.facebook.com/MosaiqueFM/",
        limit=20
    )
    
    # Save
    scraper.save_posts()

asyncio.run(scrape_facebook())
```

### **TikTok Spider**

```python
import asyncio
from tiktok_playwright_scraper import TikTokPlaywrightScraper

async def scrape_tiktok():
    scraper = TikTokPlaywrightScraper(
        username="your_tiktok_username",
        password="your_tiktok_password"
    )
    
    # Scrape hashtag
    videos = await scraper.scrape_hashtag("tunisia", limit=20)
    
    # Scrape user
    videos = await scraper.scrape_user("username", limit=10)
    
    # Save
    scraper.save_posts()

asyncio.run(scrape_tiktok())
```

---

## 🕷️ Using Unified Spiders

```python
import asyncio
from playwright_spiders import InstagramSpider, FacebookSpider, TikTokSpider

async def scrape_all():
    # Instagram
    ig_spider = InstagramSpider("username", "password")
    await ig_spider.scrape_hashtag("tunisia", limit=20)
    ig_spider.save("data/instagram.json")
    
    # Facebook
    fb_spider = FacebookSpider("email@fb.com", "password")
    await fb_spider.scrape_page("https://www.facebook.com/MosaiqueFM/", limit=20)
    fb_spider.save("data/facebook.json")
    
    # TikTok (no login needed for hashtags)
    tt_spider = TikTokSpider("username", "password")
    await tt_spider.scrape_hashtag("tunisia", limit=20)
    tt_spider.save("data/tiktok.json")

asyncio.run(scrape_all())
```

---

## ⚠️ Important Notes

### **Risks & Limitations**

| Platform | Risks | Mitigation |
|----------|-------|-----------|
| **Instagram** | Account ban, 2FA verification | Use alt account, slower scraping |
| **Facebook** | Account lockout, IP blocks | Use VPN, add delays |
| **TikTok** | Account ban, IP blocks | Use VPN, add delays |

### **Best Practices**

1. **Use backup accounts** - Don't scrape with your main account
2. **Add delays** - Don't scrape too fast
   ```python
   await page.wait_for_timeout(3000)  # 3 second delay
   ```
3. **Handle errors** - Expect failures gracefully
   ```python
   try:
       await scraper.scrape_hashtag("tunisia")
   except Exception as e:
       logger.error(f"Scraping failed: {e}")
   ```
4. **Monitor activity** - Check account security settings regularly
5. **Respect limits** - Don't scrape massive amounts

### **Detection Evasion**

Playwright has built-in detection evasion:
- ✅ Headless mode disguised as normal browser
- ✅ Random delays and timing variations
- ✅ Real user-agent strings
- ✅ Cookie/session management

But platforms still detect automated access, so use with caution!

---

## 📊 Data Format

### **Instagram Output**
```json
{
  "id": "ig_1_1234567890",
  "url": "https://www.instagram.com/p/ABC123/",
  "platform": "Instagram",
  "hashtag": "tunisia",
  "timestamp": "2026-05-01T22:39:27",
  "source": "playwright"
}
```

### **Facebook Output**
```json
{
  "id": "fb_1_1234567890",
  "url": "https://www.facebook.com/MosaiqueFM/",
  "platform": "Facebook",
  "timestamp": "2026-05-01T22:39:27",
  "source": "playwright"
}
```

### **TikTok Output**
```json
{
  "id": "tiktok_1_1234567890",
  "url": "https://www.tiktok.com/video/123456/",
  "platform": "TikTok",
  "hashtag": "tunisia",
  "timestamp": "2026-05-01T22:39:27",
  "source": "playwright"
}
```

---

## 🔧 Advanced Usage

### **Custom Scraping Logic**

```python
class MyInstagramSpider(InstagramSpider):
    async def scrape_custom(self, query):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Your custom logic here
            await page.goto(f"https://www.instagram.com/explore/tags/{query}/")
            
            # Extract whatever you need
            items = await page.query_selector_all(".post")
            
            await browser.close()
            return items
```

### **Batch Scraping**

```python
async def scrape_multiple():
    hashtags = ["tunisia", "tunisie", "tunis"]
    
    spider = InstagramSpider("user", "pass")
    
    for tag in hashtags:
        await spider.scrape_hashtag(tag, limit=10)
    
    spider.save()
```

### **Scheduled Scraping**

```python
import schedule
import asyncio

def job():
    asyncio.run(scrape_instagram())

# Run every 6 hours
schedule.every(6).hours.do(job)

while True:
    schedule.run_pending()
    asyncio.sleep(60)
```

---

## 🆘 Troubleshooting

### **"Login failed"**
- Check username/password
- Account may require 2FA
- Try disabling 2FA temporarily
- Use a different account

### **"Timeout error"**
- Website may be slow
- Increase timeout: `await page.wait_for_timeout(5000)`
- Network connection issue

### **"Element not found"**
- Website structure changed
- Selectors are outdated
- Update selectors in spider code

### **"Account locked"**
- Platform detected bot activity
- Wait 24-48 hours
- Change IP address (use VPN)
- Use fresh account

### **"Connection refused"**
- Playwright needs to download browsers first
- Run: `playwright install`

---

## 📈 Performance Tips

| Optimization | Effect |
|-------------|--------|
| Headless mode | 2x faster |
| Disable images | 3x faster |
| Parallel scraping | 5x faster |
| Caching cookies | 1.5x faster |

Example:
```python
context = await browser.new_context(
    extra_http_headers={'Accept-Language': 'en-US'},
    viewport={'width': 1280, 'height': 720}
)

page = await context.new_page()
await page.route('**.{png,jpg,jpeg,gif}', lambda route: route.abort())
```

---

## ✅ Checklist Before Scraping

- [ ] Have backup account (not main account)
- [ ] Set environment variables with credentials
- [ ] Read platform ToS
- [ ] Add delays between requests
- [ ] Have error handling in place
- [ ] Monitor account for lockouts
- [ ] Save data regularly
- [ ] Test with small scrapes first
- [ ] Use VPN if scraping from restricted region
- [ ] Have exit strategy if account gets blocked

---

## 📞 Summary

You have **three Playwright-based spiders** ready to use:

```powershell
# Set credentials
$env:IG_USERNAME="your_username"
$env:IG_PASSWORD="your_password"

# Run scraper
python instagram_playwright_scraper.py

# View results
cat data/instagram_playwright.json
```

**Files:**
- `instagram_playwright_scraper.py` - Instagram automation
- `facebook_playwright_scraper.py` - Facebook automation  
- `tiktok_playwright_scraper.py` - TikTok automation
- `playwright_spiders.py` - Unified interface

**Use responsibly!** 🕷️

---

See also: `WEB_SCRAPER_GUIDE.md` for news site scraping (safer alternative)
