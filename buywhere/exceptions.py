"""BuyWhere SDK exceptions."""
from __future__ import annotations


class BuyWhereError(Exception):
    """Base exception for all BuyWhere SDK errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(BuyWhereError):
    """Raised when the API key is missing or invalid (HTTP 401/403)."""


class NotFoundError(BuyWhereError):
    """Raised when a requested resource does not exist (HTTP 404)."""


class RateLimitError(BuyWhereError):
    """Raised when the rate limit is exceeded (HTTP 429)."""


class APIError(BuyWhereError):
    """Raised for unexpected API responses (HTTP 5xx or unrecognised errors)."""
