"""Shared HTTP helpers: request building, error mapping, retry logic."""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

import httpx

from buywhere.exceptions import (
    APIError,
    AuthenticationError,
    BuyWhereError,
    NotFoundError,
    RateLimitError,
)

DEFAULT_BASE_URL = "https://api.buywhere.io"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.5  # seconds


def _build_headers(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "buywhere-python/0.1.0",
    }


def _raise_for_response(response: httpx.Response) -> None:
    if response.is_success:
        return
    status = response.status_code
    try:
        detail = response.json().get("detail") or response.text
        if isinstance(detail, dict):
            detail = detail.get("message") or str(detail)
    except Exception:
        detail = response.text or f"HTTP {status}"

    if status in (401, 403):
        raise AuthenticationError(detail, status_code=status)
    if status == 404:
        raise NotFoundError(detail, status_code=status)
    if status == 429:
        raise RateLimitError(detail, status_code=status)
    raise APIError(detail, status_code=status)


def _should_retry(exc: Exception, attempt: int) -> bool:
    if attempt >= MAX_RETRIES:
        return False
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, APIError) and exc.status_code and exc.status_code >= 500:
        return True
    if isinstance(exc, (httpx.ConnectError, httpx.TimeoutException)):
        return True
    return False


def _backoff(attempt: int) -> None:
    time.sleep(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)))


async def _async_backoff(attempt: int) -> None:
    import asyncio
    await asyncio.sleep(RETRY_BACKOFF_BASE * (2 ** (attempt - 1)))


def clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Drop None values from a query-params dict."""
    return {k: v for k, v in params.items() if v is not None}
