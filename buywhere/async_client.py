"""Asynchronous BuyWhere client."""
from __future__ import annotations

import httpx

from buywhere._http import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, _build_headers
from buywhere.resources.categories import AsyncCategoriesResource
from buywhere.resources.products import AsyncProductsResource


class AsyncBuyWhereClient:
    """Asynchronous client for the BuyWhere Product Catalog API.

    Usage::

        import asyncio
        from buywhere import AsyncBuyWhereClient

        async def main():
            async with AsyncBuyWhereClient(api_key="key_xxx") as client:
                results = await client.products.search(q="iphone 15", country="sg")
                for r in results.results:
                    print(r.title, r.price.amount)

        asyncio.run(main())
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = httpx.AsyncClient(
            base_url=base_url,
            headers=_build_headers(api_key),
            timeout=timeout,
        )
        self.products = AsyncProductsResource(self._http)
        self.categories = AsyncCategoriesResource(self._http)

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.aclose()

    async def __aenter__(self) -> "AsyncBuyWhereClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()
