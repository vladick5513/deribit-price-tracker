from sqlalchemy import select

from app.dao.base import BaseDAO
from app.prices.models import Price


class PriceDAO(BaseDAO[Price]):
    model = Price

    async def find_by_ticker(self, ticker: str) -> list[Price]:
        result = await self.session.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.asc(), Price.id.asc())
        )
        return list(result.scalars().all())

    async def find_latest(self, ticker: str) -> Price | None:
        result = await self.session.execute(
            select(Price)
            .where(Price.ticker == ticker)
            .order_by(Price.timestamp.desc(), Price.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def find_by_ticker_in_range(
        self,
        ticker: str,
        date_from: int | None = None,
        date_to: int | None = None,
    ) -> list[Price]:
        query = select(Price).where(Price.ticker == ticker)
        if date_from is not None:
            query = query.where(Price.timestamp >= date_from)
        if date_to is not None:
            query = query.where(Price.timestamp <= date_to)
        result = await self.session.execute(query.order_by(Price.timestamp.asc(), Price.id.asc()))
        return list(result.scalars().all())
