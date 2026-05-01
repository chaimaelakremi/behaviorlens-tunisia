#!/usr/bin/env python3
"""
InsightTN Quick Start Reference
================================

Run this file to see what's ready to go!
"""

import os
import sys
from pathlib import Path

def print_section(title, content):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")
    print(content)

def main():
    print("\n" + "🚀 " * 10)
    print("  InsightTN System - Quick Start Guide")
    print("🚀 " * 10)
    
    # Section 1: What's Ready
    print_section(
        "✅ READY TO RUN NOW (No Installation Needed)",
        """1. See Demo Data:
   python demo_extraction.py
   → Creates realistic Tunisian social media posts with comments
   
2. See Graph API Setup Guide:
   python graph_api_demo.py
   → Shows how to get credentials and what data looks like
   
3. Check System Status:
   python setup_and_status.py
   → Shows what's installed and what's missing
"""
    )
    
    # Section 2: Installation
    print_section(
        "📦 INSTALLATION (5 minutes)",
        """Install Core Packages (for Graph API - Official APIs):
   
   PowerShell:
   uv pip install feedparser requests pandas python-dotenv
   
   Or run script:
   .\install_all.ps1

After installation, all collection features will work!
"""
    )
    
    # Section 3: Get Credentials
    print_section(
        "🔑 GET FACEBOOK CREDENTIALS (5 minutes)",
        """1. Go to: https://developers.facebook.com
2. Click "Create App" → Select "Business"
3. Go to "Tools" → "Access Token Debugger"
4. Generate token with permissions:
   - pages_read_posts
   - pages_read_engagement
   - instagram_basic
5. Copy token

6. Set Environment Variable (PowerShell):
   $env:FACEBOOK_ACCESS_TOKEN = "your_token_here"

7. Optional: Add your page ID to social_media/config.py:
   "graph_api_page_ids": ["YOUR_PAGE_ID"]
"""
    )
    
    # Section 4: Collect Data
    print_section(
        "📊 COLLECT DATA (After steps above)",
        """Run:
   python -m social_media.app --collect

Or test first:
   python test_collection.py

You'll get posts like:
   {
     "author": "Mosaique FM",
     "text": "خبر عاجل...",
     "sentiment": "negative",
     "comments": [
       {"author": "Ahmed", "text": "...", "sentiment": "negative"}
     ]
   }
"""
    )
    
    # Section 5: Optional Web Scraper
    print_section(
        "⚙️ OPTIONAL: Web Scraper (Supplementary Data)",
        """Install Scrapy (optional, takes 5-10 minutes):
   
   uv pip install scrapy scrapy-playwright --only-binary :all:

Then collect from web:
   python -m social_media.app --collect --mode hybrid

Or use just scraper:
   python -m social_media.app --collect --mode scraper

Scrapy is slower but gets extended data from any site.
"""
    )
    
    # Section 6: Documentation
    print_section(
        "📚 DOCUMENTATION",
        """Read these for more info:
   
   - COMPLETE_SETUP_GUIDE.md
   - SYSTEM_STATUS.md (You're reading this one!)
   - GRAPH_API_SETUP.md
   - HYBRID_SCRAPER_PROMPT.md
   - FACEBOOK_INSTAGRAM_API_GUIDE.md
"""
    )
    
    # Section 7: What You Get
    print_section(
        "💰 WHAT YOU GET",
        """From Facebook (Graph API):
   ✓ Posts with metadata
   ✓ Comment threads (up to 15 per post)
   ✓ Likes, comments, shares
   ✓ Author info, timestamps

From Instagram (Graph API):
   ✓ Media posts (images, videos)
   ✓ Captions and hashtags
   ✓ Comments and engagement

Analysis Included:
   ✓ Sentiment detection (positive/negative/neutral)
   ✓ Language detection (Arabic/French/English/Mixed)
   ✓ Dialect detection (Tunisian vs Standard)
   ✓ Bot detection
   ✓ Post type classification
   ✓ Hashtag extraction
"""
    )
    
    # Section 8: Troubleshooting
    print_section(
        "🆘 TROUBLESHOOTING",
        """Q: "No module named feedparser"
A: Run: uv pip install feedparser requests pandas

Q: "FACEBOOK_ACCESS_TOKEN not set"
A: Set environment: $env:FACEBOOK_ACCESS_TOKEN = "token"

Q: "Graph API returns 400 error"
A: Check token validity, page ID, and permissions

Q: "Can't install Scrapy (C++ error)"
A: Try: uv pip install scrapy --only-binary :all:
   Or use Docker: docker run -it python:3.11 bash

Q: "No data returned"
A: Check page ID is valid and public
   Verify token has correct permissions
   Check date range isn't too old
"""
    )
    
    # Section 9: Quick Summary
    print_section(
        "⚡ QUICK SUMMARY",
        """RIGHT NOW:
   python demo_extraction.py          # See demo data
   python graph_api_demo.py            # See setup guide
   python setup_and_status.py          # Check status

NEXT (5 min):
   uv pip install feedparser requests pandas python-dotenv

THEN (5 min):
   Get Facebook token from developers.facebook.com
   $env:FACEBOOK_ACCESS_TOKEN = "your_token"

FINALLY (1 min):
   python -m social_media.app --collect

DONE! 🎉
"""
    )
    
    print("\n" + "✅ " * 10)
    print("  Next Step: python demo_extraction.py")
    print("✅ " * 10 + "\n")

if __name__ == "__main__":
    main()
