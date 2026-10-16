from fastapi import APIRouter, HTTPException, status

from app.prices.dependencies import DaoDep, DateQuery, TickerDep
from app.prices.schemas import PriceRead

router = APIRouter(prefix="/prices", tags=["Цены"])


@router.get("", response_model=list[PriceRead], summary="Все сохранённые цены по тикеру")
async def list_prices(ticker: TickerDep, dao: DaoDep):
    return await dao.find_by_ticker(ticker)


@router.get("/latest", response_model=PriceRead, summary="Последняя цена по тикеру")
async def get_latest_price(ticker: TickerDep, dao: DaoDep):
    price = await dao.find_latest(ticker)
    if price is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No prices stored for {ticker}")
    return price


@router.get("/filter", response_model=list[PriceRead], summary="Цены по тикеру с фильтром по дате")
async def filter_prices(
    ticker: TickerDep,
    dao: DaoDep,
    date_from: DateQuery = None,
    date_to: DateQuery = None,
):
    if date_from is None and date_to is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, "date_from or date_to is required"
        )
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "date_from must be <= date_to")
    return await dao.find_by_ticker_in_range(ticker, date_from=date_from, date_to=date_to)
