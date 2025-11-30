# Raindrop Bookmarks

A Python library for fetching bookmarks from the Raindrop.io API that were created/saved in the last N days.

## Features

- **Date-based filtering**: Retrieve bookmarks from the last N days
- **Automatic pagination**: Handles large bookmark collections automatically
- **Collection filtering**: Filter by specific collections, unsorted, or trash
- **CLI interface**: Command-line tool for quick access
- **Comprehensive error handling**: Clear error messages for authentication, rate limits, and network issues
- **Type hints**: Full type annotations for IDE support

## Installation

```bash
pip install raindrop-bookmarks
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

### As a Library

```python
from raindrop_bookmarks import RaindropClient

# Create client with your access token
client = RaindropClient("your-access-token")

# Get bookmarks from the last 7 days
response = client.get_bookmarks(days=7)

print(f"Found {response.count} bookmarks")
for bookmark in response.bookmarks:
    print(f"  - {bookmark.title} ({bookmark.created.strftime('%Y-%m-%d')})")
```

### From Command Line

```bash
# Set your token as an environment variable
export RAINDROP_ACCESS_TOKEN="your-access-token"

# Get bookmarks from the last 7 days
raindrop-bookmarks --days 7

# Output as JSON
raindrop-bookmarks --days 7 --output-format json

# Filter by collection
raindrop-bookmarks --days 7 --collection-id 12345
```

## API Reference

### RaindropClient

The main client class for interacting with the Raindrop.io API.

```python
client = RaindropClient(
    access_token="your-token",  # Required: OAuth Bearer token
    base_url="...",            # Optional: API base URL
    page_delay=0.5,            # Optional: Delay between pagination requests
)
```

### get_bookmarks()

Fetch bookmarks from the last N days.

```python
response = client.get_bookmarks(
    days=7,                    # Required: Number of days to look back
    collection_id=0,           # Optional: Collection ID (0=all, -1=unsorted, -99=trash)
    include_nested=False,      # Optional: Include nested collections
)
```

Returns a `BookmarkResponse` with:
- `bookmarks`: List of `Bookmark` objects
- `count`: Total number of bookmarks
- `from_date`: Start of date range
- `to_date`: End of date range

### Bookmark

Each bookmark contains:
- `id`: Unique identifier
- `title`: Bookmark title
- `link`: The bookmarked URL
- `created`: Creation datetime
- `tags`: List of tags
- `collection_id`: Parent collection ID
- `excerpt`: Page excerpt
- `domain`: URL domain
- `cover`: Cover image URL

## Collection IDs

| ID | Description |
|----|-------------|
| 0 | All bookmarks (excluding trash) |
| -1 | Unsorted bookmarks |
| -99 | Trash |
| > 0 | Specific user collection |

## Error Handling

The library provides specific exception types:

```python
from raindrop_bookmarks import (
    RaindropError,      # Base exception
    AuthenticationError, # Invalid/expired token (401)
    RateLimitError,     # Rate limit exceeded (429)
    ValidationError,    # Invalid parameters
    NotFoundError,      # Collection not found (404)
    NetworkError,       # Connection issues
    APIError,           # Other API errors
)

try:
    response = client.get_bookmarks(days=7)
except AuthenticationError:
    print("Please check your access token")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except RaindropError as e:
    print(f"Error: {e.message}")
```

## Getting an Access Token

1. Go to [Raindrop.io Integrations](https://app.raindrop.io/settings/integrations)
2. Create a new app or use the "Test Token"
3. Copy the access token

## Rate Limits

The Raindrop.io API has a rate limit of 120 requests per minute. For large bookmark collections, consider using the `page_delay` parameter to add delays between pagination requests.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=raindrop_bookmarks
```

## License

MIT