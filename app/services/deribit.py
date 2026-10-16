from decimal import Decimal
from types import TracebackType
from typing import Any, Self

import aiohttp

from app.services.exceptions import (
    DeribitApiError,
    DeribitResponseError,
    DeribitTransportError,
)


class DeribitClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0):
        self._base_url = base_url.rstrip("/")
        self._timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def get_index_price(self, index_name: str) -> Decimal:
        payload = await self._get("public/get_index_price", {"index_name": index_name})
        return self._parse_index_price(payload)

    async def _get(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        if self._session is None:
            raise RuntimeError("DeribitClient must be used as an async context manager")

        url = f"{self._base_url}/{method}"
        try:
            async with self._session.get(url, params=params) as response:
                if response.status != 200:
                    raise DeribitTransportError(f"{method}: HTTP {response.status}")
                payload = await response.json()
        except (aiohttp.ClientError, TimeoutError) as exc:
            raise DeribitTransportError(f"{method}: transport error: {exc}") from exc

        if "error" in payload:
            error = payload["error"] or {}
            raise DeribitApiError(method, error.get("code"), error.get("message", str(error)))
        return payload

    @staticmethod
    def _parse_index_price(payload: dict[str, Any]) -> Decimal:
        try:
            raw = payload["result"]["index_price"]
        except (KeyError, TypeError) as exc:
            raise DeribitResponseError(f"unexpected response shape: {payload!r}") from exc
        if raw is None:
            raise DeribitResponseError("index_price is empty")
        return Decimal(str(raw))
