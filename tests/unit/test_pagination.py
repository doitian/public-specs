"""
Unit tests for pagination logic.

These tests verify the pagination behavior when fetching
bookmarks that span multiple API pages.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from raindrop_bookmarks.client import RaindropClient, MAX_PER_PAGE


class TestPaginationLogic:
    """Tests for pagination logic in the client."""

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_single_page_no_pagination(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify no pagination when results fit on one page."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Return 25 items (less than MAX_PER_PAGE)
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "result": True,
            "items": [{"_id": i, "title": f"Item {i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(25)],
            "count": 25,
        }
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Should only make one API call
        assert mock_session.get.call_count == 1
        assert response.count == 25

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_pagination_continues_when_page_full(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify pagination continues when page has MAX_PER_PAGE items."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # First page: 50 items (full)
        first_page = {
            "result": True,
            "items": [{"_id": i, "title": f"Item {i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(50)],
            "count": 75,
        }
        
        # Second page: 25 items (partial - signals end)
        second_page = {
            "result": True,
            "items": [{"_id": i, "title": f"Item {i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(50, 75)],
            "count": 75,
        }
        
        mock_response1 = MagicMock()
        mock_response1.ok = True
        mock_response1.json.return_value = first_page
        
        mock_response2 = MagicMock()
        mock_response2.ok = True
        mock_response2.json.return_value = second_page
        
        mock_session.get.side_effect = [mock_response1, mock_response2]

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Should make two API calls
        assert mock_session.get.call_count == 2
        assert response.count == 75

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_pagination_stops_on_partial_page(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify pagination stops when receiving fewer than MAX_PER_PAGE items."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "result": True,
            "items": [{"_id": i, "title": f"Item {i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(30)],
            "count": 30,
        }
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # Only one call needed
        assert mock_session.get.call_count == 1
        assert response.count == 30

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_pagination_stops_on_empty_page(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify pagination stops when receiving empty items list."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "result": True,
            "items": [],
            "count": 0,
        }
        mock_session.get.return_value = mock_response

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        assert mock_session.get.call_count == 1
        assert response.count == 0

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_page_numbers_increment(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify page number increments correctly in API calls."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Three full pages then partial
        responses = []
        for page in range(4):
            items_count = MAX_PER_PAGE if page < 3 else 25
            mock_resp = MagicMock()
            mock_resp.ok = True
            mock_resp.json.return_value = {
                "result": True,
                "items": [{"_id": i, "title": f"Item {i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(items_count)],
                "count": 175,
            }
            responses.append(mock_resp)
        
        mock_session.get.side_effect = responses

        client = RaindropClient("test-token")
        client.get_bookmarks(days=7)

        # Verify page numbers in calls
        call_args_list = mock_session.get.call_args_list
        for i, call_args in enumerate(call_args_list):
            params = call_args[1]["params"]
            assert params["page"] == i

    @patch("raindrop_bookmarks.client.requests.Session")
    def test_accumulates_all_bookmarks(
        self, mock_session_class: MagicMock
    ) -> None:
        """Verify all bookmarks from all pages are accumulated."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Two pages: 50 + 30 = 80 total
        first_page = {
            "result": True,
            "items": [{"_id": i, "title": f"Page1-Item{i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(50)],
            "count": 80,
        }
        second_page = {
            "result": True,
            "items": [{"_id": i + 50, "title": f"Page2-Item{i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(30)],
            "count": 80,
        }
        
        mock_response1 = MagicMock()
        mock_response1.ok = True
        mock_response1.json.return_value = first_page
        
        mock_response2 = MagicMock()
        mock_response2.ok = True
        mock_response2.json.return_value = second_page
        
        mock_session.get.side_effect = [mock_response1, mock_response2]

        client = RaindropClient("test-token")
        response = client.get_bookmarks(days=7)

        # All 80 bookmarks should be returned
        assert response.count == 80
        assert len(response.bookmarks) == 80
        
        # Verify we have items from both pages
        titles = [b.title for b in response.bookmarks]
        assert "Page1-Item0" in titles
        assert "Page2-Item0" in titles

    @patch("raindrop_bookmarks.client.requests.Session")
    @patch("time.sleep")
    def test_page_delay_between_requests(
        self, mock_sleep: MagicMock, mock_session_class: MagicMock
    ) -> None:
        """Verify delay is applied between pagination requests."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Two pages
        responses = []
        for page in range(2):
            items_count = MAX_PER_PAGE if page == 0 else 10
            mock_resp = MagicMock()
            mock_resp.ok = True
            mock_resp.json.return_value = {
                "result": True,
                "items": [{"_id": i, "title": f"Item {i}", "link": "https://example.com", "created": "2025-11-25T10:00:00Z"} for i in range(items_count)],
                "count": 60,
            }
            responses.append(mock_resp)
        
        mock_session.get.side_effect = responses

        # Create client with delay
        client = RaindropClient("test-token", page_delay=0.5)
        client.get_bookmarks(days=7)

        # Verify sleep was called between pages
        mock_sleep.assert_called_once_with(0.5)
