"""LangChain tool integration for BuyWhere.

Install the optional extra to use this module::

    pip install buywhere-sdk[langchain]

Usage::

    from buywhere import BuyWhereClient
    from buywhere.tools import BuyWhereTool

    client = BuyWhereClient(api_key="bw_...")
    tool = BuyWhereTool(client=client, country="sg")

    # Use directly
    result = tool.run("wireless headphones under $100")

    # Or attach to a LangChain agent
    from langchain.agents import initialize_agent, AgentType
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini")
    agent = initialize_agent([tool], llm, agent=AgentType.OPENAI_FUNCTIONS)
    agent.run("Find me the cheapest wireless headphones in Singapore")
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Type

try:
    from langchain_core.tools import BaseTool
    from pydantic import BaseModel, Field
except ImportError as exc:
    raise ImportError(
        "LangChain integration requires langchain-core. "
        "Install it with: pip install buywhere-sdk[langchain]"
    ) from exc

if TYPE_CHECKING:
    from buywhere.client import BuyWhereClient


class _SearchInput(BaseModel):
    query: str = Field(description="Product search query in natural language")
    country: str = Field(default="sg", description="Country code (default: sg)")
    category: Optional[str] = Field(default=None, description="Category slug filter")
    price_min: Optional[float] = Field(default=None, description="Minimum price in SGD")
    price_max: Optional[float] = Field(default=None, description="Maximum price in SGD")
    limit: int = Field(default=5, description="Number of results to return (1-20)")


class BuyWhereTool(BaseTool):
    """LangChain tool that searches the BuyWhere product catalog.

    Give this tool to any LangChain agent and it can search Singapore's
    product catalog across Shopee, Lazada, and Qoo10.

    Example::

        client = BuyWhereClient(api_key="bw_...")
        tool = BuyWhereTool(client=client)
        agent = initialize_agent([tool], llm, agent=AgentType.OPENAI_FUNCTIONS)
        agent.run("Find me affordable noise-cancelling headphones")
    """

    name: str = "buywhere_product_search"
    description: str = (
        "Search BuyWhere's Singapore product catalog. "
        "Use this to find products, compare prices, and check availability. "
        "Input: a natural-language product query."
    )
    args_schema: Type[_SearchInput] = _SearchInput

    client: object  # BuyWhereClient — typed as object to avoid Pydantic issues
    country: str = "sg"
    default_limit: int = 5

    class Config:
        arbitrary_types_allowed = True

    def _run(
        self,
        query: str,
        country: str = "sg",
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        limit: int = 5,
    ) -> str:
        from buywhere.client import BuyWhereClient
        assert isinstance(self.client, BuyWhereClient)

        resp = self.client.products.search(
            q=query,
            country=country or self.country,
            category=category,
            price_min=price_min,
            price_max=price_max,
            limit=min(limit, 20),
        )

        if not resp.results:
            return f"No products found for '{query}'."

        lines = [f"Found {resp.total_estimated} products for '{query}' (showing {len(resp.results)}):\n"]
        for i, r in enumerate(resp.results, 1):
            lines.append(
                f"{i}. {r.title}\n"
                f"   Price: {r.price.currency} {r.price.amount:.2f}"
                + (f" (was {r.price.original_amount:.2f})" if r.price.original_amount else "")
                + f"\n   Platform: {r.merchant.platform} | Merchant: {r.merchant.name}"
                + f"\n   In stock: {r.availability.in_stock}"
                + f"\n   URL: {r.source_url}\n"
            )

        if resp.has_more:
            lines.append(f"(More results available — refine your query or set a higher limit)")

        return "\n".join(lines)

    async def _arun(
        self,
        query: str,
        country: str = "sg",
        category: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        limit: int = 5,
    ) -> str:
        from buywhere.async_client import AsyncBuyWhereClient
        assert isinstance(self.client, AsyncBuyWhereClient)

        resp = await self.client.products.search(
            q=query,
            country=country or self.country,
            category=category,
            price_min=price_min,
            price_max=price_max,
            limit=min(limit, 20),
        )

        if not resp.results:
            return f"No products found for '{query}'."

        lines = [f"Found {resp.total_estimated} products for '{query}' (showing {len(resp.results)}):\n"]
        for i, r in enumerate(resp.results, 1):
            lines.append(
                f"{i}. {r.title}\n"
                f"   Price: {r.price.currency} {r.price.amount:.2f}"
                + (f" (was {r.price.original_amount:.2f})" if r.price.original_amount else "")
                + f"\n   Platform: {r.merchant.platform} | Merchant: {r.merchant.name}"
                + f"\n   In stock: {r.availability.in_stock}"
                + f"\n   URL: {r.source_url}\n"
            )

        if resp.has_more:
            lines.append(f"(More results available — refine your query or set a higher limit)")

        return "\n".join(lines)
