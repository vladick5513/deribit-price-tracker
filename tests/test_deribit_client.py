import asyncio
from collections.abc import AsyncIterator
from decimal import Decimal
from typing import Any

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.services.deribit import DeribitClient
from app.services.exceptions import (
    DeribitApiError,
    DeribitError,
    DeribitResponseError,
    DeribitTransportError,
)


class FakeDeribit:
    def __init__(self) -> None:
        self.payload: Any = {"result": {"index_price": 0}}
        self.status = 200
        self.delay = 0.0
        self.requests: list[dict[str, str]] = []

    async def handle(self, request: web.Request) -> web.Response:
        self.requests.append(dict(request.query))
        if self.delay:
            await asyncio.sleep(self.delay)
        return web.json_response(self.payload, status=self.status)

    def app(self) -> web.Application:
        app = web.Application()
        app.router.add_get("/api/v2/public/get_index_price", self.handle)
        return app


@pytest.fixture
async def fake_deribit() -> AsyncIterator[tuple[FakeDeribit, str]]:
    fake = FakeDeribit()
    async with TestServer(fake.app()) as server:
        yield fake, f"{server.make_url('/api/v2')}"


async def test_get_index_price_maps_response(fake_deribit: tuple[FakeDeribit, str]):
    fake, base_url = fake_deribit
    fake.payload = {"result": {"index_price": 11628.81, "estimated_delivery_price": 11628.81}}

    async with DeribitClient(base_url) as client:
        price = await client.get_index_price("btc_usd")

    assert price == Decimal("11628.81")
    assert isinstance(price, Decimal)
    assert fake.requests == [{"index_name": "btc_usd"}]


async def test_get_index_price_raises_on_api_error(fake_deribit: tuple[FakeDeribit, str]):
    fake, base_url = fake_deribit
    fake.payload = {"error": {"code": -32602, "message": "Invalid params"}}

    async with DeribitClient(base_url) as client:
        with pytest.raises(DeribitApiError, match="Invalid params") as exc_info:
            await client.get_index_price("btc_usd")

    assert exc_info.value.code == -32602
    assert isinstance(exc_info.value, DeribitError)  # сборщик ловит базовый класс


async def test_get_index_price_raises_on_http_error(fake_deribit: tuple[FakeDeribit, str]):
    fake, base_url = fake_deribit
    fake.status = 503

    async with DeribitClient(base_url) as client:
        with pytest.raises(DeribitTransportError, match="HTTP 503"):
            await client.get_index_price("btc_usd")


@pytest.mark.parametrize(
    "payload", [{}, {"result": None}, {"result": {}}, {"result": {"index_price": None}}]
)
async def test_get_index_price_raises_on_unexpected_shape(
    fake_deribit: tuple[FakeDeribit, str], payload: dict
):
    fake, base_url = fake_deribit
    fake.payload = payload

    async with DeribitClient(base_url) as client:
        with pytest.raises(DeribitResponseError):
            await client.get_index_price("btc_usd")


async def test_get_index_price_raises_on_timeout(fake_deribit: tuple[FakeDeribit, str]):
    fake, base_url = fake_deribit
    fake.delay = 1.0

    async with DeribitClient(base_url, timeout_seconds=0.1) as client:
        with pytest.raises(DeribitTransportError, match="transport error"):
            await client.get_index_price("btc_usd")


async def test_client_requires_context_manager():
    client = DeribitClient("http://unused")
    with pytest.raises(RuntimeError):
        await client.get_index_price("btc_usd")
