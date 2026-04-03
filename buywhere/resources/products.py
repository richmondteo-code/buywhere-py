"""Sync and async Products resource."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from buywhere._http import (
    MAX_RETRIES,
    _async_backoff,
    _backoff,
    _raise_for_response,
    _should_retry,
    clean_params,
)
from buywhere.models import (
    BulkSearchResponse,
    CompareProductsResponse,
    NLQueryResponse,
    PriceCompareResponse,
    Product,
    SearchResponse,
    SimilarProductsResponse,
    TrendingProductsResponse,
)

if TYPE_CHECKING:
    import httpx


class ProductsResource:
    """Synchronous products resource."""

    def __init__(self, http: "httpx.Client") -> None:
        self._http = http

    def search(
        self,
        q: str,
        *,
        country: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        availability: str = "in_stock",
        sort: str = "relevance",
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> SearchResponse:
        """Search products.

        Args:
            q: Keyword or natural-language query.
            country: Country code hint (e.g. ``"sg"``). Informational for now.
            category: Category slug filter (e.g. ``"electronics/smartphones"``).
            platform: Platform filter: ``lazada`` | ``shopee`` | ``carousell`` |
                ``courts`` | ``fairprice`` | ``redmart`` | ``qoo10`` | ``all``.
            min_price: Minimum price in SGD (inclusive).
            max_price: Maximum price in SGD (inclusive).
            availability: ``"in_stock"`` (default) or ``"all"``.
            sort: ``"relevance"`` | ``"price_asc"`` | ``"price_desc"`` | ``"newest"`` | ``"rating"``.
            limit: Results per page (1–50, default 10).
            cursor: Pagination cursor from a previous response.

        Returns:
            :class:`~buywhere.models.SearchResponse`
        """
        params = clean_params({
            "q": q,
            "category": category,
            "platform": platform,
            "min_price": min_price,
            "max_price": max_price,
            "availability": availability,
            "sort": sort,
            "limit": limit,
            "cursor": cursor,
        })
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get("/v1/products/search", params=params)
                _raise_for_response(resp)
                return SearchResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def get(self, product_id: str) -> Product:
        """Fetch a single product by ID.

        Args:
            product_id: The BuyWhere product identifier.

        Returns:
            :class:`~buywhere.models.Product`
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get(f"/v1/products/{product_id}")
                _raise_for_response(resp)
                return Product.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def compare_prices(self, product_id: str) -> PriceCompareResponse:
        """Compare prices across merchants for a product.

        Args:
            product_id: The BuyWhere product identifier.

        Returns:
            :class:`~buywhere.models.PriceCompareResponse`
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get(f"/v1/products/{product_id}/prices")
                _raise_for_response(resp)
                return PriceCompareResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise


    def compare(self, product_ids: List[str]) -> CompareProductsResponse:
        """Compare 2–5 products side-by-side.

        Returns structured differentiators, price range, price trends, and
        affiliate URLs — purpose-built for AI agent decision-making.

        Args:
            product_ids: List of 2–5 BuyWhere product identifiers.

        Returns:
            :class:`~buywhere.models.CompareProductsResponse`
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.post(
                    "/v1/products/compare",
                    json={"product_ids": product_ids},
                )
                _raise_for_response(resp)
                return CompareProductsResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def query(
        self,
        query: str,
        *,
        context: Optional[dict] = None,
        limit: int = 10,
    ) -> NLQueryResponse:
        """Natural-language product query.

        Accepts a free-text query, extracts structured intent (price range,
        category, sort preference, sentiment), and returns matching products
        with an ``interpreted_as`` object explaining the parsing.

        Args:
            query: Free-text natural-language query, e.g.
                ``"gaming laptop under $2000 with good reviews"``.
            context: Optional context dict, e.g. ``{"country": "sg"}``.
            limit: Number of products to return (1–50, default 10).

        Returns:
            :class:`~buywhere.models.NLQueryResponse`

        Example::

            results = client.products.query("birthday gift for mum, around $50")
            print(results.interpreted_as.sentiment)   # "gift"
            print(results.interpreted_as.max_price)   # 62.5
            for p in results.products:
                print(p.title, p.price.amount)
        """
        payload: dict = {"query": query, "limit": limit}
        if context is not None:
            payload["context"] = context
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.post("/v1/products/query", json=payload)
                _raise_for_response(resp)
                return NLQueryResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def similar(self, product_id: str) -> SimilarProductsResponse:
        """Return similar/recommended products for a given product ID.

        Primary source: co-occurrence data (products frequently compared together).
        Fallback: same category + similar price range (±30%) from a different platform.

        Args:
            product_id: The BuyWhere product identifier.

        Returns:
            :class:`~buywhere.models.SimilarProductsResponse` — up to 5 products with
            ``similarity_reason``: ``"frequently_compared"`` | ``"same_category"`` | ``"similar_price"``
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get(f"/v1/products/{product_id}/similar")
                _raise_for_response(resp)
                return SimilarProductsResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def trending(
        self,
        *,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> TrendingProductsResponse:
        """Return the most-queried products in the last 24 hours.

        Args:
            category: Optional category slug prefix filter (e.g. ``"electronics"``).
            limit: Number of products to return (1–50, default 10).

        Returns:
            :class:`~buywhere.models.TrendingProductsResponse`
        """
        params = {"limit": limit}
        if category is not None:
            params["category"] = category
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.get("/v1/products/trending", params=params)
                _raise_for_response(resp)
                return TrendingProductsResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise

    def search_bulk(self, queries: List[dict]) -> BulkSearchResponse:
        """Execute up to 10 product search queries in a single request.

        Sub-queries run in parallel server-side — response time is approximately
        equal to a single query. Each sub-query counts as 1 query against your
        rate limit.

        Args:
            queries: List of up to 10 query dicts. Each dict supports the same
                fields as :meth:`search`: ``q`` (required), ``category``,
                ``min_price``, ``max_price``, ``platform``, ``availability``,
                ``sort``, ``is_deal``, ``limit``.

        Returns:
            :class:`~buywhere.models.BulkSearchResponse`

        Example::

            results = client.products.search_bulk([
                {"q": "wireless headphones", "max_price": 100, "limit": 3},
                {"q": "laptop stand", "category": "accessories", "limit": 3},
                {"q": "mechanical keyboard", "platform": "lazada", "limit": 3},
            ])
            for r in results.results:
                print(r.query, r.total)
        """
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = self._http.post(
                    "/v1/products/search/bulk",
                    json={"queries": queries},
                )
                _raise_for_response(resp)
                return BulkSearchResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    _backoff(attempt)
                else:
                    raise


class AsyncProductsResource:
    """Asynchronous products resource."""

    def __init__(self, http: "httpx.AsyncClient") -> None:
        self._http = http

    async def search(
        self,
        q: str,
        *,
        country: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        availability: str = "in_stock",
        sort: str = "relevance",
        limit: int = 10,
        cursor: Optional[str] = None,
    ) -> SearchResponse:
        """Async version of :meth:`ProductsResource.search`."""
        params = clean_params({
            "q": q,
            "category": category,
            "platform": platform,
            "min_price": min_price,
            "max_price": max_price,
            "availability": availability,
            "sort": sort,
            "limit": limit,
            "cursor": cursor,
        })
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get("/v1/products/search", params=params)
                _raise_for_response(resp)
                return SearchResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def get(self, product_id: str) -> Product:
        """Async version of :meth:`ProductsResource.get`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get(f"/v1/products/{product_id}")
                _raise_for_response(resp)
                return Product.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def compare_prices(self, product_id: str) -> PriceCompareResponse:
        """Async version of :meth:`ProductsResource.compare_prices`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get(f"/v1/products/{product_id}/prices")
                _raise_for_response(resp)
                return PriceCompareResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def compare(self, product_ids: List[str]) -> CompareProductsResponse:
        """Async version of :meth:`ProductsResource.compare`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.post(
                    "/v1/products/compare",
                    json={"product_ids": product_ids},
                )
                _raise_for_response(resp)
                return CompareProductsResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def query(
        self,
        query: str,
        *,
        context: Optional[dict] = None,
        limit: int = 10,
    ) -> NLQueryResponse:
        """Async version of :meth:`ProductsResource.query`."""
        payload: dict = {"query": query, "limit": limit}
        if context is not None:
            payload["context"] = context
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.post("/v1/products/query", json=payload)
                _raise_for_response(resp)
                return NLQueryResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def similar(self, product_id: str) -> SimilarProductsResponse:
        """Async version of :meth:`ProductsResource.similar`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get(f"/v1/products/{product_id}/similar")
                _raise_for_response(resp)
                return SimilarProductsResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def trending(
        self,
        *,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> TrendingProductsResponse:
        """Async version of :meth:`ProductsResource.trending`."""
        params = {"limit": limit}
        if category is not None:
            params["category"] = category
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.get("/v1/products/trending", params=params)
                _raise_for_response(resp)
                return TrendingProductsResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise

    async def search_bulk(self, queries: List[dict]) -> BulkSearchResponse:
        """Async version of :meth:`ProductsResource.search_bulk`."""
        attempt = 0
        while True:
            attempt += 1
            try:
                resp = await self._http.post(
                    "/v1/products/search/bulk",
                    json={"queries": queries},
                )
                _raise_for_response(resp)
                return BulkSearchResponse.model_validate(resp.json())
            except Exception as exc:
                if _should_retry(exc, attempt):
                    await _async_backoff(attempt)
                else:
                    raise
