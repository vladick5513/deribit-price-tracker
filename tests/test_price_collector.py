from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Ticker
from app.prices.dao import PriceDAO
from app.services.deribit import DeribitClient
from app.services.exceptions import DeribitError
from app.services.price_collector import PriceCollector


class FakeDeribitClient(DeribitClient):
    def __init__(self, prices: dict[str, Decimal | Exception]):
        super().__init__("https://fake")
        self._prices = prices

    async def get_index_price(self, index_name: str) -> Decimal:
        value = self._prices[index_name]
        if isinstance(value, Exception):
            raise value
        return value


async def test_collect_stores_all_tickers_with_same_timestamp(
    session: AsyncSession, price_dao: PriceDAO
):
    client = FakeDeribitClient({"btc_usd": Decimal("50000.5"), "eth_usd": Decimal("3000.25")})

    stored = await PriceCollector(client, session).collect([Ticker.BTC_USD, Ticker.ETH_USD])

    assert stored == 2
    btc = await price_dao.find_by_ticker("btc_usd")
    eth = await price_dao.find_by_ticker("eth_usd")
    assert [p.price for p in btc] == [Decimal("50000.5")]
    assert [p.price for p in eth] == [Decimal("3000.25")]
    assert btc[0].timestamp == eth[0].timestamp > 0


async def test_collect_skips_failed_ticker_and_keeps_others(
    session: AsyncSession, price_dao: PriceDAO
):
    client = FakeDeribitClient({"btc_usd": DeribitError("boom"), "eth_usd": Decimal("3000")})

    stored = await PriceCollector(client, session).collect([Ticker.BTC_USD, Ticker.ETH_USD])

    assert stored == 1
    assert await price_dao.find_by_ticker("btc_usd") == []
    assert len(await price_dao.find_by_ticker("eth_usd")) == 1


async def test_collect_returns_zero_when_everything_failed(
    session: AsyncSession, price_dao: PriceDAO
):
    client = FakeDeribitClient({"btc_usd": DeribitError("boom")})

    stored = await PriceCollector(client, session).collect([Ticker.BTC_USD])

    assert stored == 0
    assert await price_dao.find_by_ticker("btc_usd") == []
