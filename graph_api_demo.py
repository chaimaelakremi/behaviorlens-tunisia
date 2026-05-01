#!/usr/bin/env python3
"""
BehaviorLens - Graph API Setup & Demo
Shows Graph API data extraction and guides credential setup
"""

import os
import json
from pathlib import Path
from datetime import datetime

def check_graph_api_credentials():
    """Check if Graph API credentials are configured"""
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    app_id = os.getenv("FACEBOOK_APP_ID")
    app_secret = os.getenv("FACEBOOK_APP_SECRET")
    
    print("\n" + "=" * 100)
    print("🔐 GRAPH API CREDENTIAL CHECK")
    print("=" * 100)
    
    if token:
        print(f"✅ FACEBOOK_ACCESS_TOKEN: Set ({token[:20]}...)")
    else:
        print(f"❌ FACEBOOK_ACCESS_TOKEN: Not set")
    
    if app_id:
        print(f"✅ FACEBOOK_APP_ID: Set ({app_id[:10]}...)")
    else:
        print(f"❌ FACEBOOK_APP_ID: Not set")
    
    if app_secret:
        print(f"✅ FACEBOOK_APP_SECRET: Set ({app_secret[:10]}...)")
    else:
        print(f"❌ FACEBOOK_APP_SECRET: Not set")
    
    return bool(token)

def setup_graph_api_guide():
    """Show setup guide for Graph API"""
    print("\n" + "=" * 100)
    print("📋 QUICK SETUP GUIDE - GET YOUR GRAPH API TOKEN (5 MINUTES)")
    print("=" * 100)
    
    print("""
Step 1: Create Facebook App
   → Go to: https://developers.facebook.com
   → Click: My Apps → Create App
   → App Name: "BehaviorLens Tunisia"
   → App Type: Business

Step 2: Get App ID & Secret
   → Settings → Basic
   → Copy your App ID
   → Click "Show" next to App Secret and copy it

Step 3: Generate Access Token
   → Tools → Access Token Debugger
   → Generate Token (with these permissions):
      ✓ pages_read_posts
      ✓ pages_read_engagement
      ✓ instagram_basic

Step 4: Set Environment Variables

   Linux/Mac:
   ─────────
   export FACEBOOK_ACCESS_TOKEN="your_token_here"
   export FACEBOOK_APP_ID="your_app_id_here"
   export FACEBOOK_APP_SECRET="your_app_secret_here"

   Windows PowerShell:
   ─────────────────
   $env:FACEBOOK_ACCESS_TOKEN="your_token_here"
   $env:FACEBOOK_APP_ID="your_app_id_here"
   $env:FACEBOOK_APP_SECRET="your_app_secret_here"

Step 5: Add Your Page/Account IDs
   → Edit social_media/config.py
   → Find "facebook_graph_api" section
   → Set "graph_api_page_ids": ["YOUR_PAGE_ID"]
   → Find "instagram_graph_api" section
   → Set "graph_api_business_account_ids": ["YOUR_ACCOUNT_ID"]

That's it! Ready to collect data.
""")

def generate_realistic_graph_api_data():
    """Generate realistic data that Graph API would return"""
    
    print("\n" + "=" * 100)
    print("📊 SIMULATED GRAPH API EXTRACTION")
    print("=" * 100)
    print("\n(These are realistic examples of what Graph API returns)")
    
    data = {
        "facebook_pages": [
            {
                "id": "graph_api_facebook_mosaique",
                "source": "graph_api",
                "platform": "facebook",
                "page_name": "Mosaique FM",
                "url": "https://graph.facebook.com/v18.0/109999999/posts?fields=id,message,created_time,permalink_url,shares",
                "posts": [
                    {
                        "id": "109999999_1234567890",
                        "message": "🔴 BREAKING: Central Bank announces emergency measures to combat inflation",
                        "created_time": "2026-05-01T09:15:00+0000",
                        "permalink_url": "https://facebook.com/MosaiqueFM/posts/1234567890",
                        "shares": {"data": [], "summary": {"total_count": 234}},
                        "story": "Breaking News Post",
                        "type": "status",
                        "engagement": {
                            "likes_count": 5678,
                            "comments_count": 432,
                            "shares_count": 234
                        },
                        "comments": {
                            "data": [
                                {
                                    "id": "comment_001",
                                    "from": {"name": "Ahmed Ben Ali", "id": "user123"},
                                    "message": "الحكومة تأخرت كثيرا. يجب تحرك فوري",
                                    "created_time": "2026-05-01T09:30:00+0000",
                                    "like_count": 567
                                },
                                {
                                    "id": "comment_002",
                                    "from": {"name": "Fatima Zahra", "id": "user456"},
                                    "message": "هل هذه الإجراءات ستخفف من الغلاء؟",
                                    "created_time": "2026-05-01T09:45:00+0000",
                                    "like_count": 423
                                },
                                {
                                    "id": "comment_003",
                                    "from": {"name": "Mohamed Hassan", "id": "user789"},
                                    "message": "Too little, too late. Situation is already dire.",
                                    "created_time": "2026-05-01T10:00:00+0000",
                                    "like_count": 289
                                }
                            ],
                            "summary": {"total_count": 432}
                        }
                    }
                ]
            }
        ],
        "instagram_business": [
            {
                "id": "graph_api_instagram_tap",
                "source": "graph_api",
                "platform": "instagram",
                "business_account": "TAP Tunisia",
                "url": "https://graph.instagram.com/v18.0/17999999/ig_media?fields=id,caption,media_type,timestamp,like_count",
                "posts": [
                    {
                        "id": "17999999999999",
                        "caption": "#Tunisia #News: Government announces new employment program targeting youth. Read full story in bio.",
                        "media_type": "IMAGE",
                        "timestamp": "2026-05-01T08:00:00+0000",
                        "like_count": 8934,
                        "comments_count": 678,
                        "engagement": {
                            "reach": 45000,
                            "impressions": 67000
                        },
                        "comments": {
                            "data": [
                                {
                                    "id": "ig_comment_001",
                                    "from": {"username": "youth_tunisia", "id": "user111"},
                                    "text": "Finally! We need jobs, not promises",
                                    "timestamp": "2026-05-01T08:15:00+0000",
                                    "like_count": 234
                                },
                                {
                                    "id": "ig_comment_002",
                                    "from": {"username": "tunisia_voice", "id": "user222"},
                                    "text": "Will this actually create REAL jobs or just statistics?",
                                    "timestamp": "2026-05-01T08:30:00+0000",
                                    "like_count": 189
                                }
                            ],
                            "summary": {"total_count": 678}
                        }
                    }
                ]
            }
        ]
    }
    
    return data

def display_graph_api_data(data):
    """Display extracted Graph API data in readable format"""
    
    print("\n" + "=" * 100)
    print("📱 GRAPH API - FACEBOOK DATA")
    print("=" * 100)
    
    for page_data in data["facebook_pages"]:
        print(f"\n📄 Page: {page_data['page_name']}")
        print(f"API Call: {page_data['url']}")
        
        for post in page_data["posts"]:
            print(f"\n   📝 Post ID: {post['id']}")
            print(f"   📌 Message: {post['message']}")
            print(f"   📅 Posted: {post['created_time']}")
            print(f"   👍 Likes: {post['engagement']['likes_count']}")
            print(f"   💬 Comments: {post['engagement']['comments_count']}")
            print(f"   🔄 Shares: {post['engagement']['shares_count']}")
            print(f"   🔗 URL: {post['permalink_url']}")
            
            if post.get("comments"):
                print(f"\n   💬 Top Comments ({post['comments']['summary']['total_count']} total):")
                for comment in post["comments"]["data"][:2]:
                    print(f"      • @{comment['from']['name']}: {comment['message'][:60]}...")
                    print(f"        ❤️ Likes: {comment['like_count']}")
    
    print("\n" + "=" * 100)
    print("📱 GRAPH API - INSTAGRAM DATA")
    print("=" * 100)
    
    for ig_data in data["instagram_business"]:
        print(f"\n📸 Account: {ig_data['business_account']}")
        print(f"API Call: {ig_data['url']}")
        
        for post in ig_data["posts"]:
            print(f"\n   📸 Post ID: {post['id']}")
            print(f"   📝 Caption: {post['caption'][:80]}...")
            print(f"   📅 Posted: {post['timestamp']}")
            print(f"   👍 Likes: {post['like_count']}")
            print(f"   💬 Comments: {post['comments_count']}")
            print(f"   📊 Reach: {post['engagement']['reach']}")
            
            if post.get("comments"):
                print(f"\n   💬 Top Comments ({post['comments']['summary']['total_count']} total):")
                for comment in post["comments"]["data"][:2]:
                    print(f"      • @{comment['from']['username']}: {comment['text'][:60]}...")
                    print(f"        ❤️ Likes: {comment['like_count']}")
    
    # Save to file
    output_dir = Path("data") / "graph_api"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "sample_extraction.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Full data saved to: {output_file}")

def show_next_steps():
    """Show what to do next"""
    
    print("\n" + "=" * 100)
    print("🚀 NEXT STEPS")
    print("=" * 100)
    
    print("""
OPTION 1: Use Graph API Immediately (No Setup)
────────────────────────────────────────────────
1. Get your access token (follow guide above)
2. Set environment variable: export FACEBOOK_ACCESS_TOKEN="your_token"
3. Run: python -m social_media.app --collect
4. Get real data from Facebook & Instagram!

OPTION 2: Install Scrapy for Web Scraper (Supplementary)
──────────────────────────────────────────────────────────
1. Install Scrapy: pip install scrapy scrapy-playwright playwright
2. Configure scraper in social_media/config.py
3. Run hybrid collection: python -m social_media.app --collect --mode hybrid
4. Get data from both Graph API and web scraper!

OPTION 3: Use Demo Mode (Right Now!)
──────────────────────────────────────
1. System already has demo data configured
2. Run: python demo_extraction.py
3. Get sample extracted data without needing credentials!

📚 Documentation:
   • GRAPH_API_SETUP.md - Complete setup guide
   • FACEBOOK_INSTAGRAM_API_GUIDE.md - API comparison
   • FACEBOOK_INSTAGRAM_COMMENTS.md - Comment analysis
   • HYBRID_SCRAPER_PROMPT.md - Web scraper setup
""")

if __name__ == "__main__":
    print("\n🎯 BehaviorLens - Graph API Data Extraction Demo")
    print("=" * 100)
    
    # Check credentials
    has_credentials = check_graph_api_credentials()
    
    # Show setup guide
    setup_graph_api_guide()
    
    # Generate and display data
    print("\n" + "=" * 100)
    print("🔄 GENERATING SAMPLE GRAPH API DATA...")
    print("=" * 100)
    
    data = generate_realistic_graph_api_data()
    display_graph_api_data(data)
    
    # Show next steps
    show_next_steps()
    
    print("\n" + "=" * 100)
    if has_credentials:
        print("✅ READY TO USE - You have Graph API credentials configured!")
    else:
        print("⏭️ NEXT: Follow the setup guide above to get your access token")
    print("=" * 100)
