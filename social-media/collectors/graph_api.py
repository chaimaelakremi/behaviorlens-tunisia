"""
Facebook and Instagram Graph API collector
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from .base import BaseCollector
from ..schemas import PostSchema, CommentSchema
from ..exceptions import AuthenticationError, RateLimitError, CollectionError

logger = logging.getLogger(__name__)


class GraphAPICollector(BaseCollector):
    """Collector for Facebook and Instagram Graph API"""
    
    BASE_URL = "https://graph.instagram.com/v18.0"
    
    def __init__(self, platform: str, access_token: str, accounts: List[str], config: Dict[str, Any]):
        """
        Initialize Graph API collector
        
        Args:
            platform: "facebook" or "instagram"
            access_token: Graph API access token
            accounts: List of page/account IDs
            config: Additional configuration
        """
        super().__init__(platform, config)
        self.platform = platform
        self.access_token = access_token
        self.accounts = accounts
        self.session: Optional[aiohttp.ClientSession] = None
        self.max_retries = config.get("max_retries", 3)
        self.timeout = config.get("timeout_seconds", 30)
    
    async def _ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def _close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make API request with retry logic
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
        """
        if params is None:
            params = {}
        
        params["access_token"] = self.access_token
        
        await self._ensure_session()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 401:
                        raise AuthenticationError("Invalid access token")
                    elif response.status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    elif response.status >= 400:
                        raise CollectionError(f"API error: {response.status}")
                    
                    return await response.json()
            except RateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Request error (attempt {attempt+1}/{self.max_retries}): {e}")
                    await asyncio.sleep(1)
                else:
                    raise CollectionError(f"Failed after {self.max_retries} attempts: {e}")
    
    async def collect(self) -> List[PostSchema]:
        """Collect posts from Graph API"""
        posts = []
        
        try:
            await self.on_start()
            
            for account_id in self.accounts:
                try:
                    account_posts = await self._collect_account(account_id)
                    posts.extend(account_posts)
                except Exception as e:
                    await self.on_error(e)
                    continue
            
            self.logger.info(f"Collected {len(posts)} posts from {self.platform}")
            
        finally:
            await self.on_stop()
        
        return posts
    
    async def _collect_account(self, account_id: str) -> List[PostSchema]:
        """Collect posts from a single account"""
        posts = []
        
        try:
            # Get posts from account
            response = await self._make_request(
                f"{account_id}/media",
                {
                    "fields": "id,caption,media_type,timestamp,media_url,like_count,"
                             "comments_count",
                    "limit": 25,
                }
            )
            
            for item in response.get("data", []):
                post = await self._parse_post(item, account_id)
                if post:
                    posts.append(post)
                    
                    # Get comments if enabled
                    if self.config.get("include_comments", True):
                        comments = await self._get_comments(item["id"])
                        post.comments = comments
            
        except Exception as e:
            self.logger.error(f"Error collecting from account {account_id}: {e}")
        
        return posts
    
    async def _parse_post(self, item: Dict[str, Any], account_id: str) -> Optional[PostSchema]:
        """Parse API item to PostSchema"""
        try:
            created_at = datetime.fromisoformat(item.get("timestamp", "").replace("Z", "+00:00"))
            
            post = PostSchema(
                source=self.platform,
                url=f"https://{self.platform}.com/{item['id']}",
                post_id=item["id"],
                author=account_id,
                text=item.get("caption", ""),
                media_type=item.get("media_type", "image").lower(),
                likes=item.get("like_count", 0),
                comments_count=item.get("comments_count", 0),
                created_at=created_at,
                scraped_at=datetime.utcnow(),
            )
            
            return self._validate_post(post.model_dump())
        except Exception as e:
            self.logger.error(f"Error parsing post: {e}")
            return None
    
    async def _get_comments(self, post_id: str) -> List[CommentSchema]:
        """Get comments for a post"""
        comments = []
        
        try:
            response = await self._make_request(
                f"{post_id}/comments",
                {
                    "fields": "text,from,timestamp,like_count",
                    "limit": 10,
                }
            )
            
            for item in response.get("data", []):
                comment = CommentSchema(
                    text=item.get("text", ""),
                    author=item.get("from", {}).get("name"),
                    likes=item.get("like_count", 0),
                )
                comments.append(comment)
        except Exception as e:
            self.logger.warning(f"Error getting comments for {post_id}: {e}")
        
        return comments
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API connectivity"""
        try:
            await self._ensure_session()
            
            response = await self._make_request("me", {"fields": "id,name"})
            
            return {
                "status": "healthy",
                "message": "Graph API connection successful",
                "details": {
                    "platform": self.platform,
                    "account": response.get("name"),
                }
            }
        except AuthenticationError:
            return {
                "status": "error",
                "message": "Authentication failed - invalid token",
                "details": {}
            }
        except RateLimitError:
            return {
                "status": "degraded",
                "message": "Rate limit exceeded",
                "details": {}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Health check failed: {e}",
                "details": {}
            }
        finally:
            await self._close_session()
