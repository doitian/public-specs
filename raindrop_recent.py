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
    skipped_count = 0

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            created_str = row.get("created", "")
            created_dt = parse_iso_datetime(created_str)

            if created_dt is None:
                skipped_count += 1
                continue

            if created_dt.timestamp() >= cutoff_timestamp:
                bookmarks.append(row)

    if skipped_count > 0:
        print(
            f"Warning: Skipped {skipped_count} row(s) with invalid or missing creation dates.",
            file=sys.stderr,
        )

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
    except PermissionError:
        print(f"Error: Permission denied to read '{args.csv_file}'.", file=sys.stderr)
        sys.exit(1)
    except csv.Error as e:
        print(f"Error: Failed to parse CSV file: {e}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError as e:
        print(f"Error: Failed to decode file (encoding issue): {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
