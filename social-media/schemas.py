"""
Pydantic schemas for social media posts and comments
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CommentSchema(BaseModel):
    """Comment schema"""
    text: str
    author: Optional[str] = None
    likes: int = 0
    sentiment: Optional[str] = None
    is_tunisian: bool = False
    language: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostSchema(BaseModel):
    """Post schema with all metadata"""
    source: str  # facebook, instagram, tiktok, etc.
    url: str
    post_id: str
    author: str
    text: str
    media_type: str = "text"  # text, image, video, reel
    likes: int = 0
    shares: int = 0
    comments_count: int = 0
    
    # Classification
    post_type: Optional[str] = None  # complaint, opinion, news, humor, etc.
    sentiment: Optional[str] = None  # positive, negative, neutral
    language: Optional[str] = None  # arabic, french, tunisian_dialect, mixed
    is_tunisian: bool = False
    tunisian_score: float = 0.0  # 0-1 confidence
    
    # Metadata
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)
    
    # Comments
    comments: List[CommentSchema] = Field(default_factory=list)
    
    # Timestamps
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CollectionStatsSchema(BaseModel):
    """Statistics from collection run"""
    total_posts: int
    total_comments: int
    posts_by_source: Dict[str, int]
    posts_by_sentiment: Dict[str, int]
    posts_by_type: Dict[str, int]
    tunisian_posts: int
    avg_tunisian_score: float
    collection_duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CollectorHealthSchema(BaseModel):
    """Health check response from collector"""
    status: str  # "healthy", "degraded", "error"
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
