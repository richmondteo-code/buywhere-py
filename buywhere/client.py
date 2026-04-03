"""Synchronous BuyWhere client."""
from __future__ import annotations

from typing import Optional

import httpx

from buywhere._http import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, _build_headers
from buywhere.resources.categories import CategoriesResource
from buywhere.resources.products import ProductsResource


class BuyWhereClient:
    """Synchronous client for the BuyWhere Product Catalog API.

    Usage::

        from buywhere import BuyWhereClient

        client = BuyWhereClient(api_key="key_xxx")

        results = client.products.search(q="iphone 15", country="sg", limit=10)
        for r in results.results:
            print(r.title, r.price.amount, r.price.currency)

    Can be used as a context manager::

        with BuyWhereClient(api_key="key_xxx") as client:
            product = client.products.get("abc123")
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = httpx.Client(
            base_url=base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )
        self.products = ProductsResource(self._http)
        self.categories = CategoriesResource(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> "BuyWhereClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
