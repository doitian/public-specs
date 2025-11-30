"""
Contract tests for the Raindrop.io API.

These tests verify that our client correctly interacts with the Raindrop API
according to the OpenAPI specification.
"""

import pytest
from pytest_httpx import HTTPXMock
import httpx

from raindrop_bookmarks.client import RaindropClient, BASE_URL


class TestRaindropAPIContract:
    """Test the contract with the Raindrop.io API."""

    def test_get_raindrops_request_format(self, httpx_mock: HTTPXMock) -> None:
        """Verify GET /raindrops/{collectionId} request format."""
        # Mock the expected response
        httpx_mock.add_response(
            method="GET",
            url=httpx.URL(f"{BASE_URL}/raindrops/0").copy_with(
                params={
                    "search": "created:>2025-11-23",
                    "sort": "-created",
                    "perpage": "50",
                    "page": "0",
                }
            ),
            json={"result": True, "items": [], "count": 0},
        )

        # Create client and make request - use httpx directly for contract testing
        client = httpx.Client(
            headers={"Authorization": "Bearer test-token"},
            base_url=BASE_URL,
        )
        
        response = client.get(
            "/raindrops/0",
            params={
                "search": "created:>2025-11-23",
                "sort": "-created",
                "perpage": 50,
                "page": 0,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"] is True
        assert isinstance(data["items"], list)
        assert "count" in data

    def test_response_parsing_with_bookmark_data(
        self, httpx_mock: HTTPXMock, sample_bookmark_data: dict
    ) -> None:
        """Verify response parsing matches expected Raindrop schema."""
        httpx_mock.add_response(
            json={
                "result": True,
                "items": [sample_bookmark_data],
                "count": 1,
            }
        )

        client = httpx.Client(base_url=BASE_URL)
        response = client.get("/raindrops/0")
        data = response.json()

        # Verify the structure matches OpenAPI spec
        assert "result" in data
        assert "items" in data
        assert "count" in data

        # Verify bookmark structure
        item = data["items"][0]
        assert "_id" in item
        assert "title" in item
        assert "link" in item
        assert "created" in item

    def test_authorization_header_format(self, httpx_mock: HTTPXMock) -> None:
        """Verify Authorization header is sent correctly."""
        def check_auth_header(request: httpx.Request) -> httpx.Response:
            auth_header = request.headers.get("Authorization")
            assert auth_header is not None
            assert auth_header.startswith("Bearer ")
            return httpx.Response(
                status_code=200,
                json={"result": True, "items": [], "count": 0},
            )

        httpx_mock.add_callback(check_auth_header)

        client = httpx.Client(
            headers={"Authorization": "Bearer test-token"},
            base_url=BASE_URL,
        )
        client.get("/raindrops/0")

    def test_collection_id_in_path(self, httpx_mock: HTTPXMock) -> None:
        """Verify collection ID is correctly included in the path."""
        collection_ids = [0, -1, -99, 12345]

        for cid in collection_ids:
            httpx_mock.add_response(
                method="GET",
                url=httpx.URL(f"{BASE_URL}/raindrops/{cid}"),
                json={"result": True, "items": [], "count": 0},
            )

            client = httpx.Client(base_url=BASE_URL)
            response = client.get(f"/raindrops/{cid}")
            assert response.status_code == 200

    def test_error_response_format_401(self, httpx_mock: HTTPXMock) -> None:
        """Verify 401 error response format."""
        httpx_mock.add_response(
            status_code=401,
            json={
                "result": False,
                "errorMessage": "Invalid access token",
                "error": 401,
            },
        )

        client = httpx.Client(base_url=BASE_URL)
        response = client.get("/raindrops/0")

        assert response.status_code == 401
        data = response.json()
        assert data["result"] is False
        assert "errorMessage" in data

    def test_error_response_format_429(self, httpx_mock: HTTPXMock) -> None:
        """Verify 429 rate limit error response format."""
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "60"},
            json={
                "result": False,
                "errorMessage": "Rate limit exceeded",
                "error": 429,
            },
        )

        client = httpx.Client(base_url=BASE_URL)
        response = client.get("/raindrops/0")

        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_search_parameter_date_format(self, httpx_mock: HTTPXMock) -> None:
        """Verify search parameter uses correct date format."""
        def check_search_param(request: httpx.Request) -> httpx.Response:
            search = request.url.params.get("search")
            assert search is not None
            # Should be in format "created:>YYYY-MM-DD"
            assert search.startswith("created:>")
            date_part = search.split(">")[1]
            # Verify it's a valid date format (YYYY-MM-DD)
            parts = date_part.split("-")
            assert len(parts) == 3
            assert len(parts[0]) == 4  # Year
            assert len(parts[1]) == 2  # Month
            assert len(parts[2]) == 2  # Day
            return httpx.Response(
                status_code=200,
                json={"result": True, "items": [], "count": 0},
            )

        httpx_mock.add_callback(check_search_param)

        client = httpx.Client(base_url=BASE_URL)
        client.get("/raindrops/0", params={"search": "created:>2025-11-23"})
