# Quickstart: Get Bookmarks in Last N Days from Raindrop API

## Prerequisites

1. **Raindrop.io Account**: You need an active Raindrop.io account
2. **API Access Token**: Get your OAuth token from [Raindrop.io App Settings](https://app.raindrop.io/settings/integrations)
3. **Python 3.11+**: Install from [python.org](https://www.python.org/downloads/)

## Installation

```bash
pip install requests
```

## Quick Example

```python
import requests
from datetime import datetime, timedelta

def get_bookmarks_last_n_days(access_token: str, days: int, collection_id: int = 0) -> list[dict]:
    """
    Fetch all bookmarks created in the last N days.
    
    Args:
        access_token: Your Raindrop.io OAuth token
        days: Number of days to look back
        collection_id: Collection to filter (0 = all, -1 = unsorted)
    
    Returns:
        List of bookmark dictionaries
    """
    # Calculate the date N days ago
    from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # API configuration
    base_url = f"https://api.raindrop.io/rest/v1/raindrops/{collection_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    all_bookmarks = []
    page = 0
    
    while True:
        params = {
            "search": f"created:>{from_date}",
            "sort": "-created",
            "perpage": 50,
            "page": page
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        items = data.get("items", [])
        
        if not items:
            break
            
        all_bookmarks.extend(items)
        
        # Check if we've fetched all items
        if len(items) < 50:
            break
            
        page += 1
    
    return all_bookmarks

# Usage
if __name__ == "__main__":
    TOKEN = "your-access-token-here"
    
    # Get bookmarks from the last 7 days
    bookmarks = get_bookmarks_last_n_days(TOKEN, days=7)
    
    print(f"Found {len(bookmarks)} bookmarks from the last 7 days:")
    for bm in bookmarks[:5]:  # Show first 5
        print(f"  - {bm['title']} ({bm['created'][:10]})")
```

## Expected Output

```
Found 12 bookmarks from the last 7 days:
  - How to Use Raindrop API (2025-11-29)
  - Python Best Practices (2025-11-28)
  - REST API Design Guide (2025-11-27)
  - OAuth 2.0 Tutorial (2025-11-26)
  - HTTP Status Codes (2025-11-25)
```

## Common Use Cases

### Get Last 24 Hours

```python
bookmarks = get_bookmarks_last_n_days(TOKEN, days=1)
```

### Get from Specific Collection

```python
# Get from collection ID 12345
bookmarks = get_bookmarks_last_n_days(TOKEN, days=7, collection_id=12345)
```

### Get Unsorted Only

```python
# Collection ID -1 = unsorted
bookmarks = get_bookmarks_last_n_days(TOKEN, days=7, collection_id=-1)
```

## Error Handling

```python
try:
    bookmarks = get_bookmarks_last_n_days(TOKEN, days=7)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Invalid or expired token. Please re-authenticate.")
    elif e.response.status_code == 429:
        print("Rate limit exceeded. Wait and retry.")
    else:
        print(f"API error: {e}")
except requests.exceptions.ConnectionError:
    print("Network error. Check your internet connection.")
```

## Rate Limits

- **Limit**: 120 requests per minute per user
- **Recommendation**: For large bookmark collections, add delays between pagination requests

## Next Steps

1. Review the [full API documentation](./contracts/openapi.yaml)
2. Implement proper error handling for production use
3. Add caching to reduce API calls
4. Consider using async/await for better performance with multiple requests
