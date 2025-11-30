# Feature Specification: Get Bookmarks in Last N Days from Raindrop API

**Feature Branch**: `001-raindrop-bookmarks-by-date`  
**Created**: 2025-11-30  
**Status**: Draft  
**Input**: User description: "Create a feature that fetches bookmarks from the Raindrop.io API that were created or saved in the last N days, where N is configurable."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fetch Recent Bookmarks (Priority: P1)

As a user, I want to retrieve all my bookmarks that were saved in the last N days so that I can review my recent saves.

**Why this priority**: This is the core functionality - without this, the feature has no value. It directly addresses the main requirement.

**Independent Test**: Can be fully tested by calling the API with a specific N value and verifying returned bookmarks have creation dates within the expected range.

**Acceptance Scenarios**:

1. **Given** a valid API token and N=7, **When** I request bookmarks, **Then** I receive only bookmarks created within the last 7 days, sorted by creation date (newest first).
2. **Given** a valid API token and N=1, **When** I request bookmarks, **Then** I receive only bookmarks created in the last 24 hours.
3. **Given** a valid API token and N=30, **When** I request bookmarks, **Then** I receive bookmarks from the last 30 days.

---

### User Story 2 - Handle Pagination (Priority: P2)

As a user with many bookmarks, I want the feature to retrieve all matching bookmarks across multiple API pages so that I don't miss any recent saves.

**Why this priority**: Essential for users with high bookmark volume; without this, users may receive incomplete results.

**Independent Test**: Can be tested by creating >50 bookmarks in a test account and verifying all are returned when N covers the creation period.

**Acceptance Scenarios**:

1. **Given** a user with 100 bookmarks in the last 7 days and N=7, **When** I request bookmarks, **Then** I receive all 100 bookmarks (handling pagination automatically).
2. **Given** a user with bookmarks across 3 pages, **When** I request bookmarks, **Then** the system fetches all pages until no more results exist within the date range.

---

### User Story 3 - Filter by Collection (Priority: P3)

As a user, I want to optionally filter bookmarks by collection ID so that I can retrieve recent bookmarks from a specific collection only.

**Why this priority**: Nice-to-have enhancement that adds flexibility but core functionality works without it.

**Independent Test**: Can be tested by filtering to a specific collection and verifying only bookmarks from that collection are returned.

**Acceptance Scenarios**:

1. **Given** a valid collection ID and N=7, **When** I request bookmarks, **Then** I receive only bookmarks from that collection created in the last 7 days.
2. **Given** collection ID=0 (all bookmarks) and N=7, **When** I request bookmarks, **Then** I receive bookmarks from all collections created in the last 7 days.

---

### Edge Cases

- What happens when N=0? Should return no bookmarks or throw validation error.
- What happens when N is negative? Should throw validation error.
- What happens when API token is invalid or expired? Should return authentication error with clear message.
- What happens when rate limit is exceeded (120 requests/minute)? Should handle gracefully with retry or clear error.
- What happens when no bookmarks exist in the date range? Should return empty array, not error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate with Raindrop.io API using OAuth Bearer token
- **FR-002**: System MUST accept a configurable N parameter representing number of days
- **FR-003**: System MUST fetch bookmarks created within the last N days using the `created:>` search filter
- **FR-004**: System MUST handle pagination automatically to retrieve all matching bookmarks (max 50 per page)
- **FR-005**: System MUST return bookmarks in a structured format containing: id, title, link, created date, collection, tags
- **FR-006**: System MUST validate that N is a positive integer
- **FR-007**: System SHOULD allow optional filtering by collection ID (default: 0 for all collections)
- **FR-008**: System MUST handle API errors gracefully with meaningful error messages
- **FR-009**: System MUST respect rate limits (120 requests/minute)

### Key Entities

- **Bookmark (Raindrop)**: Represents a saved bookmark with id, title, link/URL, created timestamp, excerpt, tags, collection reference, and cover image
- **Collection**: Represents a folder/category for organizing bookmarks; referenced by ID in bookmarks
- **APIResponse**: Wrapper containing items array, count, and pagination info

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can retrieve bookmarks from the last N days with a single function/command call
- **SC-002**: Response time is acceptable for typical use cases (<5 seconds for up to 500 bookmarks)
- **SC-003**: All bookmarks within the date range are returned (verified via count matching API total)
- **SC-004**: Zero data loss - all bookmark fields are preserved in the structured output
