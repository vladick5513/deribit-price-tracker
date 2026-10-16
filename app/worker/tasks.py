import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker

from app.database import create_task_engine
from app.services.deribit import DeribitClient
from app.services.price_collector import PriceCollector
from app.settings import settings
from app.worker.celery_app import celery_app


async def _fetch_prices() -> int:
    engine = create_task_engine()
    try:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
        async with (
            DeribitClient(settings.DERIBIT_API_URL, settings.DERIBIT_TIMEOUT_SECONDS) as client,
            session_factory() as session,
        ):
            collector = PriceCollector(client, session)
            stored = await collector.collect(settings.TICKERS)
            await session.commit()
            return stored
    finally:
        await engine.dispose()


@celery_app.task(name="app.worker.tasks.fetch_prices")
def fetch_prices() -> int:
    return asyncio.run(_fetch_prices())
