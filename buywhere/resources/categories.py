"""Sync and async Categories resource."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from buywhere._http import (
    _async_backoff,
    _backoff,
    _raise_for_response,
    _should_retry,
)
from buywhere.models import Category, CategoryDetail

if TYPE_CHECKING:
    import httpx


class CategoriesResource:
    """Synchronous categories resource."""

    def __init__(self, http: "httpx.Client") -> None:
        self._http = http

    def list(self) -> List[Category]:
        """List all top-level product categories.

        Returns:
            List of :class:`~buywhere.models.Category` objects.
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get("/v1/categories")
                _raise_for_response(resp)
                data = resp.json()
                return [Category.model_validate(c) for c in data.get("categories", [])]
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def get(self, slug: str) -> CategoryDetail:
        """Get details and subcategories for a category slug.

        Args:
            slug: Category slug (e.g. ``"electronics"`` or ``"electronics/smartphones"``).

        Returns:
            :class:`~buywhere.models.CategoryDetail`
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get(f"/v1/categories/{slug}")
                _raise_for_response(resp)
                return CategoryDetail.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise


class AsyncCategoriesResource:
    """Asynchronous categories resource."""

    def __init__(self, http: "httpx.AsyncClient") -> None:
        self._http = http

    async def list(self) -> List[Category]:
        """Async version of :meth:`CategoriesResource.list`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get("/v1/categories")
                _raise_for_response(resp)
                data = resp.json()
                return [Category.model_validate(c) for c in data.get("categories", [])]
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def get(self, slug: str) -> CategoryDetail:
        """Async version of :meth:`CategoriesResource.get`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get(f"/v1/categories/{slug}")
                _raise_for_response(resp)
                return CategoryDetail.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise
