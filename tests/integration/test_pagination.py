"""
Integration tests for pagination with multi-page mocked responses.

These tests verify the complete pagination flow when fetching
large numbers of bookmarks.
"""

import pytest
from unittest.mock import MagicMock, patch

from raindrop_bookmarks.client import RaindropClient, MAX_PER_PAGE
from raindrop_bookmarks.models import BookmarkResponse


class TestPaginationIntegration:
    """Integration tests for pagination functionality."""

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_pagination_with_exactly_50_items(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify behavior with exactly MAX_PER_PAGE items."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # First page: exactly 50 items
        first_page = {
            "result": True,
            "items": [
                {"_id": i, "title": f"Item {i}", "link": f"https://example.com/{i}", "created": "2025-11-25T10:00:00Z"}
                for i in range(50)
            ],
            "count": 50,
        }
        # Second page: empty (no more items)
        second_page = {
            "result": True,
            "items": [],
            "count": 50,
        }
        
        mock_resp1 = MagicMock()
        mock_resp1.ok = True
        mock_resp1.json.return_value = first_page
        
        mock_resp2 = MagicMock()
        mock_resp2.ok = True
        mock_resp2.json.return_value = second_page
        
        mock_session.get.side_effect = [mock_resp1, mock_resp2]

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Should fetch second page to confirm end
        assert mock_session.get.call_count == 2
        assert response.count == 50

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_pagination_with_100_items(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify pagination works with 100 items across 2 pages."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Page 0: 50 items
        page_0 = {
            "result": True,
            "items": [
                {"_id": i, "title": f"Item {i}", "link": f"https://example.com/{i}", "created": "2025-11-25T10:00:00Z"}
                for i in range(50)
            ],
            "count": 100,
        }
        # Page 1: 50 items
        page_1 = {
            "result": True,
            "items": [
                {"_id": i + 50, "title": f"Item {i + 50}", "link": f"https://example.com/{i + 50}", "created": "2025-11-25T10:00:00Z"}
                for i in range(50)
            ],
            "count": 100,
        }
        # Page 2: empty
        page_2 = {
            "result": True,
            "items": [],
            "count": 100,
        }
        
        responses = []
        for page_data in [page_0, page_1, page_2]:
            mock_resp = MagicMock()
            mock_resp.ok = True
            mock_resp.json.return_value = page_data
            responses.append(mock_resp)
        
        mock_session.get.side_effect = responses

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Verify all items were collected
        assert response.count == 100
        assert len(response.bookmarks) == 100
        
        # Verify items have unique IDs from 0 to 99
        ids = sorted([b.id for b in response.bookmarks])
        assert ids == list(range(100))

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_pagination_preserves_order(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify bookmarks maintain order across pages."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Create pages with specific order
        page_0 = {
            "result": True,
            "items": [
                {"_id": 100 - i, "title": f"Item {100 - i}", "link": f"https://example.com/{100 - i}", "created": f"2025-11-{30 - (i // 2):02d}T10:00:00Z"}
                for i in range(50)
            ],
            "count": 75,
        }
        page_1 = {
            "result": True,
            "items": [
                {"_id": 50 - i, "title": f"Item {50 - i}", "link": f"https://example.com/{50 - i}", "created": f"2025-11-{15 - (i // 2):02d}T10:00:00Z"}
                for i in range(25)
            ],
            "count": 75,
        }
        
        mock_resp0 = MagicMock()
        mock_resp0.ok = True
        mock_resp0.json.return_value = page_0
        
        mock_resp1 = MagicMock()
        mock_resp1.ok = True
        mock_resp1.json.return_value = page_1
        
        mock_session.get.side_effect = [mock_resp0, mock_resp1]

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=30)

        # Verify order is preserved (first page items first)
        assert len(response.bookmarks) == 75
        # First bookmark should be from page 0
        assert response.bookmarks[0].id == 100
        # Bookmark at index 50 should be first from page 1
        assert response.bookmarks[50].id == 50

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_large_dataset_pagination(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify pagination works with larger datasets (250+ items)."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        total_items = 275
        responses = []
        
        # Create 6 pages (5 full + 1 partial)
        for page in range(6):
            start = page * 50
            end = min(start + 50, total_items)
            items = [
                {"_id": i, "title": f"Item {i}", "link": f"https://example.com/{i}", "created": "2025-11-25T10:00:00Z"}
                for i in range(start, end)
            ]
            
            mock_resp = MagicMock()
            mock_resp.ok = True
            mock_resp.json.return_value = {
                "result": True,
                "items": items,
                "count": total_items,
            }
            responses.append(mock_resp)
        
        mock_session.get.side_effect = responses

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Verify all items collected
        assert response.count == total_items
        assert len(response.bookmarks) == total_items
        
        # Verify 6 API calls were made
        assert mock_session.get.call_count == 6
