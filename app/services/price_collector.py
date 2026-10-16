import time
from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import Ticker
from app.logger import logger
from app.prices.dao import PriceDAO
from app.services.deribit import DeribitClient
from app.services.exceptions import DeribitError


class PriceCollector:
    def __init__(self, client: DeribitClient, session: AsyncSession):
        self._client = client
        self._prices = PriceDAO(session)

    async def collect(self, tickers: Iterable[Ticker]) -> int:
        timestamp = int(time.time())
        rows = []
        for ticker in tickers:
            try:
                price = await self._client.get_index_price(ticker)
            except DeribitError as exc:
                logger.warning("skip %s: %s", ticker, exc)
                continue
            rows.append({"ticker": ticker.value, "price": price, "timestamp": timestamp})

        if not rows:
            logger.warning("no prices fetched at %s", timestamp)
            return 0

        await self._prices.add_many(rows)
        logger.info("stored %d prices at %s", len(rows), timestamp)
        return len(rows)
