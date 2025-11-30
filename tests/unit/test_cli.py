"""
Unit tests for CLI argument parsing.
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from raindrop_bookmarks.cli import (
    create_parser,
    get_access_token,
    format_table,
    format_json,
    main,
    ENV_TOKEN_KEY,
)
from raindrop_bookmarks.models import BookmarkResponse, Bookmark
from datetime import date, datetime, timezone


class TestArgumentParsing:
    """Tests for CLI argument parsing."""

    def test_required_days_argument(self) -> None:
        """Verify --days is required."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_days_argument(self) -> None:
        """Verify --days argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7"])
        
        assert args.days == 7

    def test_token_argument(self) -> None:
        """Verify --token argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7", "--token", "my-token"])
        
        assert args.token == "my-token"

    def test_collection_id_argument(self) -> None:
        """Verify --collection-id argument parsing."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7", "--collection-id", "12345"])
        
        assert args.collection_id == 12345

    def test_collection_id_default(self) -> None:
        """Verify --collection-id defaults to 0."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7"])
        
        assert args.collection_id == 0

    def test_include_nested_flag(self) -> None:
        """Verify --include-nested flag."""
        parser = create_parser()
        
        args_without = parser.parse_args(["--days", "7"])
        assert args_without.include_nested is False
        
        args_with = parser.parse_args(["--days", "7", "--include-nested"])
        assert args_with.include_nested is True

    def test_output_format_json(self) -> None:
        """Verify --output-format json."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7", "--output-format", "json"])
        
        assert args.output_format == "json"

    def test_output_format_table(self) -> None:
        """Verify --output-format table."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7", "--output-format", "table"])
        
        assert args.output_format == "table"

    def test_output_format_default(self) -> None:
        """Verify --output-format defaults to table."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7"])
        
        assert args.output_format == "table"

    def test_verbose_flag(self) -> None:
        """Verify --verbose flag."""
        parser = create_parser()
        
        args_without = parser.parse_args(["--days", "7"])
        assert args_without.verbose is False
        
        args_with = parser.parse_args(["--days", "7", "--verbose"])
        assert args_with.verbose is True
        
        args_short = parser.parse_args(["--days", "7", "-v"])
        assert args_short.verbose is True


class TestAccessToken:
    """Tests for access token retrieval."""

    def test_token_from_args(self) -> None:
        """Verify token is read from command-line argument."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7", "--token", "arg-token"])
        
        token = get_access_token(args)
        assert token == "arg-token"

    def test_token_from_env(self) -> None:
        """Verify token is read from environment variable."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7"])
        
        with patch.dict(os.environ, {ENV_TOKEN_KEY: "env-token"}):
            token = get_access_token(args)
            assert token == "env-token"

    def test_token_args_priority_over_env(self) -> None:
        """Verify command-line token takes priority over env."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7", "--token", "arg-token"])
        
        with patch.dict(os.environ, {ENV_TOKEN_KEY: "env-token"}):
            token = get_access_token(args)
            assert token == "arg-token"

    def test_no_token_returns_none(self) -> None:
        """Verify None is returned when no token is provided."""
        parser = create_parser()
        args = parser.parse_args(["--days", "7"])
        
        with patch.dict(os.environ, {}, clear=True):
            # Ensure RAINDROP_ACCESS_TOKEN is not set
            os.environ.pop(ENV_TOKEN_KEY, None)
            token = get_access_token(args)
            assert token is None


class TestOutputFormatting:
    """Tests for output formatting."""

    @pytest.fixture
    def sample_response(self) -> BookmarkResponse:
        """Create a sample BookmarkResponse for testing."""
        return BookmarkResponse(
            bookmarks=[
                Bookmark(
                    id=1,
                    title="Test Bookmark",
                    link="https://example.com",
                    created=datetime(2025, 11, 25, 10, 0, 0, tzinfo=timezone.utc),
                    tags=["test", "python"],
                    domain="example.com",
                ),
                Bookmark(
                    id=2,
                    title="Another Bookmark",
                    link="https://another.com",
                    created=datetime(2025, 11, 26, 10, 0, 0, tzinfo=timezone.utc),
                    tags=[],
                    domain="another.com",
                ),
            ],
            count=2,
            from_date=date(2025, 11, 23),
            to_date=date(2025, 11, 30),
        )

    def test_format_table(self, sample_response: BookmarkResponse) -> None:
        """Verify table formatting."""
        output = format_table(sample_response)
        
        assert "Found 2 bookmarks" in output
        assert "Test Bookmark" in output
        assert "Another Bookmark" in output
        assert "example.com" in output
        assert "test, python" in output

    def test_format_json(self, sample_response: BookmarkResponse) -> None:
        """Verify JSON formatting."""
        import json
        
        output = format_json(sample_response)
        data = json.loads(output)
        
        assert data["count"] == 2
        assert data["from_date"] == "2025-11-23"
        assert data["to_date"] == "2025-11-30"
        assert len(data["bookmarks"]) == 2
        assert data["bookmarks"][0]["title"] == "Test Bookmark"

    def test_format_empty_response(self) -> None:
        """Verify formatting of empty response."""
        response = BookmarkResponse(
            bookmarks=[],
            count=0,
            from_date=date(2025, 11, 23),
            to_date=date(2025, 11, 30),
        )
        
        table_output = format_table(response)
        assert "Found 0 bookmarks" in table_output
        assert "No bookmarks found" in table_output
        
        json_output = format_json(response)
        import json
        data = json.loads(json_output)
        assert data["count"] == 0
        assert data["bookmarks"] == []


class TestMainFunction:
    """Tests for the main CLI function."""

    def test_missing_token_returns_error(self) -> None:
        """Verify error when no token is provided."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop(ENV_TOKEN_KEY, None)
            exit_code = main(["--days", "7"])
            assert exit_code == 1

    def test_invalid_days_returns_error(self) -> None:
        """Verify error when days is not positive."""
        exit_code = main(["--days", "0", "--token", "test-token"])
        assert exit_code == 1
        
        exit_code = main(["--days", "-5", "--token", "test-token"])
        assert exit_code == 1

    @patch("raindrop_bookmarks.cli.RaindropClient")
    def test_successful_fetch(self, mock_client_class: MagicMock) -> None:
        """Verify successful fetch returns 0."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_bookmarks.return_value = BookmarkResponse(
            bookmarks=[],
            count=0,
            from_date=date(2025, 11, 23),
            to_date=date(2025, 11, 30),
        )
        
        exit_code = main(["--days", "7", "--token", "test-token"])
        assert exit_code == 0

    @patch("raindrop_bookmarks.cli.RaindropClient")
    def test_auth_error_returns_error(self, mock_client_class: MagicMock) -> None:
        """Verify authentication error returns non-zero."""
        from raindrop_bookmarks.exceptions import AuthenticationError
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_bookmarks.side_effect = AuthenticationError()
        
        exit_code = main(["--days", "7", "--token", "bad-token"])
        assert exit_code == 1
