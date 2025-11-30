"""
Unit tests for collection ID parameter handling.

These tests verify the collection filtering functionality.
"""

import pytest
from unittest.mock import MagicMock, patch

from raindrop_bookmarks.client import (
    RaindropClient,
    COLLECTION_ALL,
    COLLECTION_UNSORTED,
    COLLECTION_TRASH,
)
from raindrop_bookmarks.exceptions import ValidationError


class TestCollectionFilter:
    """Tests for collection filtering functionality."""

    def test_collection_constants(self) -> None:
        """Verify collection ID constants are defined correctly."""
        assert COLLECTION_ALL == 0
        assert COLLECTION_UNSORTED == -1
        assert COLLECTION_TRASH == -99

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_default_collection_is_all(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify default collection is COLLECTION_ALL (0)."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": True, "items": [], "count": 0}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        client.get_bookmarks(days=7)

        # Verify URL uses collection ID 0
        call_args = mock_session.get.call_args
        url = call_args[0][0]
        assert "/raindrops/0" in url

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_unsorted_collection(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify fetching from unsorted collection (-1)."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": True, "items": [], "count": 0}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        client.get_bookmarks(days=7, collection_id=COLLECTION_UNSORTED)

        call_args = mock_session.get.call_args
        url = call_args[0][0]
        assert "/raindrops/-1" in url

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_trash_collection(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify fetching from trash collection (-99)."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": True, "items": [], "count": 0}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        client.get_bookmarks(days=7, collection_id=COLLECTION_TRASH)

        call_args = mock_session.get.call_args
        url = call_args[0][0]
        assert "/raindrops/-99" in url

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_specific_collection(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify fetching from a specific user collection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": True, "items": [], "count": 0}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        client.get_bookmarks(days=7, collection_id=12345)

        call_args = mock_session.get.call_args
        url = call_args[0][0]
        assert "/raindrops/12345" in url

    def test_invalid_collection_id_negative(self) -> None:
        """Verify invalid negative collection ID raises error."""
        client = RaindropClient("test-token")
        
        with pytest.raises(ValidationError) as exc_info:
            client._validate_collection_id(-50)
        
        assert "Invalid collection_id" in str(exc_info.value)

    def test_invalid_collection_id_values(self) -> None:
        """Verify various invalid collection IDs raise errors."""
        client = RaindropClient("test-token")
        
        invalid_ids = [-2, -98, -100, -1000]
        for cid in invalid_ids:
            with pytest.raises(ValidationError):
                client._validate_collection_id(cid)

    def test_valid_collection_ids(self) -> None:
        """Verify all valid collection IDs pass validation."""
        client = RaindropClient("test-token")
        
        # Special IDs
        client._validate_collection_id(0)
        client._validate_collection_id(-1)
        client._validate_collection_id(-99)
        
        # Positive IDs
        client._validate_collection_id(1)
        client._validate_collection_id(12345)
        client._validate_collection_id(999999999)
