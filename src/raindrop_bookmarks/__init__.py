"""
Raindrop Bookmarks - Python library for fetching Raindrop.io bookmarks from the last N days.

This library provides a simple interface to the Raindrop.io API for retrieving
bookmarks created within a specified date range.
"""

from .client import RaindropClient
from .models import Bookmark, BookmarkRequest, BookmarkResponse
from .exceptions import (
    RaindropError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    NetworkError,
    APIError,
)

__version__ = "1.0.0"

__all__ = [
    "RaindropClient",
    "Bookmark",
    "BookmarkRequest",
    "BookmarkResponse",
    "RaindropError",
    "AuthenticationError",
    "RateLimitError",
    "ValidationError",
    "NotFoundError",
    "NetworkError",
    "APIError",
]
