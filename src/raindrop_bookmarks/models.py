"""
Data models for the Raindrop Bookmarks library.

These models represent the core data structures used throughout the library:
- Bookmark: A saved bookmark from Raindrop.io
- BookmarkRequest: Parameters for fetching bookmarks
- BookmarkResponse: Response wrapper with bookmarks and metadata
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Bookmark:
    """
    Represents a saved bookmark (called "Raindrop" in the API).

    Attributes:
        id: Unique identifier from Raindrop API.
        title: Bookmark title.
        link: The bookmarked URL.
        created: When the bookmark was created/saved.
        tags: User-assigned tags, empty list if none.
        collection_id: ID of the parent collection (None for unsorted).
        excerpt: Description or excerpt from the page.
        domain: Domain of the bookmarked URL.
        cover: Cover image URL if available.
    """

    id: int
    title: str
    link: str
    created: datetime
    tags: list[str] = field(default_factory=list)
    collection_id: Optional[int] = None
    excerpt: Optional[str] = None
    domain: Optional[str] = None
    cover: Optional[str] = None


@dataclass
class BookmarkRequest:
    """
    Parameters for fetching bookmarks from the Raindrop API.

    Attributes:
        days: Number of days to look back (must be positive).
        collection_id: Collection to filter (0 = all, -1 = unsorted, -99 = trash).
        include_nested: Whether to include bookmarks from nested collections.
    """

    days: int
    collection_id: int = 0
    include_nested: bool = False


@dataclass
class BookmarkResponse:
    """
    Response wrapper for bookmark queries.

    Attributes:
        bookmarks: List of matching bookmarks.
        count: Total number of bookmarks returned.
        from_date: Start of date range (today - N days).
        to_date: End of date range (today).
    """

    bookmarks: list[Bookmark]
    count: int
    from_date: date
    to_date: date
