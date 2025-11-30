# Phase 0 Research: Get Bookmarks in Last N Days from Raindrop API

**Feature Branch**: `001-raindrop-bookmarks-by-date`  
**Created**: 2025-11-30  
**Status**: Complete

## Research Tasks

### 1. Raindrop.io API Authentication

**Decision**: Use OAuth 2.0 Bearer token authentication

**Rationale**: 
- Official Raindrop.io API requires OAuth authentication
- Bearer tokens are passed in the `Authorization` header as `Bearer <access-token>`
- Rate limit is 120 requests per minute per authenticated user
- Tokens are obtained through Raindrop.io app registration

**Alternatives Considered**:
- API Key authentication: Not supported by Raindrop.io API
- Session-based auth: Not available for API access

**Implementation Notes**:
- Require user to provide OAuth access token as configuration
- Token should be stored securely (environment variable or secure config)
- Include proper error handling for expired/invalid tokens

---

### 2. Date Filtering Mechanism

**Decision**: Use the `search` query parameter with `created:>YYYY-MM-DD` syntax

**Rationale**:
- Raindrop.io API supports date filtering via search parameter
- `created:>YYYY-MM-DD` filters bookmarks created after the specified date
- This is the officially documented approach
- Dates should be in ISO 8601 format

**Alternatives Considered**:
- Client-side filtering: Inefficient, would require fetching all bookmarks
- Custom date parameters: Not supported by the API

**Implementation Notes**:
- Calculate target date as: `today - N days`
- Format date as `YYYY-MM-DD`
- Combine with sort parameter `-created` for newest first

---

### 3. Pagination Strategy

**Decision**: Use page-based pagination with automatic iteration

**Rationale**:
- API returns max 50 items per page (`perpage` parameter)
- Page numbers start at 0
- Response includes `count` field for total matching items
- Need to loop until all pages are fetched

**Alternatives Considered**:
- Cursor-based pagination: Not supported by this API
- Single large request: Not possible due to 50-item limit

**Implementation Notes**:
- Start at page 0
- Continue until `items.length < perpage` or total fetched equals `count`
- Accumulate results across pages
- Be mindful of rate limits (120/min) for users with many bookmarks

---

### 4. API Endpoint Structure

**Decision**: Use `GET https://api.raindrop.io/rest/v1/raindrops/{collectionId}`

**Rationale**:
- Official endpoint for fetching multiple bookmarks
- Collection ID 0 = all bookmarks (excluding Trash)
- Collection ID -1 = Unsorted bookmarks
- Collection ID -99 = Trash
- Specific positive IDs for user collections

**Alternatives Considered**:
- Bulk export endpoint: Exists but designed for full export, not filtered queries
- Search endpoint: Same functionality, this is the recommended approach

**Implementation Notes**:
- Default to collection ID 0 (all)
- Allow optional collection ID parameter for filtering
- Include `nested=true` if sub-collection support is desired

---

### 5. Response Data Structure

**Decision**: Map API response to clean Bookmark model

**Rationale**:
- Raindrop API returns rich objects with many fields
- Users typically need: id, title, link, created, tags, collection, excerpt
- Simplify by exposing only commonly needed fields
- Preserve full data if needed via optional flag

**Key Fields from API Response**:
```json
{
  "_id": 123456789,
  "title": "Bookmark Title",
  "link": "https://example.com",
  "created": "2025-11-25T10:30:00Z",
  "tags": ["tag1", "tag2"],
  "collection": {"$id": 12345},
  "excerpt": "Description text...",
  "cover": "https://cover-image-url.jpg",
  "domain": "example.com"
}
```

---

### 6. Technology Stack Decision

**Decision**: Python with `requests` library

**Rationale**:
- Python is widely used for API integrations
- `requests` library is the de facto standard for HTTP in Python
- Simple, readable code for REST API calls
- Easy to integrate into larger projects or use standalone
- Good type hint support with Python 3.11+

**Alternatives Considered**:
- Node.js/TypeScript: Valid alternative, more complex setup
- Go: Overkill for simple API client
- curl/shell: Too limited for pagination and data processing

**Implementation Notes**:
- Use `requests` for HTTP calls
- Use `dataclasses` or `pydantic` for models
- Include proper type hints
- Support both library and CLI usage

---

### 7. Error Handling Strategy

**Decision**: Define clear error types with actionable messages

**Rationale**:
- API can fail for various reasons (auth, rate limit, network)
- Users need clear feedback to resolve issues
- Different errors require different responses

**Error Types**:
| Error | HTTP Code | User Action |
|-------|-----------|-------------|
| Invalid token | 401 | Re-authenticate |
| Rate limited | 429 | Wait and retry |
| Collection not found | 404 | Check collection ID |
| Network error | - | Check connection |
| Invalid N value | - | Provide positive integer |

---

## Dependencies Summary

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| requests | 2.31+ | HTTP client |
| pydantic | 2.0+ | Data validation (optional) |

## Open Questions Resolved

All initial NEEDS CLARIFICATION items have been resolved:

1. ✅ Authentication method → OAuth Bearer token
2. ✅ Date filtering approach → `search=created:>YYYY-MM-DD`
3. ✅ Pagination handling → Page-based, auto-iterate
4. ✅ API endpoint → `/rest/v1/raindrops/{collectionId}`
5. ✅ Language/stack → Python 3.11+ with requests
