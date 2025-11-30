# Tasks: Get Bookmarks in Last N Days from Raindrop API

**Input**: Design documents from `/specs/001-raindrop-bookmarks-by-date/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Tests are included as this is a library with contract tests defined in plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, this is a single project Python library:

- Source code: `src/raindrop_bookmarks/`
- Tests: `tests/`
- Package marker: `src/py.typed`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure per plan.md: `src/raindrop_bookmarks/`, `tests/unit/`, `tests/integration/`, `tests/contract/`
- [X] T002 Initialize Python project with pyproject.toml including dependencies: requests>=2.31, pydantic>=2.0 (optional), pytest, pytest-httpx
- [X] T003 [P] Create `src/raindrop_bookmarks/__init__.py` with package exports placeholder
- [X] T004 [P] Create `src/py.typed` PEP 561 marker for type hints
- [X] T005 [P] Create `tests/conftest.py` with common pytest fixtures

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create `src/raindrop_bookmarks/exceptions.py` with custom exception types: RaindropError (base class), and subclasses AuthenticationError, RateLimitError, ValidationError, NotFoundError, NetworkError, APIError (all inherit from RaindropError)
- [X] T007 Create `src/raindrop_bookmarks/models.py` with Bookmark dataclass: id, title, link, created, tags, collection_id, excerpt, domain, cover
- [X] T008 [P] Create BookmarkRequest dataclass in `src/raindrop_bookmarks/models.py`: days (int), collection_id (int, default=0), include_nested (bool, default=False)
- [X] T009 [P] Create BookmarkResponse dataclass in `src/raindrop_bookmarks/models.py`: bookmarks (list[Bookmark]), count (int), from_date (date), to_date (date)
- [X] T010 Create base RaindropClient skeleton in `src/raindrop_bookmarks/client.py` with constructor accepting access_token and base_url

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Fetch Recent Bookmarks (Priority: P1) 🎯 MVP

**Goal**: Retrieve all bookmarks saved in the last N days so users can review recent saves

**Independent Test**: Call the API with a specific N value and verify returned bookmarks have creation dates within the expected range

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Contract test for GET /raindrops/{collectionId} endpoint in `tests/contract/test_raindrop_api.py` - verify request format and response parsing
- [X] T012 [P] [US1] Unit test for date calculation (N days ago) in `tests/unit/test_client.py`
- [X] T013 [P] [US1] Integration test for fetching bookmarks with mocked API in `tests/integration/test_fetch_bookmarks.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement `_calculate_from_date(days: int) -> str` method in `src/raindrop_bookmarks/client.py` - returns YYYY-MM-DD format
- [X] T015 [US1] Implement `_build_request_params(search: str, sort: str, perpage: int, page: int) -> dict` method in `src/raindrop_bookmarks/client.py`
- [X] T016 [US1] Implement `_parse_raindrop_item(item: dict) -> Bookmark` method in `src/raindrop_bookmarks/client.py` - maps API fields to Bookmark model
- [X] T017 [US1] Implement `get_bookmarks(days: int, collection_id: int = 0) -> BookmarkResponse` main method in `src/raindrop_bookmarks/client.py` - single page fetch
- [X] T018 [US1] Add input validation for N parameter (must be positive integer) in `src/raindrop_bookmarks/client.py`
- [X] T019 [US1] Add HTTP error handling with appropriate exception types in `src/raindrop_bookmarks/client.py` - map 401→AuthenticationError, 404→NotFoundError, 429→RateLimitError
- [X] T020 [US1] Update `src/raindrop_bookmarks/__init__.py` with exports: RaindropClient, Bookmark, BookmarkRequest, BookmarkResponse, and all exception types

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (single page of results)

---

## Phase 4: User Story 2 - Handle Pagination (Priority: P2)

**Goal**: Retrieve all matching bookmarks across multiple API pages so users don't miss any recent saves

**Independent Test**: Create >50 bookmarks in a test account and verify all are returned when N covers the creation period

### Tests for User Story 2 ⚠️

- [X] T021 [P] [US2] Unit test for pagination logic in `tests/unit/test_pagination.py` - verify continues until items < perpage
- [X] T022 [P] [US2] Integration test with multi-page mocked responses in `tests/integration/test_pagination.py`

### Implementation for User Story 2

- [X] T023 [US2] Implement `_fetch_page(collection_id: int, search: str, page: int) -> tuple[list[dict], int]` method in `src/raindrop_bookmarks/client.py`
- [X] T024 [US2] Implement pagination loop in `get_bookmarks()` method in `src/raindrop_bookmarks/client.py` - continue until items < MAX_PER_PAGE (50, Raindrop API limit) or error
- [X] T025 [US2] Add rate limit awareness with optional delay between pagination requests in `src/raindrop_bookmarks/client.py`
- [X] T026 [US2] Add logging for pagination progress in `src/raindrop_bookmarks/client.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (handles any number of bookmarks)

---

## Phase 5: User Story 3 - Filter by Collection (Priority: P3)

**Goal**: Optionally filter bookmarks by collection ID to retrieve recent bookmarks from a specific collection only

**Independent Test**: Filter to a specific collection and verify only bookmarks from that collection are returned

### Tests for User Story 3 ⚠️

- [X] T027 [P] [US3] Unit test for collection ID parameter handling in `tests/unit/test_collection_filter.py`
- [X] T028 [P] [US3] Integration test for collection filtering with mocked API in `tests/integration/test_collection_filter.py`

### Implementation for User Story 3

- [X] T029 [US3] Add collection_id validation with constants (COLLECTION_ALL=0, COLLECTION_UNSORTED=-1, COLLECTION_TRASH=-99, positive=specific) in `src/raindrop_bookmarks/client.py` per Raindrop API docs
- [X] T030 [US3] Add include_nested parameter support to `get_bookmarks()` method in `src/raindrop_bookmarks/client.py`
- [X] T031 [US3] Update integration test fixtures with collection-specific response mocks in `tests/integration/test_collection_filter.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: CLI Interface (Enhancement)

**Purpose**: Provide command-line interface for the library per plan.md

- [X] T032 [P] Create `src/raindrop_bookmarks/cli.py` with argparse-based CLI entry point
- [X] T033 [P] Add CLI arguments: --token, --days, --collection-id, --output-format (json/table)
- [X] T034 Add environment variable support for RAINDROP_ACCESS_TOKEN in `src/raindrop_bookmarks/cli.py`
- [X] T035 Add CLI entry point to pyproject.toml: `raindrop-bookmarks = "raindrop_bookmarks.cli:main"`
- [X] T036 [P] Unit test CLI argument parsing in `tests/unit/test_cli.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T037 [P] Add comprehensive docstrings to all public methods in `src/raindrop_bookmarks/client.py`
- [X] T038 [P] Add type hints throughout all source files in `src/raindrop_bookmarks/`
- [X] T039 [P] Create README.md at project root with installation, usage examples, and API reference
- [X] T040 [P] Add retry logic with exponential backoff for rate limit errors in `src/raindrop_bookmarks/client.py`
- [X] T041 Code review and refactoring for consistency
- [X] T042 Run quickstart.md validation scenarios manually or with integration tests
- [X] T043 Security review: ensure tokens are not logged, validate input sanitization

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **CLI (Phase 6)**: Depends on at least US1 completion
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Extends US1 by adding pagination - Can start after US1 core implementation or in parallel with separate pagination module
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent of US1/US2, adds optional filtering

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T008, T009)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T011: "Contract test for GET /raindrops/{collectionId} in tests/contract/test_raindrop_api.py"
Task T012: "Unit test for date calculation in tests/unit/test_client.py"
Task T013: "Integration test for fetching bookmarks in tests/integration/test_fetch_bookmarks.py"

# After tests fail, implementation tasks T014-T017 are sequential (depend on each other)
```

## Parallel Example: Foundational Phase

```bash
# After T007 (Bookmark model) is complete, these can run in parallel:
Task T008: "Create BookmarkRequest dataclass in src/raindrop_bookmarks/models.py"
Task T009: "Create BookmarkResponse dataclass in src/raindrop_bookmarks/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - users can fetch up to 50 bookmarks from last N days

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (handles large bookmark collections)
4. Add User Story 3 → Test independently → Deploy/Demo (collection filtering)
5. Add CLI → Deploy/Demo (command-line access)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2 (pagination module)
   - Developer C: User Story 3 (collection filtering)
3. Stories complete and integrate independently

---

## Task Summary

| Phase | Tasks | Parallel Opportunities |
|-------|-------|------------------------|
| Phase 1: Setup | 5 (T001-T005) | 3 tasks can run in parallel |
| Phase 2: Foundational | 5 (T006-T010) | 2 tasks can run in parallel |
| Phase 3: User Story 1 | 10 (T011-T020) | 3 test tasks can run in parallel |
| Phase 4: User Story 2 | 6 (T021-T026) | 2 test tasks can run in parallel |
| Phase 5: User Story 3 | 5 (T027-T031) | 2 test tasks can run in parallel |
| Phase 6: CLI | 5 (T032-T036) | 2 tasks can run in parallel |
| Phase 7: Polish | 7 (T037-T043) | 4 tasks can run in parallel |
| **Total** | **43 tasks** | |

### Task Count per User Story

- **User Story 1 (Fetch Recent Bookmarks)**: 10 tasks (T011-T020)
- **User Story 2 (Handle Pagination)**: 6 tasks (T021-T026)
- **User Story 3 (Filter by Collection)**: 5 tasks (T027-T031)

### Suggested MVP Scope

- Complete Phases 1-3 (Setup + Foundational + User Story 1)
- **20 tasks** for MVP delivery
- Delivers: Single-page bookmark fetching with date filtering, error handling, and structured response

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- API rate limit: 120 requests/minute - be mindful during pagination
- Max 50 items per API page - pagination required for large collections
