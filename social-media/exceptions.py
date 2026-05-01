"""
Custom exceptions for social media collector
"""


class SocialMediaCollectorError(Exception):
    """Base exception for social media collector"""
    pass


class ConfigurationError(SocialMediaCollectorError):
    """Configuration error"""
    pass


class CollectionError(SocialMediaCollectorError):
    """Error during data collection"""
    pass


class AuthenticationError(SocialMediaCollectorError):
    """Authentication failed (tokens, credentials, etc.)"""
    pass


class RateLimitError(SocialMediaCollectorError):
    """Rate limit exceeded"""
    pass


class StorageError(SocialMediaCollectorError):
    """Storage operation failed"""
    pass


class ValidationError(SocialMediaCollectorError):
    """Data validation failed"""
    pass


class PlatformNotSupportedError(SocialMediaCollectorError):
    """Platform not supported"""
    pass
