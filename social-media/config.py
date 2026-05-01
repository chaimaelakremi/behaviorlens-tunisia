"""
Configuration for social media collector using Pydantic v2
Environment variables: BEHAVIORLENS_*
"""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import logging

logger = logging.getLogger(__name__)


class FacebookGraphSettings(BaseSettings):
    """Facebook Graph API settings"""
    enabled: bool = False
    access_token: Optional[str] = None
    page_ids: List[str] = Field(default_factory=list)
    include_comments: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    
    class Config:
        env_prefix = "BEHAVIORLENS_FACEBOOK_"
    
    @field_validator('page_ids')
    @classmethod
    def validate_page_ids(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v


class InstagramGraphSettings(BaseSettings):
    """Instagram Graph API settings"""
    enabled: bool = False
    access_token: Optional[str] = None
    business_account_ids: List[str] = Field(default_factory=list)
    include_comments: bool = True
    max_retries: int = 3
    timeout_seconds: int = 30
    
    class Config:
        env_prefix = "BEHAVIORLENS_INSTAGRAM_"
    
    @field_validator('business_account_ids')
    @classmethod
    def validate_account_ids(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v


class PlaywrightSettings(BaseSettings):
    """Playwright scraping settings"""
    enabled: bool = True
    headless: bool = True
    timeout_seconds: int = 30
    scroll_pause_ms: int = 1200
    max_retries: int = 2
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    
    class Config:
        env_prefix = "BEHAVIORLENS_PLAYWRIGHT_"


class RSSSettings(BaseSettings):
    """RSS feed collection settings"""
    enabled: bool = True
    feeds: List[str] = Field(default_factory=list)
    timeout_seconds: int = 15
    
    class Config:
        env_prefix = "BEHAVIORLENS_RSS_"


class StorageSettings(BaseSettings):
    """Storage settings"""
    database_url: str = Field(
        default="sqlite:///behaviorlens.db",
        description="Database URL (sqlite:/// or postgresql://...)"
    )
    output_jsonl: str = Field(default="behaviorlens_output.jsonl")
    batch_size: int = 50
    
    class Config:
        env_prefix = "BEHAVIORLENS_STORAGE_"


class ClassificationSettings(BaseSettings):
    """Classification settings"""
    detect_post_type: bool = True
    detect_sentiment: bool = True
    detect_language: bool = True
    detect_tunisian: bool = True
    min_text_length: int = 10
    
    class Config:
        env_prefix = "BEHAVIORLENS_CLASSIFICATION_"


class Settings(BaseSettings):
    """Main settings class"""
    # General
    log_level: str = "INFO"
    debug: bool = False
    
    # Platform settings
    facebook_graph: FacebookGraphSettings = Field(default_factory=FacebookGraphSettings)
    instagram_graph: InstagramGraphSettings = Field(default_factory=InstagramGraphSettings)
    playwright: PlaywrightSettings = Field(default_factory=PlaywrightSettings)
    rss: RSSSettings = Field(default_factory=RSSSettings)
    
    # Storage
    storage: StorageSettings = Field(default_factory=StorageSettings)
    
    # Classification
    classification: ClassificationSettings = Field(default_factory=ClassificationSettings)
    
    # Collection behavior
    collection_interval_minutes: int = 60
    max_posts_per_run: int = 1000
    include_comments: bool = True
    
    class Config:
        env_prefix = "BEHAVIORLENS_"
        case_sensitive = False
        env_file = ".env"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
        logger.info(f"Loaded settings: log_level={_settings.log_level}")
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment"""
    global _settings
    _settings = Settings()
    logger.info("Settings reloaded")
    return _settings
