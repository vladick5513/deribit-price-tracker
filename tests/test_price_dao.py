from decimal import Decimal

from app.prices.dao import PriceDAO
from tests.conftest import seed_prices


async def test_find_by_ticker_returns_only_that_ticker_sorted(price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(300, "3"), (100, "1"), (200, "2")])
    await seed_prices(price_dao, "eth_usd", [(150, "9")])

    rows = await price_dao.find_by_ticker("btc_usd")

    assert [(r.timestamp, r.price) for r in rows] == [
        (100, Decimal("1")),
        (200, Decimal("2")),
        (300, Decimal("3")),
    ]


async def test_find_latest_picks_max_timestamp(price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(300, "3"), (100, "1"), (200, "2")])

    latest = await price_dao.find_latest("btc_usd")

    assert latest is not None
    assert latest.timestamp == 300
    assert latest.price == Decimal("3")


async def test_find_latest_returns_none_for_unknown_ticker(price_dao: PriceDAO):
    assert await price_dao.find_latest("btc_usd") is None


async def test_find_in_range_is_inclusive_on_both_ends(price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(100, "1"), (200, "2"), (300, "3"), (400, "4")])

    rows = await price_dao.find_by_ticker_in_range("btc_usd", date_from=200, date_to=300)

    assert [r.timestamp for r in rows] == [200, 300]


async def test_find_in_range_with_open_bounds(price_dao: PriceDAO):
    await seed_prices(price_dao, "btc_usd", [(100, "1"), (200, "2"), (300, "3")])

    only_from = await price_dao.find_by_ticker_in_range("btc_usd", date_from=200)
    only_to = await price_dao.find_by_ticker_in_range("btc_usd", date_to=200)

    assert [r.timestamp for r in only_from] == [200, 300]
    assert [r.timestamp for r in only_to] == [100, 200]
