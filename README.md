# BuyWhere Python SDK

Official Python SDK for the [BuyWhere](https://buywhere.io) Product Catalog API — the agent-native product search API for Singapore.

## Installation

```bash
pip install buywhere-sdk
```

Or from source:

```bash
pip install -e sdk/python/
```

## Quickstart

```python
from buywhere import BuyWhereClient

client = BuyWhereClient(api_key="key_xxx", base_url="http://143.198.87.39:8000")

# Search products in Singapore
results = client.products.search(q="iphone 15", country="sg", limit=10)
for r in results.results:
    print(r.title, r.price.amount, r.price.currency)
```

## Usage

### Sync client

```python
from buywhere import BuyWhereClient

client = BuyWhereClient(api_key="key_xxx")

# Search products
results = client.products.search(q="iphone 15", country="sg", limit=10)

# Get product by ID
product = client.products.get(product_id="abc123")

# Compare prices across merchants
prices = client.products.compare_prices(product_id="abc123")
print(prices.best_price)

# List categories
categories = client.categories.list()

# Category detail
electronics = client.categories.get("electronics")
print(electronics.subcategories)
```

### Async client

```python
import asyncio
from buywhere import AsyncBuyWhereClient

async def main():
    async with AsyncBuyWhereClient(api_key="key_xxx") as client:
        results = await client.products.search(q="airfryer", country="sg")
        for r in results.results:
            print(r.title, r.price.amount)

asyncio.run(main())
```

### Pagination

```python
results = client.products.search(q="laptop", limit=10)
while results.has_more:
    results = client.products.search(q="laptop", limit=10, cursor=results.next_cursor)
    for r in results.results:
        print(r.title)
```

### Filtering and sorting

```python
results = client.products.search(
    q="headphones",
    category="electronics/audio",
    price_min=50.0,
    price_max=300.0,
    platform="shopee",
    sort="price_asc",
    limit=20,
)
```

## Error handling

```python
from buywhere import BuyWhereClient, NotFoundError, AuthenticationError, RateLimitError

client = BuyWhereClient(api_key="key_xxx")

try:
    product = client.products.get("does-not-exist")
except NotFoundError:
    print("Product not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limited — retry later")
```

## Configuration

| Parameter  | Default                      | Description                       |
|------------|------------------------------|-----------------------------------|
| `api_key`  | *(required)*                 | Your BuyWhere API key             |
| `base_url` | `https://api.buywhere.io`    | Override for staging/local        |
| `timeout`  | `30.0`                       | Request timeout in seconds        |

## LangChain integration

BuyWhere ships a first-class LangChain tool so your agents can search the catalog in natural language.

```bash
pip install buywhere-sdk[langchain]
```

```python
from buywhere import BuyWhereClient, BuyWhereTool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

client = BuyWhereClient(api_key="bw_...")
tool = BuyWhereTool(client=client, country="sg")
agent = initialize_agent([tool], ChatOpenAI(model="gpt-4o-mini"), agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
agent.run("Find me noise-cancelling headphones under SGD 200 on Shopee")
```

The tool exposes structured inputs so the LLM can pass filters (category, price range, platform) directly:

```python
# Use the tool directly without an agent
result = tool.run("wireless earbuds")
print(result)
# Found 48 products for 'wireless earbuds' (showing 5):
# 1. Sony WF-1000XM5
#    Price: SGD 279.00 (was 349.00)
#    Platform: shopee | Merchant: Sony Official Store
#    ...
```

## Requirements

- Python 3.9+
- `httpx >= 0.25`
- `pydantic >= 2.0`
- `langchain-core >= 0.1` *(optional — only for `BuyWhereTool`)*
