"""
Unit tests for the RaindropClient.

These tests focus on individual methods and their logic in isolation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from raindrop_bookmarks.client import (
    RaindropClient,
    COLLECTION_ALL,
    COLLECTION_UNSORTED,
    COLLECTION_TRASH,
)
from raindrop_bookmarks.exceptions import ValidationError
from raindrop_bookmarks.models import Bookmark


class TestDateCalculation:
    """Tests for the _calculate_from_date method."""

    def test_calculate_from_date_7_days(self) -> None:
        """Verify date calculation for 7 days ago."""
        client = RaindropClient("test-token")
        result = client._calculate_from_date(7)

        expected_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime(
            "%Y-%m-%d"
        )
        assert result == expected_date

    def test_calculate_from_date_1_day(self) -> None:
        """Verify date calculation for 1 day ago."""
        client = RaindropClient("test-token")
        result = client._calculate_from_date(1)

        expected_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        assert result == expected_date

    def test_calculate_from_date_30_days(self) -> None:
        """Verify date calculation for 30 days ago."""
        client = RaindropClient("test-token")
        result = client._calculate_from_date(30)

        expected_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime(
            "%Y-%m-%d"
        )
        assert result == expected_date

    def test_calculate_from_date_format(self) -> None:
        """Verify date format is YYYY-MM-DD."""
        client = RaindropClient("test-token")
        result = client._calculate_from_date(7)

        # Should match YYYY-MM-DD format
        parts = result.split("-")
        assert len(parts) == 3
        assert len(parts[0]) == 4  # Year
        assert len(parts[1]) == 2  # Month
        assert len(parts[2]) == 2  # Day


class TestBuildRequestParams:
    """Tests for the _build_request_params method."""

    def test_build_params_basic(self) -> None:
        """Verify basic parameter building."""
        client = RaindropClient("test-token")
        params = client._build_request_params(
            search="created:>2025-11-23",
            sort="-created",
            perpage=50,
            page=0,
        )

        assert params["search"] == "created:>2025-11-23"
        assert params["sort"] == "-created"
        assert params["perpage"] == 50
        assert params["page"] == 0

    def test_build_params_with_nested(self) -> None:
        """Verify nested parameter is included when True."""
        client = RaindropClient("test-token")
        params = client._build_request_params(
            search="created:>2025-11-23",
            nested=True,
        )

        assert params["nested"] == "true"

    def test_build_params_without_nested(self) -> None:
        """Verify nested parameter is not included when False."""
        client = RaindropClient("test-token")
        params = client._build_request_params(
            search="created:>2025-11-23",
            nested=False,
        )

        assert "nested" not in params

    def test_build_params_perpage_limit(self) -> None:
        """Verify perpage is limited to max 50."""
        client = RaindropClient("test-token")
        params = client._build_request_params(
            search="created:>2025-11-23",
            perpage=100,  # Above max
        )

        assert params["perpage"] == 50  # Capped at max


class TestParseRaindropItem:
    """Tests for the _parse_raindrop_item method."""

    def test_parse_complete_item(self, sample_bookmark_data: dict) -> None:
        """Verify parsing of a complete API response item."""
        client = RaindropClient("test-token")
        bookmark = client._parse_raindrop_item(sample_bookmark_data)

        assert isinstance(bookmark, Bookmark)
        assert bookmark.id == 123456789
        assert bookmark.title == "Test Bookmark"
        assert bookmark.link == "https://example.com/article"
        assert bookmark.tags == ["test", "python"]
        assert bookmark.collection_id == 12345
        assert bookmark.excerpt == "This is a test bookmark excerpt"
        assert bookmark.domain == "example.com"
        assert bookmark.cover == "https://example.com/cover.jpg"

    def test_parse_minimal_item(self) -> None:
        """Verify parsing of a minimal API response item."""
        client = RaindropClient("test-token")
        minimal_item = {
            "_id": 1,
            "title": "Minimal",
            "link": "https://example.com",
            "created": "2025-11-25T10:00:00Z",
        }
        bookmark = client._parse_raindrop_item(minimal_item)

        assert bookmark.id == 1
        assert bookmark.title == "Minimal"
        assert bookmark.link == "https://example.com"
        assert bookmark.tags == []
        assert bookmark.collection_id is None
        assert bookmark.excerpt is None

    def test_parse_item_with_missing_fields(self) -> None:
        """Verify parsing handles missing optional fields."""
        client = RaindropClient("test-token")
        item = {"_id": 1}  # Missing most fields

        bookmark = client._parse_raindrop_item(item)

        assert bookmark.id == 1
        assert bookmark.title == ""
        assert bookmark.link == ""

    def test_parse_datetime_with_z_suffix(self) -> None:
        """Verify datetime parsing handles Z suffix."""
        client = RaindropClient("test-token")
        item = {
            "_id": 1,
            "title": "Test",
            "link": "https://example.com",
            "created": "2025-11-25T10:30:00Z",
        }
        bookmark = client._parse_raindrop_item(item)

        assert bookmark.created.year == 2025
        assert bookmark.created.month == 11
        assert bookmark.created.day == 25
        assert bookmark.created.hour == 10
        assert bookmark.created.minute == 30


class TestValidation:
    """Tests for input validation."""

    def test_validate_days_positive(self) -> None:
        """Verify positive days value passes validation."""
        client = RaindropClient("test-token")
        # Should not raise
        client._validate_days(1)
        client._validate_days(7)
        client._validate_days(365)

    def test_validate_days_zero(self) -> None:
        """Verify zero days raises ValidationError."""
        client = RaindropClient("test-token")
        with pytest.raises(ValidationError) as exc_info:
            client._validate_days(0)
        assert "positive integer" in str(exc_info.value)

    def test_validate_days_negative(self) -> None:
        """Verify negative days raises ValidationError."""
        client = RaindropClient("test-token")
        with pytest.raises(ValidationError) as exc_info:
            client._validate_days(-5)
        assert "positive integer" in str(exc_info.value)

    def test_validate_collection_id_special_values(self) -> None:
        """Verify special collection IDs pass validation."""
        client = RaindropClient("test-token")
        # Should not raise
        client._validate_collection_id(COLLECTION_ALL)  # 0
        client._validate_collection_id(COLLECTION_UNSORTED)  # -1
        client._validate_collection_id(COLLECTION_TRASH)  # -99

    def test_validate_collection_id_positive(self) -> None:
        """Verify positive collection IDs pass validation."""
        client = RaindropClient("test-token")
        # Should not raise
        client._validate_collection_id(1)
        client._validate_collection_id(12345)

    def test_validate_collection_id_invalid_negative(self) -> None:
        """Verify invalid negative IDs raise ValidationError."""
        client = RaindropClient("test-token")
        with pytest.raises(ValidationError) as exc_info:
            client._validate_collection_id(-50)  # Not a special value
        assert "Invalid collection_id" in str(exc_info.value)

    def test_empty_access_token(self) -> None:
        """Verify empty token raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RaindropClient("")
        assert "Access token is required" in str(exc_info.value)

    def test_whitespace_access_token(self) -> None:
        """Verify whitespace-only token raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            RaindropClient("   ")
        assert "Access token is required" in str(exc_info.value)
