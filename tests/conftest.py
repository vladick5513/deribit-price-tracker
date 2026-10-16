from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.main import app
from app.prices.dao import PriceDAO


@pytest.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """Чистая in-memory SQLite на каждый тест. Транзакция откатывается в конце"""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()
    await engine.dispose()


@pytest.fixture
def price_dao(session: AsyncSession) -> PriceDAO:
    return PriceDAO(session)


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """HTTP-клиент поверх приложения с подменённой сессией БД"""

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


async def seed_prices(dao: PriceDAO, ticker: str, points: list[tuple[int, str]]) -> None:
    await dao.add_many(
        [{"ticker": ticker, "price": Decimal(price), "timestamp": ts} for ts, price in points]
    )
