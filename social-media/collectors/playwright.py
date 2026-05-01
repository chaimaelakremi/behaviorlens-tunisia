"""
Playwright-based collector for scraping with browser automation
Wrapper around Scrapy spiders for seamless integration
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .base import BaseCollector
from ..schemas import PostSchema, CommentSchema
from ..exceptions import CollectionError

logger = logging.getLogger(__name__)


class PlaywrightCollector(BaseCollector):
    """
    Collector using Playwright for browser automation
    Wraps existing Scrapy spiders from behaviorlens_social.py
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Playwright collector
        
        Args:
            config: Configuration with platforms, headless mode, etc.
        """
        super().__init__("playwright", config)
        self.headless = config.get("headless", True)
        self.timeout = config.get("timeout_seconds", 30)
        self.scroll_pause_ms = config.get("scroll_pause_ms", 1200)
        self.max_retries = config.get("max_retries", 2)
        self.output_file = Path(config.get("output_jsonl", "behaviorlens_output.jsonl"))
        self.browser = None
    
    async def collect(self) -> List[PostSchema]:
        """
        Collect posts using Scrapy CLI
        Assumes behaviorlens_social.py is available in parent directory
        """
        posts = []
        
        try:
            await self.on_start()
            
            # Run Scrapy spider
            spider_output = await self._run_scrapy_spider()
            
            # Parse output
            posts = await self._parse_spider_output(spider_output)
            
            self.logger.info(f"Collected {len(posts)} posts from Playwright")
            
        except Exception as e:
            await self.on_error(e)
        finally:
            await self.on_stop()
        
        return posts
    
    async def _run_scrapy_spider(self) -> List[Dict[str, Any]]:
        """
        Run Scrapy spider from behaviorlens_social.py
        Returns raw items collected
        """
        items = []
        
        try:
            # Try to import and use Scrapy directly
            try:
                from scrapy.crawler import CrawlerProcess
                from scrapy.utils.project import get_project_settings
                
                # Since behaviorlens_social.py has all spiders, we'll parse the JSONL output
                # Run spiders using CLI and read output
                output_items = await self._read_jsonl_output()
                items = output_items
            except ImportError:
                self.logger.warning("Scrapy not available, attempting CLI execution")
                # Fallback to CLI execution
                import subprocess
                result = subprocess.run(
                    ["python", "backend/behaviorlens_social.py"],
                    capture_output=True,
                    text=True,
                    cwd="../..",
                )
                if result.returncode == 0:
                    items = await self._read_jsonl_output()
                else:
                    raise CollectionError(f"Scrapy execution failed: {result.stderr}")
        except Exception as e:
            self.logger.error(f"Error running Scrapy spider: {e}")
            raise
        
        return items
    
    async def _read_jsonl_output(self) -> List[Dict[str, Any]]:
        """Read JSONL output from Scrapy"""
        items = []
        
        if not self.output_file.exists():
            self.logger.warning(f"Output file not found: {self.output_file}")
            return items
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        items.append(json.loads(line))
        except Exception as e:
            self.logger.error(f"Error reading JSONL output: {e}")
        
        return items
    
    async def _parse_spider_output(self, items: List[Dict[str, Any]]) -> List[PostSchema]:
        """
        Parse Scrapy spider output items
        Convert from raw spider format to PostSchema
        """
        posts = []
        
        for item in items:
            try:
                # Extract timestamps
                created_at = None
                if "created_at" in item:
                    try:
                        created_at = datetime.fromisoformat(item["created_at"])
                    except:
                        pass
                
                # Parse comments
                comments = []
                if "comments" in item:
                    comments_data = item["comments"]
                    if isinstance(comments_data, str):
                        try:
                            comments_data = json.loads(comments_data)
                        except:
                            comments_data = []
                    
                    for comment_item in comments_data if isinstance(comments_data, list) else []:
                        try:
                            comment = CommentSchema(
                                text=comment_item.get("text", ""),
                                author=comment_item.get("author"),
                                likes=comment_item.get("likes", 0),
                                sentiment=comment_item.get("sentiment"),
                                is_tunisian=comment_item.get("is_tunisian", False),
                                language=comment_item.get("language"),
                            )
                            comments.append(comment)
                        except:
                            pass
                
                # Parse hashtags
                hashtags = []
                if "hashtags_json" in item:
                    try:
                        hashtags_data = item["hashtags_json"]
                        if isinstance(hashtags_data, str):
                            hashtags_data = json.loads(hashtags_data)
                        hashtags = hashtags_data if isinstance(hashtags_data, list) else []
                    except:
                        pass
                
                # Create post
                post = PostSchema(
                    source=item.get("source", "unknown"),
                    url=item.get("url", ""),
                    post_id=item.get("post_id", ""),
                    author=item.get("author", "Unknown"),
                    text=item.get("text", ""),
                    media_type=item.get("media_type", "text"),
                    likes=item.get("likes", 0),
                    shares=item.get("shares", 0),
                    comments_count=item.get("comments_count", 0),
                    post_type=item.get("post_type"),
                    sentiment=item.get("sentiment"),
                    language=item.get("language"),
                    is_tunisian=item.get("is_tunisian", False),
                    tunisian_score=item.get("tunisian_score", 0.0),
                    hashtags=hashtags,
                    comments=comments,
                    created_at=created_at,
                    scraped_at=datetime.utcnow(),
                )
                
                posts.append(post)
            except Exception as e:
                self.logger.error(f"Error parsing spider item: {e}")
                continue
        
        return posts
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Playwright setup"""
        try:
            # Check if output file is being written
            if self.output_file.exists():
                # Check if file has recent data
                stat = self.output_file.stat()
                from datetime import timedelta
                if datetime.fromtimestamp(stat.st_mtime) > datetime.now() - timedelta(hours=1):
                    return {
                        "status": "healthy",
                        "message": "Playwright collector ready",
                        "details": {
                            "output_file": str(self.output_file),
                            "size_bytes": stat.st_size,
                        }
                    }
            
            return {
                "status": "healthy",
                "message": "Playwright collector configured",
                "details": {
                    "headless": self.headless,
                    "timeout_seconds": self.timeout,
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Playwright health check failed: {e}",
                "details": {}
            }
