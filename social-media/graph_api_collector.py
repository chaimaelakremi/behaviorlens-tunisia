"""
Facebook & Instagram Graph API Collector
Official API method for collecting posts and comments from Facebook/Instagram

IMPORTANT LEGAL NOTES:
- Graph API requires official authorization from Meta
- Rate limits apply (varies by API tier)
- Must comply with Meta's data use policies
- Cannot use for surveillance or discrimination
- Must provide privacy disclosures to users

This module is OPTIONAL and requires API credentials to function.
Fallback: RSS feeds are used by default (no API needed).
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger("facebook_instagram_api")


class FacebookInstagramGraphAPICollector:
    """
    Collect posts and comments from Facebook & Instagram using official Graph API
    
    REQUIRES:
    - Facebook App ID
    - Facebook App Secret
    - Access Token (from app or page admin)
    
    GET STARTED:
    1. Go to https://developers.facebook.com
    2. Create an app
    3. Get the App ID and Secret
    4. Request permissions: pages_read_posts, pages_read_engagement
    """
    
    # Graph API Endpoints
    BASE_URL = "https://graph.instagram.com"
    FACEBOOK_BASE_URL = "https://graph.facebook.com/v18.0"
    
    # Rate limiting
    REQUESTS_PER_HOUR = 200  # Conservative limit
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        page_ids: Optional[List[str]] = None,
        instagram_business_account_ids: Optional[List[str]] = None
    ):
        """
        Initialize Graph API collector
        
        Args:
            app_id: Facebook App ID
            app_secret: Facebook App Secret
            access_token: Access token (user or page token)
            page_ids: List of Facebook page IDs to collect from
            instagram_business_account_ids: List of Instagram Business Account IDs
        """
        # Get credentials from environment or parameters
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
        
        self.page_ids = page_ids or []
        self.instagram_account_ids = instagram_business_account_ids or []
        
        if not self.access_token:
            logger.warning(
                "No access token found. Graph API collection disabled. "
                "Set FACEBOOK_ACCESS_TOKEN environment variable or pass as parameter."
            )
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Graph API collector initialized")
    
    def get_facebook_posts(
        self,
        page_id: str,
        limit: int = 50,
        include_comments: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Collect posts from a Facebook page
        
        Args:
            page_id: Facebook Page ID
            limit: Max posts to collect
            include_comments: Include comment threads
            
        Returns:
            List of posts with metadata
        """
        if not self.enabled:
            logger.warning("Graph API not enabled - skipping Facebook collection")
            return []
        
        try:
            url = f"{self.FACEBOOK_BASE_URL}/{page_id}/posts"
            
            params = {
                "access_token": self.access_token,
                "limit": limit,
                "fields": "id,message,story,created_time,permalink_url,shares,likes.summary(true),comments.summary(true){from,message,created_time,likes.summary(true)}"
            }
            
            logger.info(f"Fetching posts from Facebook page {page_id}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for post in data.get("data", []):
                normalized_post = {
                    "id": post.get("id"),
                    "text": post.get("message") or post.get("story", ""),
                    "platform": "facebook",
                    "source": "graph_api",
                    "author": "facebook_page",
                    "timestamp": post.get("created_time"),
                    "url": post.get("permalink_url"),
                    "engagement": {
                        "likes": post.get("likes", {}).get("summary", {}).get("total_count", 0),
                        "comments": post.get("comments", {}).get("summary", {}).get("total_count", 0),
                        "shares": post.get("shares", {}).get("count", 0)
                    },
                    "comments": []
                }
                
                # Include comment threads if requested
                if include_comments and "comments" in post:
                    for comment in post.get("comments", {}).get("data", [])[:10]:  # Limit to 10 comments
                        normalized_post["comments"].append({
                            "author": comment.get("from", {}).get("name", "unknown"),
                            "text": comment.get("message"),
                            "timestamp": comment.get("created_time"),
                            "likes": comment.get("likes", {}).get("summary", {}).get("total_count", 0)
                        })
                
                posts.append(normalized_post)
            
            logger.info(f"✓ Collected {len(posts)} posts from Facebook page {page_id}")
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Facebook posts: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def get_instagram_posts(
        self,
        business_account_id: str,
        limit: int = 50,
        include_comments: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Collect posts from an Instagram Business Account
        
        Args:
            business_account_id: Instagram Business Account ID
            limit: Max posts to collect
            include_comments: Include comment threads
            
        Returns:
            List of posts with metadata
        """
        if not self.enabled:
            logger.warning("Graph API not enabled - skipping Instagram collection")
            return []
        
        try:
            url = f"{self.FACEBOOK_BASE_URL}/{business_account_id}/ig_hashtag_search"
            
            params = {
                "access_token": self.access_token,
                "user_id": business_account_id,
                "fields": "id,caption,media_type,timestamp,media_product_type,permalink,like_count,comments_count,ig_id"
            }
            
            logger.info(f"Fetching posts from Instagram account {business_account_id}")
            
            # Get recent media
            media_url = f"{self.FACEBOOK_BASE_URL}/{business_account_id}/ig_media"
            response = requests.get(media_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for media in data.get("data", [])[:limit]:
                normalized_post = {
                    "id": media.get("id"),
                    "text": media.get("caption", ""),
                    "platform": "instagram",
                    "source": "graph_api",
                    "author": "instagram_business",
                    "timestamp": media.get("timestamp"),
                    "url": media.get("permalink"),
                    "media_type": media.get("media_type"),
                    "engagement": {
                        "likes": media.get("like_count", 0),
                        "comments": media.get("comments_count", 0),
                        "shares": 0
                    },
                    "comments": []
                }
                
                # Get comments if requested
                if include_comments:
                    comments_url = f"{self.FACEBOOK_BASE_URL}/{media.get('id')}/comments"
                    comments_params = {
                        "access_token": self.access_token,
                        "fields": "from,text,timestamp,like_count"
                    }
                    
                    try:
                        comments_response = requests.get(
                            comments_url,
                            params=comments_params,
                            timeout=10
                        )
                        comments_response.raise_for_status()
                        
                        for comment in comments_response.json().get("data", [])[:10]:
                            normalized_post["comments"].append({
                                "author": comment.get("from", {}).get("name", "unknown"),
                                "text": comment.get("text"),
                                "timestamp": comment.get("timestamp"),
                                "likes": comment.get("like_count", 0)
                            })
                    except Exception as e:
                        logger.warning(f"Could not fetch comments for media {media.get('id')}: {e}")
                
                posts.append(normalized_post)
            
            logger.info(f"✓ Collected {len(posts)} posts from Instagram account {business_account_id}")
            return posts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Instagram posts: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def collect_all(
        self,
        include_comments: bool = True,
        limit_per_source: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Collect from all configured pages and accounts
        
        Args:
            include_comments: Include comment threads
            limit_per_source: Max posts per source
            
        Returns:
            Combined list of posts from all sources
        """
        all_posts = []
        
        # Collect from Facebook pages
        for page_id in self.page_ids:
            try:
                posts = self.get_facebook_posts(
                    page_id,
                    limit=limit_per_source,
                    include_comments=include_comments
                )
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Error collecting from Facebook page {page_id}: {e}")
        
        # Collect from Instagram accounts
        for account_id in self.instagram_account_ids:
            try:
                posts = self.get_instagram_posts(
                    account_id,
                    limit=limit_per_source,
                    include_comments=include_comments
                )
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Error collecting from Instagram account {account_id}: {e}")
        
        logger.info(f"✓ Total posts collected via Graph API: {len(all_posts)}")
        return all_posts


class InstagramScrapingAlternative:
    """
    SCRAPING WARNING - NOT RECOMMENDED
    
    This is an educational reference for what's technically possible.
    
    ⚠️ LEGAL & ETHICAL CONCERNS:
    1. Violates Instagram Terms of Service
    2. Instagram actively blocks scrapers
    3. Account bans are common
    4. Unreliable (methods break frequently)
    5. Performance: Very slow, frequent failures
    6. Rate limits: Aggressive IP blocking
    7. Legal risk: CFAA violations in some jurisdictions
    
    ✅ RECOMMENDED ALTERNATIVE:
    Use Graph API (requires approval but fully legal)
    
    EXAMPLE OF WHAT DOESN'T WORK:
    - Selenium browser automation (detected and blocked)
    - Request libraries with headers spoofing (blocked)
    - Proxy rotation (expensive and unreliable)
    - Headless browsers (detected)
    
    REALISTIC OUTCOME:
    - 50% success rate
    - Account ban after 1-2 weeks
    - Data quality issues
    - Maintenance nightmare
    """
    
    @staticmethod
    def warning():
        """Print scraping warning"""
        warning_text = """
        
╔═══════════════════════════════════════════════════════════════╗
║                    ⚠️  SCRAPING WARNING  ⚠️                   ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Instagram/Facebook scraping is NOT RECOMMENDED because:     ║
║                                                               ║
║  ❌ BLOCKED: Instagram actively detects and blocks scrapers  ║
║  ❌ UNRELIABLE: Methods break every few weeks               ║
║  ❌ SLOW: Each request takes 5-30 seconds                   ║
║  ❌ RISKS: Account ban, IP ban, legal issues                ║
║  ❌ LIMITED DATA: Can't get private/protected data          ║
║                                                               ║
║  ✅ BETTER ALTERNATIVE: Use official Graph API              ║
║  ✅ LEGAL: Fully authorized and compliant                   ║
║  ✅ RELIABLE: Guaranteed access to data                     ║
║  ✅ FAST: 100ms per request                                 ║
║  ✅ COMPLETE: Full metadata and comments                    ║
║                                                               ║
║  SETUP GRAPH API (5 minutes):                               ║
║  1. Go to https://developers.facebook.com                   ║
║  2. Create an app (free tier available)                     ║
║  3. Request these permissions:                              ║
║     - pages_read_posts                                       ║
║     - pages_read_engagement                                  ║
║     - instagram_basic                                        ║
║  4. Get your access token                                    ║
║  5. Set environment variable:                               ║
║     export FACEBOOK_ACCESS_TOKEN="your_token"               ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
        """
        print(warning_text)


# Example usage
if __name__ == "__main__":
    # Show scraping warning
    InstagramScrapingAlternative.warning()
    
    # Graph API example (requires credentials)
    print("\nGraph API Example:")
    print("-" * 60)
    
    collector = FacebookInstagramGraphAPICollector(
        access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"),
        page_ids=["123456789"],  # Your Facebook page ID
        instagram_business_account_ids=["987654321"]  # Your Instagram Business Account ID
    )
    
    if collector.enabled:
        print("✓ Collector enabled with valid credentials")
        
        # This would collect real data
        # posts = collector.collect_all(include_comments=True)
        # print(f"Collected {len(posts)} posts")
    else:
        print("✗ Set FACEBOOK_ACCESS_TOKEN to enable Graph API collection")
        print("\nTo get started:")
        print("1. Visit https://developers.facebook.com")
        print("2. Create a free app")
        print("3. Request pages_read_posts and pages_read_engagement permissions")
        print("4. Get your access token")
        print("5. Set: export FACEBOOK_ACCESS_TOKEN='your_token'")
