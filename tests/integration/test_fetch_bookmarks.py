"""
Integration tests for fetching bookmarks with mocked API responses.

These tests verify the full flow of fetching bookmarks from the API,
including error handling and response parsing.
"""

import pytest
from unittest.mock import MagicMock, patch
import requests

from raindrop_bookmarks.client import RaindropClient, BASE_URL
from raindrop_bookmarks.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    APIError,
    NetworkError,
)
from raindrop_bookmarks.models import BookmarkResponse


class TestFetchBookmarks:
    """Integration tests for the get_bookmarks method."""

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_success(
        self, mock_session_class: MagicMock, sample_api_response: dict
    ) -> None:
        """Verify successful bookmark fetching."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = sample_api_response
        mock_session.get.return_value = mock_response

        # Execute
        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Verify
        assert isinstance(response, BookmarkResponse)
        assert response.count == 1
        assert len(response.bookmarks) == 1
        assert response.bookmarks[0].title == "Test Bookmark"

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_empty_response(
        self, mock_session_class: MagicMock, empty_api_response: dict
    ) -> None:
        """Verify handling of empty response."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = empty_api_response
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        assert response.count == 0
        assert len(response.bookmarks) == 0

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_auth_error(self, mock_session_class: MagicMock) -> None:
        """Verify handling of 401 authentication error."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        
        with pytest.raises(AuthenticationError) as exc_info:
            client.get_bookmarks(days=7)
        
        assert "Invalid or expired access token" in str(exc_info.value)

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_not_found_error(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify handling of 404 not found error."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        
        with pytest.raises(NotFoundError) as exc_info:
            client.get_bookmarks(days=7, collection_id=99999)
        
        assert "not found" in str(exc_info.value).lower()

    @patch("raindrop_bookmarks.client.requests.Session")
    @patch("time.sleep")
    def test_fetch_bookmarks_rate_limit_error(
        self, mock_sleep: MagicMock, mock_session_class: MagicMock
    ) -> None:
        """Verify handling of 429 rate limit error after retries."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token", max_retries=0)  # No retries for this test
        
        with pytest.raises(RateLimitError) as exc_info:
            client.get_bookmarks(days=7)
        
        assert exc_info.value.retry_after == 60

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_network_error(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify handling of network connection errors."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.get.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        client = RaindropClient("test-token")
        
        with pytest.raises(NetworkError) as exc_info:
            client.get_bookmarks(days=7)
        
        assert "Failed to connect" in str(exc_info.value)

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_with_collection_filter(
        self, mock_session_class: MagicMock, sample_api_response: dict
    ) -> None:
        """Verify fetching from a specific collection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = sample_api_response
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, collection_id=12345)

        # Verify the URL includes the collection ID
        call_args = mock_session.get.call_args
        url = call_args[0][0]
        assert "12345" in url

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_fetch_bookmarks_with_nested(
        self, mock_session_class: MagicMock, sample_api_response: dict
    ) -> None:
        """Verify fetching with nested collections."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = sample_api_response
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, include_nested=True)

        # Verify nested parameter is in the request
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params.get("nested") == "true"

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_response_dates(
        self, mock_session_class: MagicMock, sample_api_response: dict
    ) -> None:
        """Verify response includes correct date range."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = sample_api_response
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Verify date range
        from datetime import date, timedelta
        
        today = date.today()
        expected_from = today - timedelta(days=7)
        
        assert response.to_date == today
        assert response.from_date == expected_from
