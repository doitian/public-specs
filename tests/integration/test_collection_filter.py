"""
Integration tests for collection filtering with mocked API responses.

These tests verify the complete flow of filtering bookmarks by collection.
"""

import pytest
from unittest.mock import MagicMock, patch

from raindrop_bookmarks.client import (
    RaindropClient,
    COLLECTION_ALL,
    COLLECTION_UNSORTED,
    COLLECTION_TRASH,
)


class TestCollectionFilterIntegration:
    """Integration tests for collection filtering."""

    @pytest.fixture
    def mock_bookmarks_in_collection(self) -> list[dict]:
        """Sample bookmarks that belong to a specific collection."""
        return [
            {
                "_id": 1,
                "title": "Bookmark in Collection",
                "link": "https://example.com/1",
                "created": "2025-11-25T10:00:00Z",
                "tags": ["work"],
                "collection": {"$id": 12345},
            },
            {
                "_id": 2,
                "title": "Another in Collection",
                "link": "https://example.com/2",
                "created": "2025-11-26T10:00:00Z",
                "tags": [],
                "collection": {"$id": 12345},
            },
        ]

    @pytest.fixture
    def mock_unsorted_bookmarks(self) -> list[dict]:
        """Sample unsorted bookmarks."""
        return [
            {
                "_id": 100,
                "title": "Unsorted Bookmark",
                "link": "https://example.com/unsorted",
                "created": "2025-11-27T10:00:00Z",
                "tags": [],
                "collection": {"$id": -1},
            },
        ]

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_filter_by_specific_collection(
        self,
        mock_session_class: MagicMock,
        mock_bookmarks_in_collection: list[dict],
    ) -> None:
        """Verify filtering returns only bookmarks from specified collection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "result": True,
            "items": mock_bookmarks_in_collection,
            "count": 2,
        }
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, collection_id=12345)

        # Verify all returned bookmarks are from the correct collection
        assert response.count == 2
        for bookmark in response.bookmarks:
            assert bookmark.collection_id == 12345

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_filter_by_unsorted(
        self,
        mock_session_class: MagicMock,
        mock_unsorted_bookmarks: list[dict],
    ) -> None:
        """Verify filtering by unsorted collection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "result": True,
            "items": mock_unsorted_bookmarks,
            "count": 1,
        }
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, collection_id=COLLECTION_UNSORTED)

        assert response.count == 1
        assert response.bookmarks[0].collection_id == -1

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_filter_all_collections(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify fetching from all collections includes multiple."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mix of bookmarks from different collections
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "result": True,
            "items": [
                {
                    "_id": 1,
                    "title": "From Collection A",
                    "link": "https://example.com/1",
                    "created": "2025-11-25T10:00:00Z",
                    "collection": {"$id": 111},
                },
                {
                    "_id": 2,
                    "title": "From Collection B",
                    "link": "https://example.com/2",
                    "created": "2025-11-26T10:00:00Z",
                    "collection": {"$id": 222},
                },
                {
                    "_id": 3,
                    "title": "Unsorted",
                    "link": "https://example.com/3",
                    "created": "2025-11-27T10:00:00Z",
                    "collection": {"$id": -1},
                },
            ],
            "count": 3,
        }
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, collection_id=COLLECTION_ALL)

        # Should get bookmarks from multiple collections
        assert response.count == 3
        collection_ids = {b.collection_id for b in response.bookmarks}
        assert 111 in collection_ids
        assert 222 in collection_ids
        assert -1 in collection_ids

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_include_nested_parameter(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify include_nested parameter is passed correctly."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": True, "items": [], "count": 0}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        client.get_bookmarks(days=7, collection_id=12345, include_nested=True)

        # Verify nested parameter was sent
        call_args = mock_session.get.call_args
        params = call_args[1]["params"]
        assert params.get("nested") == "true"

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_empty_collection(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify handling of empty collection."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"result": True, "items": [], "count": 0}
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, collection_id=99999)

        assert response.count == 0
        assert len(response.bookmarks) == 0

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_collection_with_pagination(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify pagination works correctly with collection filter."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Two pages of bookmarks from same collection
        page_1 = {
            "result": True,
            "items": [
                {
                    "_id": i,
                    "title": f"Bookmark {i}",
                    "link": f"https://example.com/{i}",
                    "created": "2025-11-25T10:00:00Z",
                    "collection": {"$id": 12345},
                }
                for i in range(50)
            ],
            "count": 75,
        }
        page_2 = {
            "result": True,
            "items": [
                {
                    "_id": i + 50,
                    "title": f"Bookmark {i + 50}",
                    "link": f"https://example.com/{i + 50}",
                    "created": "2025-11-25T10:00:00Z",
                    "collection": {"$id": 12345},
                }
                for i in range(25)
            ],
            "count": 75,
        }
        
        mock_resp1 = MagicMock()
        mock_resp1.ok = True
        mock_resp1.json.return_value = page_1
        
        mock_resp2 = MagicMock()
        mock_resp2.ok = True
        mock_resp2.json.return_value = page_2
        
        mock_session.get.side_effect = [mock_resp1, mock_resp2]

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7, collection_id=12345)

        # Verify all bookmarks collected
        assert response.count == 75
        
        # Verify all from same collection
        for bookmark in response.bookmarks:
            assert bookmark.collection_id == 12345
        
        # Verify collection ID was in both requests
        for call_args in mock_session.get.call_args_list:
            url = call_args[0][0]
            assert "/raindrops/12345" in url
