"""Integration: market-data MCP over HTTP with a fake provider (no yfinance)."""

from __future__ import annotations

import asyncio
import json
import socket
import threading
import time
from datetime import datetime
from typing import Any

import httpx
import pytest
import uvicorn

from market_data import server as market_data_server
from market_data.provider import MarketDataProvider
from mcp import Client

pytestmark = pytest.mark.integration

CANNED_QUOTE: dict[str, Any] = {
    "ticker": "AAPL",
    "price": 111.11,
    "currency": "USD",
    "as_of": "2024-01-01T00:00:00+00:00",
}


class _FakeTicker:
    """Minimal yfinance-like object for MarketDataProvider.ticker_factory."""

    def __init__(self, symbol: str) -> None:
        self._symbol = symbol

    @property
    def fast_info(self) -> Any:
        class _FI:
            last_price = CANNED_QUOTE["price"]
            currency = CANNED_QUOTE["currency"]

        return _FI()

    @property
    def info(self) -> dict[str, Any]:
        return {
            "symbol": self._symbol,
            "shortName": "Canned Apple",
            "regularMarketPrice": CANNED_QUOTE["price"],
            "currency": CANNED_QUOTE["currency"],
            "marketCap": 1.0,
        }

    def history(self, *args: Any, **kwargs: Any) -> Any:
        class _Hist:
            empty = True

        return _Hist()


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture
def mcp_http_server() -> Any:
    """Start streamable-HTTP MCP in a background thread with a fake provider."""
    previous = market_data_server.get_provider()
    fake = MarketDataProvider(ticker_factory=lambda symbol: _FakeTicker(symbol))
    market_data_server.set_provider(fake)

    port = _free_port()
    app = market_data_server.mcp.streamable_http_app(
        streamable_http_path="/mcp",
        host="127.0.0.1",
    )
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.time() + 15.0
    health_url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        try:
            response = httpx.get(health_url, timeout=0.5)
            if response.status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.1)
    else:
        server.should_exit = True
        thread.join(timeout=5)
        market_data_server.set_provider(previous)
        pytest.fail("MCP HTTP server did not become healthy in time")

    yield port

    server.should_exit = True
    thread.join(timeout=10)
    market_data_server.set_provider(previous)


def test_health_returns_build_id(mcp_http_server: int) -> None:
    response = httpx.get(f"http://127.0.0.1:{mcp_http_server}/health", timeout=5.0)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "build_id" in body
    assert body["build_id"]


def test_get_quote_over_http_returns_canned(mcp_http_server: int) -> None:
    async def _run() -> None:
        url = f"http://127.0.0.1:{mcp_http_server}/mcp"
        async with Client(url) as client:
            result = await client.call_tool("get_quote", {"ticker": "AAPL"})
        structured = getattr(result, "structured_content", None)
        if structured is not None:
            payload: Any = structured
        else:
            content = getattr(result, "content", None) or []
            texts = [
                getattr(block, "text", "") for block in content if getattr(block, "text", None)
            ]
            assert texts, f"unexpected tool result: {result!r}"
            payload = json.loads(texts[0])

        assert payload["ticker"] == "AAPL"
        assert float(payload["price"]) == float(CANNED_QUOTE["price"])
        assert payload["currency"] == "USD"
        # as_of is generated at fetch time by the provider
        assert "as_of" in payload
        datetime.fromisoformat(str(payload["as_of"]))

    asyncio.run(_run())
