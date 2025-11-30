"""
Raindrop.io API client for fetching bookmarks by date.

This module provides the RaindropClient class, which handles authentication,
API requests, pagination, and error handling for the Raindrop.io API.
"""

import logging
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

import requests

from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .models import Bookmark, BookmarkResponse

logger = logging.getLogger(__name__)

# API constants
BASE_URL = "https://api.raindrop.io/rest/v1"
MAX_PER_PAGE = 50
DEFAULT_SORT = "-created"

# Retry constants
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0  # seconds
BACKOFF_MULTIPLIER = 2.0

# Collection ID constants
COLLECTION_ALL = 0
COLLECTION_UNSORTED = -1
COLLECTION_TRASH = -99


class RaindropClient:
    """
    Client for fetching bookmarks from the Raindrop.io API.

    This client provides methods to fetch bookmarks created within a specified
    number of days, with support for pagination, collection filtering, and
    comprehensive error handling.

    Attributes:
        access_token: OAuth Bearer token for Raindrop.io API.
        base_url: Base URL for the API (defaults to production).
        page_delay: Optional delay between pagination requests (in seconds).

    Example:
        >>> client = RaindropClient("your-access-token")
        >>> response = client.get_bookmarks(days=7)
        >>> for bookmark in response.bookmarks:
        ...     print(bookmark.title)
    """

    def __init__(
        self,
        access_token: str,
        base_url: str = BASE_URL,
        page_delay: float = 0.0,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """
        Initialize the RaindropClient.

        Args:
            access_token: OAuth Bearer token for Raindrop.io API.
            base_url: Base URL for the API (defaults to production).
            page_delay: Delay in seconds between pagination requests.
            max_retries: Maximum number of retries for rate limit errors.

        Raises:
            ValidationError: If access_token is empty.
        """
        if not access_token or not access_token.strip():
            raise ValidationError("Access token is required")
        
        self.access_token = access_token.strip()
        self.base_url = base_url.rstrip("/")
        self.page_delay = page_delay
        self.max_retries = max_retries
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        })

    def _calculate_from_date(self, days: int) -> str:
        """
        Calculate the date N days ago in YYYY-MM-DD format.

        Args:
            days: Number of days to look back.

        Returns:
            Date string in YYYY-MM-DD format.
        """
        from_date = datetime.now(timezone.utc).date() - timedelta(days=days)
        return from_date.strftime("%Y-%m-%d")

    def _build_request_params(
        self,
        search: str,
        sort: str = DEFAULT_SORT,
        perpage: int = MAX_PER_PAGE,
        page: int = 0,
        nested: bool = False,
    ) -> dict[str, Any]:
        """
        Build query parameters for the API request.

        Args:
            search: Search query (e.g., "created:>2025-11-23").
            sort: Sort order (e.g., "-created" for newest first).
            perpage: Number of items per page (max 50).
            page: Page number (0-indexed).
            nested: Whether to include nested collections.

        Returns:
            Dictionary of query parameters.
        """
        params: dict[str, Any] = {
            "search": search,
            "sort": sort,
            "perpage": min(perpage, MAX_PER_PAGE),
            "page": page,
        }
        if nested:
            params["nested"] = "true"
        return params

    def _parse_raindrop_item(self, item: dict[str, Any]) -> Bookmark:
        """
        Parse a raw API response item into a Bookmark model.

        Args:
            item: Dictionary from API response.

        Returns:
            Bookmark instance with parsed data.
        """
        # Parse created datetime
        created_str = item.get("created", "")
        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            created = datetime.now(timezone.utc)

        # Extract collection ID from nested object
        collection = item.get("collection", {})
        collection_id: Optional[int] = None
        if isinstance(collection, dict):
            collection_id = collection.get("$id")

        return Bookmark(
            id=item.get("_id", 0),
            title=item.get("title", ""),
            link=item.get("link", ""),
            created=created,
            tags=item.get("tags", []),
            collection_id=collection_id,
            excerpt=item.get("excerpt"),
            domain=item.get("domain"),
            cover=item.get("cover"),
        )

    def _handle_response_error(self, response: requests.Response) -> None:
        """
        Handle HTTP error responses and raise appropriate exceptions.

        Args:
            response: HTTP response object.

        Raises:
            AuthenticationError: For 401 responses.
            NotFoundError: For 404 responses.
            RateLimitError: For 429 responses.
            APIError: For other error responses.
        """
        status_code = response.status_code

        if status_code == 401:
            raise AuthenticationError("Invalid or expired access token")
        elif status_code == 404:
            raise NotFoundError("Collection not found")
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after else None
            raise RateLimitError(
                "API rate limit exceeded (120 requests/minute)",
                retry_after=retry_seconds,
            )
        else:
            try:
                error_data = response.json()
                message = error_data.get("errorMessage", f"API error: {status_code}")
            except (ValueError, KeyError):
                message = f"API error: {status_code}"
            raise APIError(message, status_code=status_code)

    def _fetch_page(
        self,
        collection_id: int,
        search: str,
        page: int,
        nested: bool = False,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Fetch a single page of bookmarks from the API.

        Args:
            collection_id: Collection ID to fetch from.
            search: Search query string.
            page: Page number (0-indexed).
            nested: Whether to include nested collections.

        Returns:
            Tuple of (items list, total count).

        Raises:
            NetworkError: If connection fails.
            AuthenticationError: If token is invalid.
            NotFoundError: If collection doesn't exist.
            RateLimitError: If rate limit exceeded after all retries.
            APIError: For other API errors.
        """
        url = f"{self.base_url}/raindrops/{collection_id}"
        params = self._build_request_params(
            search=search,
            page=page,
            nested=nested,
        )

        logger.debug(f"Fetching page {page} from collection {collection_id}")

        last_error: Optional[RateLimitError] = None
        backoff = INITIAL_BACKOFF

        for attempt in range(self.max_retries + 1):
            try:
                response = self._session.get(url, params=params)
            except requests.exceptions.ConnectionError as e:
                raise NetworkError(f"Failed to connect to API: {e}")
            except requests.exceptions.Timeout as e:
                raise NetworkError(f"Request timed out: {e}")
            except requests.exceptions.RequestException as e:
                raise NetworkError(f"Request failed: {e}")

            if response.status_code == 429:
                # Rate limit - retry with exponential backoff
                retry_after = response.headers.get("Retry-After")
                retry_seconds = int(retry_after) if retry_after else None
                
                if attempt < self.max_retries:
                    wait_time = retry_seconds if retry_seconds else backoff
                    logger.warning(
                        f"Rate limit exceeded, retrying in {wait_time}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(wait_time)
                    backoff *= BACKOFF_MULTIPLIER
                    last_error = RateLimitError(
                        "API rate limit exceeded (120 requests/minute)",
                        retry_after=retry_seconds,
                    )
                    continue
                else:
                    raise RateLimitError(
                        "API rate limit exceeded after retries",
                        retry_after=retry_seconds,
                    )

            if not response.ok:
                self._handle_response_error(response)

            try:
                data = response.json()
            except ValueError:
                raise APIError("Invalid JSON response from API")

            if not data.get("result", False):
                error_msg = data.get("errorMessage", "Unknown API error")
                raise APIError(error_msg)

            items = data.get("items", [])
            count = data.get("count", 0)

            logger.debug(f"Fetched {len(items)} items (total: {count})")

            return items, count

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise APIError("Unexpected error in fetch loop")

    def _validate_days(self, days: int) -> None:
        """
        Validate the days parameter.

        Args:
            days: Number of days to look back.

        Raises:
            ValidationError: If days is not a positive integer.
        """
        if not isinstance(days, int) or days <= 0:
            raise ValidationError("Days must be a positive integer")

    def _validate_collection_id(self, collection_id: int) -> None:
        """
        Validate the collection ID parameter.

        Args:
            collection_id: Collection ID to validate.

        Raises:
            ValidationError: If collection_id is invalid.
        """
        valid_special = {COLLECTION_ALL, COLLECTION_UNSORTED, COLLECTION_TRASH}
        if collection_id not in valid_special and collection_id < 0:
            raise ValidationError(
                f"Invalid collection_id: {collection_id}. "
                f"Use 0 (all), -1 (unsorted), -99 (trash), or a positive integer."
            )

    def get_bookmarks(
        self,
        days: int,
        collection_id: int = COLLECTION_ALL,
        include_nested: bool = False,
    ) -> BookmarkResponse:
        """
        Get all bookmarks created in the last N days.

        This method fetches all matching bookmarks, automatically handling
        pagination to retrieve results beyond the 50-item page limit.

        Args:
            days: Number of days to look back (must be positive).
            collection_id: Collection to filter (0=all, -1=unsorted, -99=trash,
                or a positive integer for specific collection).
            include_nested: Whether to include bookmarks from nested collections.

        Returns:
            BookmarkResponse with list of bookmarks and metadata.

        Raises:
            ValidationError: If parameters are invalid.
            AuthenticationError: If token is invalid.
            NotFoundError: If collection doesn't exist.
            RateLimitError: If rate limit exceeded.
            NetworkError: If connection fails.
            APIError: For other API errors.

        Example:
            >>> client = RaindropClient("your-token")
            >>> response = client.get_bookmarks(days=7)
            >>> print(f"Found {response.count} bookmarks")
            >>> for bm in response.bookmarks:
            ...     print(f"  - {bm.title}")
        """
        # Validate inputs
        self._validate_days(days)
        self._validate_collection_id(collection_id)

        # Calculate date range
        from_date_str = self._calculate_from_date(days)
        search_query = f"created:>{from_date_str}"
        
        today = datetime.now(timezone.utc).date()
        from_date = today - timedelta(days=days)

        # Fetch all pages
        all_bookmarks: list[Bookmark] = []
        page = 0

        while True:
            items, total_count = self._fetch_page(
                collection_id=collection_id,
                search=search_query,
                page=page,
                nested=include_nested,
            )

            # Parse items into Bookmark objects
            for item in items:
                bookmark = self._parse_raindrop_item(item)
                all_bookmarks.append(bookmark)

            # Check if we've fetched all items
            if len(items) < MAX_PER_PAGE:
                break

            page += 1
            logger.info(f"Pagination: fetched page {page}, total so far: {len(all_bookmarks)}")

            # Optional delay between pagination requests
            if self.page_delay > 0:
                time.sleep(self.page_delay)

        logger.info(f"Completed fetching {len(all_bookmarks)} bookmarks")

        return BookmarkResponse(
            bookmarks=all_bookmarks,
            count=len(all_bookmarks),
            from_date=from_date,
            to_date=today,
        )
