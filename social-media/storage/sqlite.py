"""
SQLite storage backend implementation
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

from .base import StorageBackend
from ..schemas import PostSchema, CommentSchema

logger = logging.getLogger(__name__)


class SQLiteStorage(StorageBackend):
    """SQLite storage implementation"""
    
    def __init__(self, database_url: str = "sqlite:///behaviorlens.db"):
        """
        Initialize SQLite storage
        
        Args:
            database_url: SQLite database URL (sqlite:///path/to/db.db)
        """
        # Parse URL
        if database_url.startswith("sqlite:///"):
            db_path = database_url.replace("sqlite:///", "")
        else:
            db_path = "behaviorlens.db"
        
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
    
    async def initialize(self):
        """Create database and tables"""
        try:
            # Create directory if needed
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Connect to database
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            
            # Create posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT,
                    author TEXT,
                    text TEXT,
                    media_type TEXT DEFAULT 'text',
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0,
                    comments_count INTEGER DEFAULT 0,
                    
                    -- Classification
                    post_type TEXT,
                    sentiment TEXT,
                    language TEXT,
                    is_tunisian BOOLEAN DEFAULT 0,
                    tunisian_score REAL DEFAULT 0.0,
                    
                    -- Metadata
                    hashtags_json TEXT,
                    mentions_json TEXT,
                    entities_json TEXT,
                    
                    -- Timestamps
                    created_at DATETIME,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    CONSTRAINT unique_post UNIQUE(source, post_id)
                )
            """)
            
            # Create comments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    text TEXT,
                    author TEXT,
                    likes INTEGER DEFAULT 0,
                    
                    -- Classification
                    sentiment TEXT,
                    is_tunisian BOOLEAN DEFAULT 0,
                    language TEXT,
                    
                    -- Metadata
                    hashtags_json TEXT,
                    
                    -- Timestamps
                    created_at DATETIME,
                    scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON posts(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON posts(sentiment)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_language ON posts(language)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tunisian ON posts(is_tunisian)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_at ON posts(scraped_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_id ON posts(post_id)")
            
            self.connection.commit()
            logger.info(f"Initialized SQLite database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    async def save_post(self, post: PostSchema) -> bool:
        """Save single post, returns True if new, False if duplicate"""
        try:
            cursor = self.connection.cursor()
            
            # Prepare data
            hashtags_json = json.dumps(post.hashtags) if post.hashtags else None
            mentions_json = json.dumps(post.mentions) if post.mentions else None
            entities_json = json.dumps(post.entities) if post.entities else None
            
            cursor.execute("""
                INSERT OR IGNORE INTO posts 
                (post_id, source, url, author, text, media_type, likes, shares, 
                 comments_count, post_type, sentiment, language, is_tunisian, 
                 tunisian_score, hashtags_json, mentions_json, entities_json, 
                 created_at, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.post_id, post.source, post.url, post.author, post.text,
                post.media_type, post.likes, post.shares, post.comments_count,
                post.post_type, post.sentiment, post.language, int(post.is_tunisian),
                post.tunisian_score, hashtags_json, mentions_json, entities_json,
                post.created_at, post.scraped_at
            ))
            
            # Save comments
            for comment in post.comments:
                await self.save_comment(post.post_id, comment)
            
            self.connection.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            logger.debug(f"Post already exists: {post.post_id}")
            return False
        except Exception as e:
            logger.error(f"Error saving post: {e}")
            raise
    
    async def save_posts(self, posts: List[PostSchema]) -> int:
        """Save multiple posts"""
        count = 0
        for post in posts:
            if await self.save_post(post):
                count += 1
        return count
    
    async def get_posts(self, filters: Dict[str, Any] = None, 
                       limit: int = 50, offset: int = 0) -> List[PostSchema]:
        """Retrieve posts with filters"""
        if filters is None:
            filters = {}
        
        try:
            cursor = self.connection.cursor()
            
            # Build query
            query = "SELECT * FROM posts WHERE 1=1"
            params = []
            
            if "source" in filters:
                query += " AND source = ?"
                params.append(filters["source"])
            
            if "sentiment" in filters:
                query += " AND sentiment = ?"
                params.append(filters["sentiment"])
            
            if "language" in filters:
                query += " AND language = ?"
                params.append(filters["language"])
            
            if "post_type" in filters:
                query += " AND post_type = ?"
                params.append(filters["post_type"])
            
            if filters.get("is_tunisian"):
                query += " AND is_tunisian = 1"
            
            if "date_from" in filters:
                query += " AND scraped_at >= ?"
                params.append(filters["date_from"])
            
            if "date_to" in filters:
                query += " AND scraped_at <= ?"
                params.append(filters["date_to"])
            
            # Add pagination
            query += " ORDER BY scraped_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            posts = []
            for row in rows:
                post = self._row_to_post(row)
                posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error retrieving posts: {e}")
            return []
    
    async def get_post(self, post_id: str) -> Optional[PostSchema]:
        """Get single post by ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM posts WHERE post_id = ?", (post_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_post(row)
            return None
        except Exception as e:
            logger.error(f"Error retrieving post: {e}")
            return None
    
    async def save_comment(self, post_id: str, comment: CommentSchema) -> bool:
        """Save comment"""
        try:
            cursor = self.connection.cursor()
            hashtags_json = json.dumps(comment.hashtags) if comment.hashtags else None
            
            cursor.execute("""
                INSERT INTO comments 
                (post_id, text, author, likes, sentiment, is_tunisian, 
                 language, hashtags_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_id, comment.text, comment.author, comment.likes,
                comment.sentiment, int(comment.is_tunisian),
                comment.language, hashtags_json, comment.created_at
            ))
            
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving comment: {e}")
            return False
    
    async def get_comments(self, post_id: str) -> List[CommentSchema]:
        """Get comments for post"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM comments WHERE post_id = ? 
                ORDER BY created_at DESC
            """, (post_id,))
            rows = cursor.fetchall()
            
            comments = []
            for row in rows:
                hashtags = json.loads(row["hashtags_json"]) if row["hashtags_json"] else []
                comment = CommentSchema(
                    text=row["text"],
                    author=row["author"],
                    likes=row["likes"],
                    sentiment=row["sentiment"],
                    is_tunisian=bool(row["is_tunisian"]),
                    language=row["language"],
                    hashtags=hashtags,
                    created_at=row["created_at"],
                )
                comments.append(comment)
            
            return comments
        except Exception as e:
            logger.error(f"Error retrieving comments: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        try:
            cursor = self.connection.cursor()
            
            # Total posts
            cursor.execute("SELECT COUNT(*) as count FROM posts")
            total_posts = cursor.fetchone()["count"]
            
            # Total comments
            cursor.execute("SELECT COUNT(*) as count FROM comments")
            total_comments = cursor.fetchone()["count"]
            
            # By source
            cursor.execute("""
                SELECT source, COUNT(*) as count FROM posts 
                GROUP BY source
            """)
            posts_by_source = {row["source"]: row["count"] for row in cursor.fetchall()}
            
            # By sentiment
            cursor.execute("""
                SELECT sentiment, COUNT(*) as count FROM posts 
                WHERE sentiment IS NOT NULL
                GROUP BY sentiment
            """)
            posts_by_sentiment = {row["sentiment"]: row["count"] for row in cursor.fetchall()}
            
            # By type
            cursor.execute("""
                SELECT post_type, COUNT(*) as count FROM posts 
                WHERE post_type IS NOT NULL
                GROUP BY post_type
            """)
            posts_by_type = {row["post_type"]: row["count"] for row in cursor.fetchall()}
            
            # By language
            cursor.execute("""
                SELECT language, COUNT(*) as count FROM posts 
                WHERE language IS NOT NULL
                GROUP BY language
            """)
            posts_by_language = {row["language"]: row["count"] for row in cursor.fetchall()}
            
            # Tunisian posts
            cursor.execute("SELECT COUNT(*) as count FROM posts WHERE is_tunisian = 1")
            tunisian_posts = cursor.fetchone()["count"]
            
            # Posts in last 24 hours
            yesterday = datetime.utcnow() - timedelta(hours=24)
            cursor.execute(
                "SELECT COUNT(*) as count FROM posts WHERE scraped_at > ?",
                (yesterday,)
            )
            posts_last_24h = cursor.fetchone()["count"]
            
            return {
                "total_posts": total_posts,
                "total_comments": total_comments,
                "posts_by_source": posts_by_source,
                "posts_by_sentiment": posts_by_sentiment,
                "posts_by_type": posts_by_type,
                "posts_by_language": posts_by_language,
                "tunisian_posts": tunisian_posts,
                "posts_last_24h": posts_last_24h,
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    async def delete_old_posts(self, days: int):
        """Delete posts older than specified days"""
        try:
            cursor = self.connection.cursor()
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            cursor.execute(
                "DELETE FROM posts WHERE scraped_at < ?",
                (cutoff_date,)
            )
            
            self.connection.commit()
            logger.info(f"Deleted {cursor.rowcount} posts older than {days} days")
        except Exception as e:
            logger.error(f"Error deleting old posts: {e}")
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Closed database connection")
    
    def _row_to_post(self, row) -> PostSchema:
        """Convert database row to PostSchema"""
        hashtags = json.loads(row["hashtags_json"]) if row["hashtags_json"] else []
        mentions = json.loads(row["mentions_json"]) if row["mentions_json"] else []
        entities = json.loads(row["entities_json"]) if row["entities_json"] else {}
        
        return PostSchema(
            source=row["source"],
            url=row["url"],
            post_id=row["post_id"],
            author=row["author"],
            text=row["text"],
            media_type=row["media_type"],
            likes=row["likes"],
            shares=row["shares"],
            comments_count=row["comments_count"],
            post_type=row["post_type"],
            sentiment=row["sentiment"],
            language=row["language"],
            is_tunisian=bool(row["is_tunisian"]),
            tunisian_score=row["tunisian_score"],
            hashtags=hashtags,
            mentions=mentions,
            entities=entities,
            created_at=row["created_at"],
            scraped_at=row["scraped_at"],
        )
