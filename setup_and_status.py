#!/usr/bin/env python3
"""
BehaviorLens - Complete System Setup & Status
Checks dependencies and provides setup instructions for Graph API + Scrapy
"""

import subprocess
import sys
from pathlib import Path

def check_package(package_name):
    """Check if a package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def get_installed_packages():
    """Get list of installed packages"""
    packages = {
        "feedparser": "RSS feed parsing",
        "requests": "HTTP requests",
        "pandas": "Data processing",
        "python-dotenv": "Environment variables",
        "scrapy": "Web scraping framework",
        "scrapy_playwright": "Playwright integration with Scrapy",
        "playwright": "Browser automation",
        "json": "JSON parsing",
    }
    
    return packages

def display_system_status():
    """Display current system status"""
    
    print("\n" + "=" * 100)
    print("🔧 BEHAVIORLENS - SYSTEM STATUS & SETUP")
    print("=" * 100)
    
    packages = get_installed_packages()
    
    print("\n📦 DEPENDENCY STATUS:")
    print("-" * 100)
    
    core_deps = ["feedparser", "requests", "pandas", "python-dotenv", "json"]
    scraper_deps = ["scrapy", "scrapy_playwright", "playwright"]
    
    core_installed = sum(1 for p in core_deps if check_package(p) or p == "json")
    scraper_installed = sum(1 for p in scraper_deps if check_package(p))
    
    print(f"\n✅ GRAPH API CORE (Required for Graph API):")
    for pkg in core_deps:
        status = "✅" if (check_package(pkg) or pkg == "json") else "❌"
        desc = packages.get(pkg, "")
        print(f"   {status} {pkg:20} - {desc}")
    
    print(f"\n   Status: {core_installed}/{len(core_deps)} installed")
    if core_installed == len(core_deps):
        print(f"   ✅ GRAPH API READY TO USE!")
    
    print(f"\n⚙️ SCRAPY WEB SCRAPER (Optional - for hybrid collection):")
    for pkg in scraper_deps:
        status = "✅" if check_package(pkg) else "❌"
        desc = packages.get(pkg, "")
        print(f"   {status} {pkg:20} - {desc}")
    
    print(f"\n   Status: {scraper_installed}/{len(scraper_deps)} installed")
    if scraper_installed == len(scraper_deps):
        print(f"   ✅ SCRAPY READY TO USE!")
    elif scraper_installed == 0:
        print(f"   ⏳ Scrapy not installed (requires C++ build tools)")
    
    return core_installed == len(core_deps), scraper_installed == len(scraper_deps)

def show_setup_instructions(graph_api_ready, scrapy_ready):
    """Show setup instructions based on current status"""
    
    print("\n" + "=" * 100)
    print("📋 SETUP INSTRUCTIONS")
    print("=" * 100)
    
    if graph_api_ready:
        print("""
✅ GRAPH API SYSTEM - READY!
────────────────────────────

Your system is ready to collect data from Facebook & Instagram!

To enable Graph API collection:

Step 1: Get Access Token (5 minutes)
   a) Go to https://developers.facebook.com
   b) Create app → Business app → Name it "BehaviorLens Tunisia"
   c) Go to Tools → Access Token Debugger
   d) Generate token with permissions:
      - pages_read_posts
      - pages_read_engagement
      - instagram_basic
   e) Copy the token

Step 2: Set Environment Variable (Windows PowerShell)
   $env:FACEBOOK_ACCESS_TOKEN="your_token_here"

Step 3: Configure Your Pages
   Edit: social_media/config.py
   Find: "facebook_graph_api"
   Set: "graph_api_page_ids": ["YOUR_PAGE_ID"]

Step 4: Collect Data!
   python -m social_media.app --collect

You're done! Posts + comments will be automatically collected.
""")
    else:
        print("""
❌ GRAPH API SYSTEM - NEEDS SETUP
─────────────────────────────────

Required packages missing. Install with:

   uv pip install feedparser requests pandas python-dotenv

Then follow the 4-step Graph API setup above.
""")
    
    if not scrapy_ready:
        print("""
⏳ SCRAPY WEB SCRAPER - OPTIONAL
────────────────────────────────

For web scraping (supplementary data collection), you need:

Option A: Install Pre-built Wheels (Fastest)
   uv pip install scrapy --only-binary :all:

Option B: Install Visual C++ Build Tools First
   1) Download: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   2) Run installer
   3) Run: uv pip install scrapy scrapy-playwright playwright

Option C: Use Docker (Easiest if you have Docker)
   # Run collection in container with all packages pre-installed
   docker run -it python:3.11 bash
   pip install scrapy scrapy-playwright playwright

Without Scrapy:
   • Graph API still works perfectly
   • Web scraper just won't be available
   • You can add it later anytime
""")

def show_usage_guide(graph_api_ready):
    """Show usage guide"""
    
    print("\n" + "=" * 100)
    print("🚀 USAGE GUIDE")
    print("=" * 100)
    
    if graph_api_ready:
        print("""
1. COLLECT DATA FROM FACEBOOK & INSTAGRAM (WITH CREDENTIALS)
   ────────────────────────────────────────────────────────
   python -m social_media.app --collect

2. DEMO MODE (WITHOUT CREDENTIALS)
   ─────────────────────────────────
   python demo_extraction.py
   
   OR show Graph API examples:
   python graph_api_demo.py

3. VIEW STATISTICS
   ────────────────
   python -m social_media.app --stats

4. EXPORT DATA
   ────────────
   python -m social_media.app --export csv
   python -m social_media.app --export json

5. RUN EXAMPLES
   ─────────────
   python -m social_media.examples 1  # Example 1
   python -m social_media.examples 2  # Example 2
   ... etc
""")
    
    print("""
DATA LOCATION
─────────────
Collected data saved to:
   data/extracted/             - Demo data
   data/graph_api/             - Graph API extractions
   data/processed/posts.json   - Processed posts
   data/logs/social_media.log  - Logs

DOCUMENTATION
──────────────
Read these for detailed guides:
   • GRAPH_API_SETUP.md - Complete Graph API guide
   • HYBRID_SCRAPER_PROMPT.md - Scraper setup guide
   • FACEBOOK_INSTAGRAM_API_GUIDE.md - Why Graph API is better
   • DOCUMENTATION_INDEX.md - All documentation
""")

def show_troubleshooting():
    """Show common troubleshooting"""
    
    print("\n" + "=" * 100)
    print("🆘 TROUBLESHOOTING")
    print("=" * 100)
    
    print("""
Q: Import Error "No module named 'feedparser'"
A: Missing core dependency. Install: uv pip install feedparser requests pandas

Q: "Microsoft Visual C++ 14.0 required" when installing Scrapy
A: You need C++ build tools. Either:
   1. Download C++ build tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   2. Use pre-built wheels: uv pip install scrapy --only-binary :all:
   3. Use Docker: docker run python:3.11 pip install scrapy

Q: "FACEBOOK_ACCESS_TOKEN not set"
A: Set environment variable:
   PowerShell: $env:FACEBOOK_ACCESS_TOKEN="your_token"
   
   Or create .env file in project root:
   FACEBOOK_ACCESS_TOKEN=your_token
   
   System will auto-detect and use it.

Q: No data collected from Graph API
A: Check:
   1. Access token is valid (test at developers.facebook.com)
   2. Page IDs are correct (yours, not example IDs)
   3. Permissions are set (pages_read_posts, pages_read_engagement)
   4. Check logs: cat data/logs/social_media.log

Q: Want to use Scrapy but have build issues
A: Easiest solution - use Docker:
   1. Install Docker Desktop
   2. Run: docker run -it -v $(pwd):/app python:3.11 bash
   3. cd /app && pip install scrapy scrapy-playwright playwright
   4. Run your collection
""")

if __name__ == "__main__":
    print("\n🎯 BehaviorLens System Setup")
    
    # Check status
    graph_api_ready, scrapy_ready = display_system_status()
    
    # Show instructions
    show_setup_instructions(graph_api_ready, scrapy_ready)
    
    # Show usage
    show_usage_guide(graph_api_ready)
    
    # Show troubleshooting
    show_troubleshooting()
    
    # Summary
    print("\n" + "=" * 100)
    print("✨ SUMMARY")
    print("=" * 100)
    
    if graph_api_ready:
        print("""
✅ Your system is ready!

NEXT STEPS:
1. Get your Graph API token (5 minutes)
2. Set environment variable
3. Run: python -m social_media.app --collect
4. Get real Facebook & Instagram data with comments!

For demo mode without credentials:
   python graph_api_demo.py
   python demo_extraction.py
""")
    else:
        print("""
⏳ Almost ready! Just need to install core packages:

uv pip install feedparser requests pandas python-dotenv

Then follow the 4-step Graph API setup above.
""")
    
    if scrapy_ready:
        print("\n✅ Scrapy is also installed - hybrid collection available!")
    else:
        print("\n📌 Optional: Install Scrapy later for web scraping (see instructions above)")
    
    print("\n" + "=" * 100 + "\n")
