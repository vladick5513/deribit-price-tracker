from httpx import AsyncClient

from app.prices.dao import PriceDAO
from tests.conftest import seed_prices

PRICES = "/prices"


async def test_list_prices_returns_all_for_ticker(client: AsyncClient, price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(100, "1"), (200, "2")])
    await seed_prices(price_dao, "eth_usd", [(100, "9")])

    response = await client.get(PRICES, params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == [
        {"ticker": "btc_usd", "price": 1.0, "timestamp": 100},
        {"ticker": "btc_usd", "price": 2.0, "timestamp": 200},
    ]


async def test_list_prices_empty_for_ticker_without_data(client: AsyncClient):
    response = await client.get(PRICES, params={"ticker": "eth_usd"})

    assert response.status_code == 200
    assert response.json() == []


async def test_ticker_is_required(client: AsyncClient):
    for path in (PRICES, f"{PRICES}/latest", f"{PRICES}/filter"):
        response = await client.get(path)
        assert response.status_code == 422, path


async def test_unknown_ticker_is_rejected(client: AsyncClient):
    response = await client.get(PRICES, params={"ticker": "doge_usd"})

    assert response.status_code == 422


async def test_latest_price(client: AsyncClient, price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(100, "1"), (300, "3"), (200, "2")])

    response = await client.get(f"{PRICES}/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == {"ticker": "btc_usd", "price": 3.0, "timestamp": 300}


async def test_latest_price_404_when_no_data(client: AsyncClient):
    response = await client.get(f"{PRICES}/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 404


async def test_filter_by_date_range(client: AsyncClient, price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(100, "1"), (200, "2"), (300, "3"), (400, "4")])

    response = await client.get(
        f"{PRICES}/filter", params={"ticker": "btc_usd", "date_from": 200, "date_to": 300}
    )

    assert response.status_code == 200
    assert [p["timestamp"] for p in response.json()] == [200, 300]


async def test_filter_requires_at_least_one_bound(client: AsyncClient):
    response = await client.get(f"{PRICES}/filter", params={"ticker": "btc_usd"})

    assert response.status_code == 422


async def test_filter_rejects_inverted_range(client: AsyncClient):
    response = await client.get(
        f"{PRICES}/filter", params={"ticker": "btc_usd", "date_from": 300, "date_to": 200}
    )

    assert response.status_code == 422
