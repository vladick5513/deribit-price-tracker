from pydantic import BaseModel, ConfigDict, Field

from app.enums import Ticker


class PriceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: Ticker
    price: float
    timestamp: int = Field(description="UNIX timestamp (секунды, UTC)")
