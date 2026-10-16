from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.enums import Ticker


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    DERIBIT_API_URL: str
    DERIBIT_TIMEOUT_SECONDS: float

    TICKERS: list[Ticker] = Field(default=[Ticker.BTC_USD, Ticker.ETH_USD])
    FETCH_INTERVAL_SECONDS: int

    LOG_LEVEL: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"


settings = Settings()
