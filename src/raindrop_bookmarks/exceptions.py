"""
Custom exception types for the Raindrop Bookmarks library.

All exceptions inherit from RaindropError, which allows catching any
library-specific error with a single exception type.
"""


class RaindropError(Exception):
    """Base exception for all Raindrop Bookmarks library errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """
        Initialize the RaindropError.

        Args:
            message: Human-readable error message.
            status_code: Optional HTTP status code if applicable.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(RaindropError):
    """Raised when authentication fails (invalid or expired token)."""

    def __init__(self, message: str = "Invalid or expired access token") -> None:
        """Initialize AuthenticationError with default message."""
        super().__init__(message, status_code=401)


class RateLimitError(RaindropError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self, message: str = "API rate limit exceeded", retry_after: int | None = None
    ) -> None:
        """
        Initialize RateLimitError.

        Args:
            message: Human-readable error message.
            retry_after: Seconds to wait before retrying.
        """
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ValidationError(RaindropError):
    """Raised when request parameters are invalid."""

    def __init__(self, message: str) -> None:
        """Initialize ValidationError with the validation failure message."""
        super().__init__(message, status_code=400)


class NotFoundError(RaindropError):
    """Raised when a resource (e.g., collection) is not found."""

    def __init__(self, message: str = "Resource not found") -> None:
        """Initialize NotFoundError with default message."""
        super().__init__(message, status_code=404)


class NetworkError(RaindropError):
    """Raised when a network/connection error occurs."""

    def __init__(self, message: str = "Network connection error") -> None:
        """Initialize NetworkError with default message."""
        super().__init__(message, status_code=None)


class APIError(RaindropError):
    """Raised when an unexpected API error occurs."""

    def __init__(
        self, message: str = "Unexpected API error", status_code: int | None = None
    ) -> None:
        """Initialize APIError with message and optional status code."""
        super().__init__(message, status_code=status_code)
