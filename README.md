# BuyWhere Python SDK

Official Python SDK for the [BuyWhere](https://buywhere.ai) Product Catalog API — the agent-native product search API for Singapore.

## Installation

```bash
pip install buywhere-sdk
```

Or from source (clone `buywhere-catalog-api` and run from the `sdk/` directory):

```bash
pip install -e .
```

## Quickstart

```python
from buywhere_sdk import BuyWhere

client = BuyWhere(api_key="bw_live_your_key_here")

# Search products in Singapore
results = client.search("wireless headphones", limit=5)
for p in results.items:
    print(p.name, p.price, p.currency, p.source)
```

## Usage

### Sync client

```python
from buywhere_sdk import BuyWhere

client = BuyWhere(api_key="bw_live_your_key_here")

# Search products
results = client.search("iphone 15", limit=10)
for p in results.items:
    print(p.name, p.price, p.buy_url)

# Get product by ID (integer)
product = client.get_product(12345)
print(product.name, product.is_available)

# Find cheapest listing across all platforms
cheapest = client.best_price("Nintendo Switch OLED")
print(f"Best price: SGD {cheapest.price} at {cheapest.source}")

# List categories
cats = client.list_categories()
print(cats.total, "categories available")
```

### Async client

```python
import asyncio
from buywhere_sdk import AsyncBuyWhere

async def main():
    async with AsyncBuyWhere(api_key="bw_live_your_key_here") as client:
        results = await client.search("airfryer", limit=10)
        for p in results.items:
            print(p.name, p.price)

asyncio.run(main())
```

### Filtering

```python
results = client.search(
    "headphones",
    category="Electronics",
    min_price=50.0,
    max_price=300.0,
    source="shopee_sg",   # lazada_sg | shopee_sg | qoo10_sg | carousell_sg
    limit=20,
)
```

### Pagination

```python
results = client.search("laptop", limit=10)
print(f"Total: {results.total}, showing {len(results.items)}, has_more: {results.has_more}")

# Next page
next_page = client.search("laptop", limit=10, offset=10)
```

## Error handling

```python
from buywhere_sdk import BuyWhere
from buywhere_sdk.exceptions import NotFoundError, AuthenticationError, RateLimitError

client = BuyWhere(api_key="bw_live_your_key_here")

try:
    product = client.get_product(99999999)
except NotFoundError:
    print("Product not found")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limited — retry later")
```

## Configuration

| Parameter  | Default                    | Description                        |
|------------|----------------------------|------------------------------------|
| `api_key`  | *(required)*               | Your BuyWhere API key              |
| `base_url` | `https://api.buywhere.ai`  | Override for staging/local testing |
| `timeout`  | `30.0`                     | Request timeout in seconds         |

## LangChain integration

BuyWhere ships a first-class LangChain toolkit so your agents can search the catalog in natural language.

```bash
pip install "buywhere-sdk[langchain]"
```

```python
from buywhere_sdk.langchain import BuyWhereToolkit
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

toolkit = BuyWhereToolkit(api_key="bw_live_your_key_here")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

agent = initialize_agent(
    toolkit.get_tools(),
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

result = agent.run("Find the cheapest noise-cancelling headphones under SGD 200")
print(result)
```

## Requirements

- Python 3.10+
- `httpx >= 0.27`
- `pydantic >= 2.0`
- `langchain >= 0.3` *(optional — only for `BuyWhereToolkit`)*
