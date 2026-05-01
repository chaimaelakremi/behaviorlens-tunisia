# Scrapy settings for facebook_scraper project

BOT_NAME = 'facebook_scraper'

SPIDER_MODULES = ['facebook_scraper.spiders']
NEWSPIDER_MODULE = 'facebook_scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # Facebook blocks robots, so we ignore

# Configure maximum concurrent requests made by Scrapy (default: 16)
CONCURRENT_REQUESTS = 2

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 3

# The average number of requests Scrapy should be sending in parallel to
# each remote server
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Enable Playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright options
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "args": ["--disable-blink-features=AutomationControlled"],
}

PLAYWRIGHT_CONTEXT_KWARGS = {
    "user_agent": USER_AGENT,
    "ignore_https_errors": True,
}

# Output format
FEEDS = {
    "data/facebook_comments.json": {
        "format": "json",
        "encoding": "utf-8",
        "indent": 2,
    },
}

# Log level
LOG_LEVEL = 'INFO'

# Allow redirects
REDIRECT_ENABLED = True

# Disable cookies (Facebook tracks this)
COOKIES_ENABLED = False
