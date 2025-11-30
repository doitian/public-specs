"""
Command-line interface for the Raindrop Bookmarks library.

This module provides a CLI entry point for fetching bookmarks
from the Raindrop.io API.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Optional

from .client import RaindropClient, COLLECTION_ALL, COLLECTION_UNSORTED, COLLECTION_TRASH
from .exceptions import (
    RaindropError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
    NotFoundError,
    NetworkError,
)
from .models import BookmarkResponse

# Environment variable for access token
ENV_TOKEN_KEY = "RAINDROP_ACCESS_TOKEN"


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="raindrop-bookmarks",
        description="Fetch bookmarks from Raindrop.io from the last N days",
        epilog="Example: raindrop-bookmarks --days 7 --output-format json",
    )

    parser.add_argument(
        "--token",
        type=str,
        help=f"Raindrop.io OAuth access token (or set {ENV_TOKEN_KEY} env var)",
    )

    parser.add_argument(
        "--days",
        type=int,
        required=True,
        help="Number of days to look back (required, must be positive)",
    )

    parser.add_argument(
        "--collection-id",
        type=int,
        default=COLLECTION_ALL,
        help="Collection ID to filter (0=all, -1=unsorted, -99=trash, or positive ID). Default: 0",
    )

    parser.add_argument(
        "--include-nested",
        action="store_true",
        help="Include bookmarks from nested collections",
    )

    parser.add_argument(
        "--output-format",
        choices=["json", "table"],
        default="table",
        help="Output format: json or table. Default: table",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def get_access_token(args: argparse.Namespace) -> Optional[str]:
    """
    Get the access token from args or environment variable.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Access token string or None if not found.
    """
    # First check command-line argument
    if args.token:
        return args.token

    # Then check environment variable
    return os.environ.get(ENV_TOKEN_KEY)


def format_table(response: BookmarkResponse) -> str:
    """
    Format the response as a readable table.

    Args:
        response: The bookmark response to format.

    Returns:
        Formatted table string.
    """
    lines = []
    
    # Header
    lines.append(f"Found {response.count} bookmarks from {response.from_date} to {response.to_date}")
    lines.append("")
    
    if not response.bookmarks:
        lines.append("No bookmarks found.")
        return "\n".join(lines)
    
    # Calculate column widths
    max_title = min(50, max(len(b.title) for b in response.bookmarks))
    max_domain = max(len(b.domain or "") for b in response.bookmarks)
    
    # Table header
    header = f"{'Date':<12} {'Title':<{max_title}} {'Domain':<{max_domain}} {'Tags'}"
    lines.append(header)
    lines.append("-" * len(header))
    
    # Table rows
    for bookmark in response.bookmarks:
        date_str = bookmark.created.strftime("%Y-%m-%d")
        title = bookmark.title[:max_title] if len(bookmark.title) > max_title else bookmark.title
        domain = bookmark.domain or ""
        tags = ", ".join(bookmark.tags) if bookmark.tags else ""
        
        lines.append(f"{date_str:<12} {title:<{max_title}} {domain:<{max_domain}} {tags}")
    
    return "\n".join(lines)


def format_json(response: BookmarkResponse) -> str:
    """
    Format the response as JSON.

    Args:
        response: The bookmark response to format.

    Returns:
        JSON string.
    """
    data = {
        "count": response.count,
        "from_date": response.from_date.isoformat(),
        "to_date": response.to_date.isoformat(),
        "bookmarks": [
            {
                "id": b.id,
                "title": b.title,
                "link": b.link,
                "created": b.created.isoformat(),
                "tags": b.tags,
                "collection_id": b.collection_id,
                "excerpt": b.excerpt,
                "domain": b.domain,
                "cover": b.cover,
            }
            for b in response.bookmarks
        ],
    }
    return json.dumps(data, indent=2)


def main(argv: Optional[list[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Get access token
    token = get_access_token(args)
    if not token:
        print(f"Error: Access token is required. Provide --token or set {ENV_TOKEN_KEY} environment variable.", file=sys.stderr)
        return 1

    # Validate days
    if args.days <= 0:
        print("Error: --days must be a positive integer.", file=sys.stderr)
        return 1

    try:
        if args.verbose:
            print(f"Fetching bookmarks from the last {args.days} days...", file=sys.stderr)

        # Create client and fetch bookmarks
        client = RaindropClient(token)
        response = client.get_bookmarks(
            days=args.days,
            collection_id=args.collection_id,
            include_nested=args.include_nested,
        )

        # Format and output
        if args.output_format == "json":
            output = format_json(response)
        else:
            output = format_table(response)

        print(output)
        return 0

    except AuthenticationError as e:
        print(f"Authentication error: {e.message}", file=sys.stderr)
        print("Please verify your access token is valid.", file=sys.stderr)
        return 1

    except RateLimitError as e:
        print(f"Rate limit exceeded: {e.message}", file=sys.stderr)
        if e.retry_after:
            print(f"Please retry after {e.retry_after} seconds.", file=sys.stderr)
        return 1

    except ValidationError as e:
        print(f"Validation error: {e.message}", file=sys.stderr)
        return 1

    except NotFoundError as e:
        print(f"Not found: {e.message}", file=sys.stderr)
        return 1

    except NetworkError as e:
        print(f"Network error: {e.message}", file=sys.stderr)
        print("Please check your internet connection.", file=sys.stderr)
        return 1

    except RaindropError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
