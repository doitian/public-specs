#!/usr/bin/env python3
"""
Read Raindrop backup CSV file and print bookmarks saved in the last N days as JSON.

Usage:
    python raindrop_recent.py <csv_file> [--days N]

The CSV file is assumed to be sorted from latest to oldest.
"""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Filter Raindrop bookmarks by creation date and output as JSON."
    )
    parser.add_argument("csv_file", help="Path to the Raindrop backup CSV file")
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=7,
        help="Number of days to look back (default: 7)",
    )
    return parser.parse_args()


def parse_iso_datetime(date_str):
    """Parse ISO 8601 datetime string to datetime object."""
    # Handle both with and without milliseconds
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def filter_recent_bookmarks(csv_file, days):
    """Read CSV and filter bookmarks created in the last N days."""
    now = datetime.now(timezone.utc)
    cutoff_timestamp = now.timestamp() - (days * 24 * 60 * 60)

    bookmarks = []

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            created_str = row.get("created", "")
            created_dt = parse_iso_datetime(created_str)

            if created_dt and created_dt.timestamp() >= cutoff_timestamp:
                bookmarks.append(row)

    return bookmarks


def main():
    """Main entry point."""
    args = parse_args()

    try:
        bookmarks = filter_recent_bookmarks(args.csv_file, args.days)
        print(json.dumps(bookmarks, indent=2))
    except FileNotFoundError:
        print(f"Error: File '{args.csv_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
