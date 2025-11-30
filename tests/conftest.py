"""
Pytest configuration and shared fixtures for raindrop_bookmarks tests.
"""

import pytest
from datetime import datetime, timezone


@pytest.fixture
def sample_access_token() -> str:
    """Provide a sample access token for testing."""
    return "test-access-token-12345"


@pytest.fixture
def sample_bookmark_data() -> dict:
    """Provide sample bookmark data as returned by Raindrop API."""
    return {
        "_id": 123456789,
        "title": "Test Bookmark",
        "link": "https://example.com/article",
        "created": "2025-11-25T10:30:00Z",
        "lastUpdate": "2025-11-25T10:30:00Z",
        "tags": ["test", "python"],
        "collection": {"$id": 12345},
        "excerpt": "This is a test bookmark excerpt",
        "domain": "example.com",
        "cover": "https://example.com/cover.jpg",
        "type": "article",
    }


@pytest.fixture
def sample_api_response(sample_bookmark_data: dict) -> dict:
    """Provide a sample API response with bookmarks."""
    return {
        "result": True,
        "items": [sample_bookmark_data],
        "count": 1,
    }


@pytest.fixture
def empty_api_response() -> dict:
    """Provide an empty API response."""
    return {
        "result": True,
        "items": [],
        "count": 0,
    }


@pytest.fixture
def multi_page_api_response() -> list[dict]:
    """Provide multiple API responses for pagination testing."""
    # First page: 50 items (full page)
    first_page_items = [
        {
            "_id": i,
            "title": f"Bookmark {i}",
            "link": f"https://example.com/article-{i}",
            "created": "2025-11-25T10:30:00Z",
            "tags": [],
            "collection": {"$id": 0},
            "excerpt": "",
            "domain": "example.com",
            "cover": "",
        }
        for i in range(1, 51)
    ]
    
    # Second page: 25 items (partial page - indicates end)
    second_page_items = [
        {
            "_id": i,
            "title": f"Bookmark {i}",
            "link": f"https://example.com/article-{i}",
            "created": "2025-11-25T10:30:00Z",
            "tags": [],
            "collection": {"$id": 0},
            "excerpt": "",
            "domain": "example.com",
            "cover": "",
        }
        for i in range(51, 76)
    ]
    
    return [
        {"result": True, "items": first_page_items, "count": 75},
        {"result": True, "items": second_page_items, "count": 75},
    ]


@pytest.fixture
def auth_error_response() -> dict:
    """Provide an authentication error response."""
    return {
        "result": False,
        "errorMessage": "Invalid access token",
        "error": 401,
    }


@pytest.fixture
def rate_limit_response() -> dict:
    """Provide a rate limit error response."""
    return {
        "result": False,
        "errorMessage": "Rate limit exceeded",
        "error": 429,
    }
