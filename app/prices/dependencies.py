from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.enums import Ticker
from app.prices.dao import PriceDAO

SessionDep = Annotated[AsyncSession, Depends(get_session)]
TickerDep = Annotated[Ticker, Query(description="Тикер валюты", examples=["btc_usd"])]
DateQuery = Annotated[int | None, Query(ge=0, description="UNIX timestamp, включительно")]


def get_dao(session: SessionDep) -> PriceDAO:
    return PriceDAO(session)


DaoDep = Annotated[PriceDAO, Depends(get_dao)]
