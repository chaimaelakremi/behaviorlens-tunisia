#!/usr/bin/env python3
"""
Demo: Sample Extracted Data from BehaviorLens
Shows what the system collects from Facebook, Instagram, Reddit, and Twitter
"""

import json
from datetime import datetime
from pathlib import Path

def generate_sample_data():
    """Generate realistic sample Tunisian social media data"""
    
    sample_posts = [
        {
            "id": "sm_fb_001",
            "source": "graph_api",
            "platform": "facebook",
            "url": "https://facebook.com/MosaiqueFM/posts/123456",
            "author": "Mosaique FM",
            "text": "خبر عاجل: أسعار المحروقات ترتفع 15% في تونس. الحكومة تدرس إجراءات للحد من تأثير الغلاء على المواطنين.",
            "post_type": "news",
            "sentiment": "negative",
            "hashtags": ["#تونس", "#أسعار", "#محروقات"],
            "media_type": "text",
            "is_tunisian": True,
            "timestamp": "2026-05-01T10:30:00Z",
            "engagement": {
                "likes": 1234,
                "comments": 87,
                "shares": 45
            },
            "comment_count": 3,
            "comments": [
                {
                    "author": "Ahmed Ben Ali",
                    "text": "هذا كارثة! لا يمكن تحمل هذه الأسعار. الحكومة يجب أن تفعل شيئا",
                    "sentiment": "negative",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-05-01T10:45:00Z",
                    "likes": 234
                },
                {
                    "author": "Fatima Zahra",
                    "text": "الأسعار غالية برشا. متى سنرجع للأسعار العادية؟",
                    "sentiment": "negative",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-05-01T11:00:00Z",
                    "likes": 187
                },
                {
                    "author": "Mohamed Hassan",
                    "text": "الحكومة مسؤولة عن هذا الوضع السيء",
                    "sentiment": "negative",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-05-01T11:15:00Z",
                    "likes": 156
                }
            ]
        },
        {
            "id": "sm_ig_002",
            "source": "graph_api",
            "platform": "instagram",
            "url": "https://instagram.com/p/ABC123DEF456/",
            "author": "tunisienumerique",
            "text": "#TunisiaProblems النقل العام مصدر إزعاج! الحافلات القديمة والتأخيرات المستمرة 😠",
            "post_type": "complaint",
            "sentiment": "negative",
            "hashtags": ["#TunisiaProblems", "#transport", "#public_transport"],
            "media_type": "image",
            "is_tunisian": True,
            "timestamp": "2026-05-01T14:30:00Z",
            "engagement": {
                "likes": 2345,
                "comments": 234,
                "shares": 0
            },
            "comment_count": 2,
            "comments": [
                {
                    "author": "user_tunisia_2024",
                    "text": "تسعيرة النقل غلات برشا. 3 دنانير للمسافة القصيرة!",
                    "sentiment": "negative",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-05-01T14:45:00Z",
                    "likes": 445
                },
                {
                    "author": "tunisie_voice",
                    "text": "المشكلة أن الحافلات غير صحية وغالبا ممتلئة جدا",
                    "sentiment": "negative",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-05-01T15:00:00Z",
                    "likes": 389
                }
            ]
        },
        {
            "id": "sm_reddit_003",
            "source": "rss",
            "platform": "reddit",
            "url": "https://reddit.com/r/tunisia/comments/xyz123/",
            "author": "TunisianCitizen",
            "text": "Employment crisis in Tunisia: Youth unemployment reaches 35%. Is the government doing enough?",
            "post_type": "opinion",
            "sentiment": "negative",
            "hashtags": ["#employment", "#tunisia", "#crisis"],
            "media_type": "text",
            "is_tunisian": True,
            "timestamp": "2026-04-30T09:00:00Z",
            "engagement": {
                "likes": 567,
                "comments": 45,
                "shares": 12
            },
            "comment_count": 2,
            "comments": [
                {
                    "author": "RedditUser_TN",
                    "text": "The government needs to create real jobs, not just statistics",
                    "sentiment": "negative",
                    "is_tunisian": False,
                    "hashtags": [],
                    "timestamp": "2026-04-30T10:30:00Z",
                    "likes": 123
                },
                {
                    "author": "TunisianStudent",
                    "text": "I graduated 2 years ago, still can't find a job. Very frustrated",
                    "sentiment": "negative",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-04-30T11:00:00Z",
                    "likes": 98
                }
            ]
        },
        {
            "id": "sm_twitter_004",
            "source": "rss",
            "platform": "twitter",
            "url": "https://twitter.com/BBCNews/status/123456789",
            "author": "BBC News",
            "text": "Tunisia's inflation hits record high in April. Economic crisis deepens as citizens struggle with rising prices.",
            "post_type": "news",
            "sentiment": "negative",
            "hashtags": ["#Tunisia", "#Economy", "#Inflation"],
            "media_type": "text",
            "is_tunisian": True,
            "timestamp": "2026-05-01T08:15:00Z",
            "engagement": {
                "likes": 2100,
                "comments": 156,
                "shares": 89
            },
            "comment_count": 1,
            "comments": [
                {
                    "author": "Economics_Expert",
                    "text": "This is a systemic problem. Tunisia needs structural economic reforms",
                    "sentiment": "negative",
                    "is_tunisian": False,
                    "hashtags": [],
                    "timestamp": "2026-05-01T09:00:00Z",
                    "likes": 245
                }
            ]
        },
        {
            "id": "sm_fb_005",
            "source": "graph_api",
            "platform": "facebook",
            "url": "https://facebook.com/ShemssFM/posts/789012",
            "author": "Shems FM",
            "text": "قصة نجاح: شاب تونسي ينجح في تأسيس شركة تقنية تحقق أرباحا كبيرة 🎉",
            "post_type": "news",
            "sentiment": "positive",
            "hashtags": ["#تونس", "#ريادة_أعمال", "#نجاح"],
            "media_type": "text",
            "is_tunisian": True,
            "timestamp": "2026-04-30T16:45:00Z",
            "engagement": {
                "likes": 3456,
                "comments": 234,
                "shares": 567
            },
            "comment_count": 2,
            "comments": [
                {
                    "author": "Entrepreneur_TN",
                    "text": "هذا رائع! أتمنى أن يلهم الآخرين. تونس بحاجة إلى أصحاب أعمال مثل هذا الشاب",
                    "sentiment": "positive",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-04-30T17:15:00Z",
                    "likes": 567
                },
                {
                    "author": "Youth_Voice",
                    "text": "ممتاز! إذا كان هناك مثل هذه الفرص للآخرين أيضا",
                    "sentiment": "positive",
                    "is_tunisian": True,
                    "hashtags": [],
                    "timestamp": "2026-04-30T17:45:00Z",
                    "likes": 345
                }
            ]
        }
    ]
    
    return sample_posts

def display_results(posts):
    """Display results in formatted output"""
    
    print("\n" + "=" * 100)
    print("BEHAVIORLENS - EXTRACTED SOCIAL MEDIA DATA (SAMPLE)")
    print("=" * 100)
    
    # Statistics
    print(f"\n📊 STATISTICS")
    print("-" * 100)
    print(f"Total Posts Collected: {len(posts)}")
    
    # By platform
    by_platform = {}
    by_sentiment = {}
    by_language = {}
    by_category = {}
    
    for post in posts:
        platform = post.get('platform', 'unknown')
        sentiment = post.get('sentiment', 'unknown')
        language = 'Arabic' if any(ord(c) > 127 for c in post.get('text', '')) else 'English/French'
        category = post.get('post_type', 'unknown')
        
        by_platform[platform] = by_platform.get(platform, 0) + 1
        by_sentiment[sentiment] = by_sentiment.get(sentiment, 0) + 1
        by_language[language] = by_language.get(language, 0) + 1
        by_category[category] = by_category.get(category, 0) + 1
    
    print(f"\n📱 By Platform:")
    for platform, count in sorted(by_platform.items()):
        print(f"   • {platform.upper()}: {count} posts")
    
    print(f"\n😊 By Sentiment:")
    for sentiment, count in sorted(by_sentiment.items()):
        emoji = "😢" if sentiment == "negative" else "😐" if sentiment == "neutral" else "😊"
        print(f"   {emoji} {sentiment.capitalize()}: {count} posts")
    
    print(f"\n🗣️ By Language:")
    for language, count in sorted(by_language.items()):
        print(f"   • {language}: {count} posts")
    
    print(f"\n📂 By Category:")
    for category, count in sorted(by_category.items()):
        print(f"   • {category.capitalize()}: {count} posts")
    
    # Detailed samples
    print("\n" + "=" * 100)
    print("📰 SAMPLE POSTS (First 3)")
    print("=" * 100)
    
    for i, post in enumerate(posts[:3], 1):
        print(f"\n--- POST {i} ---")
        print(f"🔗 Platform: {post.get('platform', 'N/A').upper()}")
        print(f"👤 Author: {post.get('author', 'N/A')}")
        print(f"📝 Text: {post.get('text', 'N/A')}")
        print(f"😊 Sentiment: {post.get('sentiment', 'N/A').upper()}")
        print(f"📂 Type: {post.get('post_type', 'N/A')}")
        print(f"🏷️ Hashtags: {', '.join(post.get('hashtags', []))}")
        print(f"📅 Timestamp: {post.get('timestamp', 'N/A')}")
        print(f"👍 Engagement: {post['engagement']['likes']} likes, {post['engagement']['comments']} comments")
        
        comments = post.get('comments', [])
        if comments:
            print(f"\n   💬 Top Comments ({len(comments)} total):")
            for j, comment in enumerate(comments[:2], 1):
                print(f"      {j}. @{comment['author']}: \"{comment['text'][:80]}...\"")
                print(f"         Sentiment: {comment['sentiment'].upper()}, Likes: {comment['likes']}")
    
    # JSON export
    output_dir = Path("data") / "extracted"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "sample_extraction.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 100)
    print(f"✅ SUCCESS - Sample data saved to: {output_file}")
    print("=" * 100)
    
    # Show JSON structure
    print("\n" + "=" * 100)
    print("📋 JSON STRUCTURE (Sample Post)")
    print("=" * 100)
    print(json.dumps(posts[0], indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 100)
    print("🎯 WHAT THIS DEMONSTRATES")
    print("=" * 100)
    print("""
✅ Graph API collects:
   • Posts from Facebook pages
   • Posts from Instagram business accounts
   • Full comment threads
   • Engagement metrics (likes, comments, shares)
   • Timestamps and author information

✅ Data Analysis includes:
   • Sentiment classification (positive, negative, neutral)
   • Post type detection (news, complaint, opinion, humor, promotion, question, event)
   • Language detection (Arabic, French, English, mixed)
   • Hashtag extraction
   • Tunisian dialect detection

✅ Both Graph API and RSS Feeds provide:
   • Unified data schema
   • Real-time collection
   • Comment sentiment analysis
   • Category classification

📊 Statistics & Aggregation:
   • Breakdown by platform, sentiment, language, category
   • Engagement metrics per post
   • Comment analysis for crisis detection
   • Influencer identification by comment engagement
""")

if __name__ == "__main__":
    print("\n🚀 Generating sample Tunisian social media data...")
    posts = generate_sample_data()
    display_results(posts)
