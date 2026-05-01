"""
Hybrid collector - intelligently routes between Graph API and Playwright
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base import BaseCollector
from .graph_api import GraphAPICollector
from .rss import RSSCollector
from .playwright import PlaywrightCollector
from ..schemas import PostSchema
from ..config import get_settings

logger = logging.getLogger(__name__)


class HybridCollector:
    """
    Main orchestrator that manages multiple collectors
    Strategy: Graph API first (faster, more reliable) → Playwright fallback (comprehensive)
    """
    
    def __init__(self):
        """Initialize hybrid collector with all sub-collectors"""
        self.settings = get_settings()
        self.collectors: Dict[str, BaseCollector] = {}
        self._setup_collectors()
    
    def _setup_collectors(self):
        """Setup all available collectors based on settings"""
        
        # Facebook Graph API
        if self.settings.facebook_graph.enabled and self.settings.facebook_graph.access_token:
            try:
                fb_collector = GraphAPICollector(
                    platform="facebook",
                    access_token=self.settings.facebook_graph.access_token,
                    accounts=self.settings.facebook_graph.page_ids,
                    config={
                        "enabled": True,
                        "include_comments": self.settings.include_comments,
                        "max_retries": self.settings.facebook_graph.max_retries,
                        "timeout_seconds": self.settings.facebook_graph.timeout_seconds,
                    }
                )
                self.collectors["facebook"] = fb_collector
                logger.info("Facebook Graph API collector enabled")
            except Exception as e:
                logger.warning(f"Failed to setup Facebook collector: {e}")
        
        # Instagram Graph API
        if self.settings.instagram_graph.enabled and self.settings.instagram_graph.access_token:
            try:
                ig_collector = GraphAPICollector(
                    platform="instagram",
                    access_token=self.settings.instagram_graph.access_token,
                    accounts=self.settings.instagram_graph.business_account_ids,
                    config={
                        "enabled": True,
                        "include_comments": self.settings.include_comments,
                        "max_retries": self.settings.instagram_graph.max_retries,
                        "timeout_seconds": self.settings.instagram_graph.timeout_seconds,
                    }
                )
                self.collectors["instagram"] = ig_collector
                logger.info("Instagram Graph API collector enabled")
            except Exception as e:
                logger.warning(f"Failed to setup Instagram collector: {e}")
        
        # Playwright (browser automation)
        if self.settings.playwright.enabled:
            try:
                pw_collector = PlaywrightCollector(
                    config={
                        "enabled": True,
                        "headless": self.settings.playwright.headless,
                        "timeout_seconds": self.settings.playwright.timeout_seconds,
                        "scroll_pause_ms": self.settings.playwright.scroll_pause_ms,
                        "max_retries": self.settings.playwright.max_retries,
                    }
                )
                self.collectors["playwright"] = pw_collector
                logger.info("Playwright collector enabled")
            except Exception as e:
                logger.warning(f"Failed to setup Playwright collector: {e}")
        
        # RSS feeds
        if self.settings.rss.enabled and self.settings.rss.feeds:
            try:
                rss_collector = RSSCollector(
                    feeds=self.settings.rss.feeds,
                    config={
                        "enabled": True,
                        "timeout_seconds": self.settings.rss.timeout_seconds,
                    }
                )
                self.collectors["rss"] = rss_collector
                logger.info("RSS collector enabled")
            except Exception as e:
                logger.warning(f"Failed to setup RSS collector: {e}")
    
    async def collect(self, platforms: Optional[List[str]] = None, 
                     max_total: Optional[int] = None) -> List[PostSchema]:
        """
        Collect posts from enabled collectors
        
        Args:
            platforms: Specific platforms to collect from (None = all)
            max_total: Maximum total posts to collect across all platforms
            
        Returns:
            List of collected posts
        """
        all_posts = []
        
        # Determine which collectors to use
        collectors_to_run = {}
        if platforms:
            for platform in platforms:
                if platform in self.collectors:
                    collectors_to_run[platform] = self.collectors[platform]
                else:
                    logger.warning(f"Platform {platform} not available")
        else:
            collectors_to_run = self.collectors
        
        if not collectors_to_run:
            logger.error("No collectors available to run")
            return []
        
        # Run collectors in parallel
        try:
            tasks = [
                self._run_collector_safe(name, collector)
                for name, collector in collectors_to_run.items()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Collector error: {result}")
                elif isinstance(result, list):
                    all_posts.extend(result)
        except Exception as e:
            logger.error(f"Error running collectors: {e}")
        
        # Limit total posts if specified
        if max_total and len(all_posts) > max_total:
            all_posts = all_posts[:max_total]
        
        logger.info(f"Collection complete: {len(all_posts)} posts collected")
        return all_posts
    
    async def _run_collector_safe(self, name: str, collector: BaseCollector) -> List[PostSchema]:
        """
        Run a collector with error handling
        
        Args:
            name: Collector name
            collector: Collector instance
            
        Returns:
            List of posts from collector
        """
        try:
            logger.info(f"Starting collection from {name}")
            posts = await collector.collect()
            logger.info(f"Completed collection from {name}: {len(posts)} posts")
            return posts
        except Exception as e:
            logger.error(f"Collector {name} failed: {e}", exc_info=True)
            return []
    
    async def get_platform_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all collectors"""
        stats = {}
        
        tasks = [
            (name, collector.health_check())
            for name, collector in self.collectors.items()
        ]
        
        for name, task in tasks:
            try:
                health = await task
                stats[name] = health
            except Exception as e:
                stats[name] = {
                    "status": "error",
                    "message": str(e),
                    "details": {}
                }
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Overall health check"""
        stats = await self.get_platform_stats()
        
        healthy_count = sum(1 for s in stats.values() if s.get("status") == "healthy")
        total_count = len(stats)
        
        if total_count == 0:
            status = "error"
            message = "No collectors configured"
        elif healthy_count == total_count:
            status = "healthy"
            message = f"All {total_count} collectors healthy"
        elif healthy_count > 0:
            status = "degraded"
            message = f"{healthy_count}/{total_count} collectors healthy"
        else:
            status = "error"
            message = f"All {total_count} collectors unhealthy"
        
        return {
            "status": status,
            "message": message,
            "collectors": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }
