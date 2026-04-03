"""Pydantic models for BuyWhere API responses."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------

class PriceInfo(BaseModel):
    amount: float
    currency: str = "SGD"
    original_amount: Optional[float] = None
    discount_pct: Optional[float] = None


class MerchantInfo(BaseModel):
    merchant_id: str
    name: str
    platform: str
    rating: Optional[float] = None
    review_count: Optional[int] = None


class DeliveryInfo(BaseModel):
    next_day_available: bool = False
    earliest_date: Optional[str] = None
    shipping_fee: float = 0.0
    free_shipping: bool = False


class AvailabilityInfo(BaseModel):
    in_stock: bool
    stock_level: Optional[str] = None
    delivery: Optional[DeliveryInfo] = None


class ImageInfo(BaseModel):
    url: str
    role: str = "primary"


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

class SearchResult(BaseModel):
    product_id: str
    title: str
    description_short: Optional[str] = None
    category: str
    price: PriceInfo
    merchant: MerchantInfo
    availability: AvailabilityInfo
    images: List[ImageInfo] = []
    relevance_score: float = 1.0
    source_url: str
    last_synced_at: str


class SearchResponse(BaseModel):
    query: Optional[str] = None
    total_estimated: int
    cursor: Optional[str] = None
    next_cursor: Optional[str] = None
    has_more: bool = False
    results: List[SearchResult]


# ---------------------------------------------------------------------------
# Natural-language query (BUY-193)
# ---------------------------------------------------------------------------

class InterpretedAs(BaseModel):
    categories: List[str] = []
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort: str = "relevance"
    sentiment: Optional[str] = None
    brand_mentions: List[str] = []
    platform: Optional[str] = None
    filters_applied: Dict[str, Any] = {}


class NLQueryResponse(BaseModel):
    object: str = "nl_query_result"
    original_query: str
    interpreted_as: InterpretedAs
    products: List[SearchResult]
    total: int
    has_more: bool = False
    next_cursor: Optional[str] = None
    suggested_refinements: List[str] = []


# ---------------------------------------------------------------------------
# Product detail
# ---------------------------------------------------------------------------

class ReviewsSummary(BaseModel):
    average_rating: Optional[float] = None
    total_reviews: Optional[int] = None
    sentiment: Optional[str] = None
    top_positive: Optional[str] = None
    top_negative: Optional[str] = None


class Product(BaseModel):
    product_id: str
    title: str
    description_full: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    category: str
    tags: List[str] = []
    price: PriceInfo
    merchant: MerchantInfo
    availability: AvailabilityInfo
    images: List[ImageInfo] = []
    reviews_summary: Optional[ReviewsSummary] = None
    source_url: str
    last_synced_at: str


# ---------------------------------------------------------------------------
# Price compare
# ---------------------------------------------------------------------------

class ListingPrice(BaseModel):
    amount: float
    currency: str = "SGD"
    shipping_fee: float = 0.0
    total: float


class ListingAvailability(BaseModel):
    in_stock: bool
    next_day_available: bool = False
    earliest_date: Optional[str] = None


class Listing(BaseModel):
    listing_id: str
    merchant: MerchantInfo
    price: ListingPrice
    availability: ListingAvailability
    source_url: str
    last_synced_at: str


class BestOption(BaseModel):
    listing_id: str
    total: float
    currency: str = "SGD"
    rationale: Optional[str] = None


class PriceCompareResponse(BaseModel):
    product_id: str
    canonical_title: str
    listings: List[Listing]
    best_price: Optional[BestOption] = None
    best_value: Optional[BestOption] = None


# ---------------------------------------------------------------------------
# Product comparison
# ---------------------------------------------------------------------------

class CompareProductItem(BaseModel):
    product_id: str
    title: str
    category: str
    price: PriceInfo
    merchant: MerchantInfo
    availability: AvailabilityInfo
    images: List[ImageInfo] = []
    specifications: Optional[Dict[str, Any]] = None
    tags: List[str] = []
    reviews_summary: Optional[ReviewsSummary] = None
    price_trend: Optional[str] = None
    affiliate_url: Optional[str] = None
    source_url: str
    last_synced_at: str


class PriceRange(BaseModel):
    min: float
    max: float
    currency: str = "SGD"


class ComparisonSummary(BaseModel):
    cheapest: str
    best_value: str
    price_range: PriceRange
    common_features: List[str] = []
    differentiators: Dict[str, List[str]] = {}


class CompareProductsResponse(BaseModel):
    object: str = "comparison"
    products: List[CompareProductItem]
    comparison: ComparisonSummary


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

class PopularFilter(BaseModel):
    parameter: str
    label: str
    value: Any


class Category(BaseModel):
    slug: str
    name: str
    product_count: int


class CategoryDetail(BaseModel):
    slug: str
    name: str
    product_count: int
    subcategories: List[Category] = []
    popular_filters: List[PopularFilter] = []


# ---------------------------------------------------------------------------
# Recommendations (BUY-197)
# ---------------------------------------------------------------------------

class SimilarProduct(BaseModel):
    product_id: str
    title: str
    price: PriceInfo
    merchant: MerchantInfo
    similarity_reason: str  # "frequently_compared" | "same_category" | "similar_price"
    affiliate_url: Optional[str] = None
    source_url: str


class SimilarProductsResponse(BaseModel):
    object: str = "similar_products"
    product_id: str
    products: List[SimilarProduct]


class TrendingProduct(BaseModel):
    product_id: str
    title: str
    price: PriceInfo
    merchant: MerchantInfo
    query_count: int
    affiliate_url: Optional[str] = None
    source_url: str


class TrendingProductsResponse(BaseModel):
    object: str = "trending_products"
    period: str = "24h"
    products: List[TrendingProduct]


# --- Bulk search (BUY-200) ---

class BulkSearchQueryResult(BaseModel):
    query: str
    products: List[SearchResult]
    total: int


class BulkSearchResponse(BaseModel):
    object: str = "bulk_search_result"
    results: List[BulkSearchQueryResult]
    queries_consumed: int
