# Data Model: Get Bookmarks in Last N Days from Raindrop API

**Feature Branch**: `001-raindrop-bookmarks-by-date`  
**Created**: 2025-11-30  
**Status**: Complete

## Entity Definitions

### Bookmark

Represents a saved bookmark (called "Raindrop" in the API).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Unique identifier from Raindrop API (`_id`) |
| title | string | Yes | Bookmark title |
| link | string (URL) | Yes | The bookmarked URL |
| created | datetime (ISO 8601) | Yes | When the bookmark was created/saved |
| tags | array[string] | No | User-assigned tags, empty array if none |
| collection_id | integer | No | ID of the parent collection (null for unsorted) |
| excerpt | string | No | Description or excerpt from the page |
| domain | string | No | Domain of the bookmarked URL |
| cover | string (URL) | No | Cover image URL if available |

**Validation Rules**:
- `id` must be a positive integer
- `link` must be a valid URL
- `created` must be a valid ISO 8601 datetime
- `tags` must be an array (can be empty)

**Example**:
```json
{
  "id": 123456789,
  "title": "Example Article",
  "link": "https://example.com/article",
  "created": "2025-11-25T10:30:00Z",
  "tags": ["tech", "python"],
  "collection_id": 12345,
  "excerpt": "An interesting article about...",
  "domain": "example.com",
  "cover": "https://example.com/image.jpg"
}
```

---

### Collection

Represents a folder/category for organizing bookmarks.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Unique identifier; special values: 0=all, -1=unsorted, -99=trash |
| name | string | No | Collection name (for user-created collections) |

**Special Collection IDs**:
- `0` - All bookmarks (excluding Trash)
- `-1` - Unsorted bookmarks
- `-99` - Trash

---

### BookmarkRequest

Parameters for fetching bookmarks.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| days | integer | Yes | - | Number of days to look back (N) |
| collection_id | integer | No | 0 | Collection to filter (0 = all) |
| include_nested | boolean | No | false | Include bookmarks from nested collections |

**Validation Rules**:
- `days` must be a positive integer (> 0)
- `collection_id` must be a valid collection ID

---

### BookmarkResponse

Response wrapper for bookmark queries.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| bookmarks | array[Bookmark] | Yes | List of matching bookmarks |
| count | integer | Yes | Total number of bookmarks returned |
| from_date | date | Yes | Start of date range (today - N days) |
| to_date | date | Yes | End of date range (today) |

**Example**:
```json
{
  "bookmarks": [...],
  "count": 25,
  "from_date": "2025-11-23",
  "to_date": "2025-11-30"
}
```

---

### APIError

Error response structure.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| error_type | string (enum) | Yes | Type of error |
| message | string | Yes | Human-readable error message |
| status_code | integer | No | HTTP status code if applicable |
| retry_after | integer | No | Seconds to wait before retry (for rate limits) |

**Error Types Enum**:
- `AUTHENTICATION_ERROR` - Invalid or expired token
- `RATE_LIMIT_ERROR` - API rate limit exceeded
- `VALIDATION_ERROR` - Invalid request parameters
- `NOT_FOUND_ERROR` - Collection not found
- `NETWORK_ERROR` - Connection or network failure
- `API_ERROR` - Unexpected API response

---

## Relationships

```
┌──────────────────┐
│ BookmarkRequest  │
│ (Input)          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐         ┌─────────────┐
│ Raindrop.io API  │────────▶│  Bookmark   │ (0..*)
│                  │         │             │
└──────────────────┘         └──────┬──────┘
                                    │
                                    │ belongs_to
                                    ▼
                             ┌─────────────┐
                             │ Collection  │
                             │             │
                             └─────────────┘
```

---

## State Transitions

This feature is primarily read-only with no state transitions for bookmarks themselves.

**Request State Flow**:
```
IDLE → FETCHING → (PAGINATING) → COMPLETE
                      ↓
                    ERROR
```

---

## Mapping: Raindrop API → Our Model

| API Field | Model Field | Transform |
|-----------|-------------|-----------|
| `_id` | `id` | Rename |
| `title` | `title` | Direct |
| `link` | `link` | Direct |
| `created` | `created` | Parse as ISO 8601 |
| `tags` | `tags` | Direct (array) |
| `collection.$id` | `collection_id` | Extract from nested object |
| `excerpt` | `excerpt` | Direct |
| `domain` | `domain` | Direct |
| `cover` | `cover` | Direct |
