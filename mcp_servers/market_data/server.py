"""Market-data MCP server over HTTP (streamable-HTTP) — ADR-0015.

Run (no-docker fallback)::

    PORT=8081 PYTHONPATH=mcp_servers uv run python -m market_data.server

Docker Compose::

    docker compose up market-data-mcp

MCP endpoint: ``/mcp`` · Health: ``GET /health`` (O31).
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from mcp.server import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from market_data.provider import MarketDataProvider

STARTED_AT: str = datetime.now(UTC).isoformat()
BUILD_ID: str = os.environ.get("BUILD_ID", "dev")
_DEPLOY_TIME: str | None = os.environ.get("DEPLOY_TIME")
deployed_at: str = _DEPLOY_TIME if _DEPLOY_TIME else STARTED_AT

mcp = MCPServer("market-data")
_provider: MarketDataProvider = MarketDataProvider()


def get_provider() -> MarketDataProvider:
    """Return the active market-data provider (swappable for tests)."""
    return _provider


def set_provider(provider: MarketDataProvider) -> None:
    """Replace the active provider (integration tests inject a fake)."""
    global _provider
    _provider = provider


def health_payload() -> dict[str, str]:
    """Plain /health body (O31) — used by route and hermetic tests."""
    return {
        "status": "ok",
        "build_id": BUILD_ID,
        "deployed_at": deployed_at,
        "started_at": STARTED_AT,
    }


@mcp.custom_route("/health", methods=["GET"])  # type: ignore[untyped-decorator]
async def health_check(_request: Request) -> Response:
    """Liveness/readiness-style health with build id + deploy time."""
    return JSONResponse(health_payload())


@mcp.tool()
def get_quote(ticker: str) -> dict[str, Any]:
    """Get the latest stock quote for a ticker (price, currency, as_of)."""
    return get_provider().fetch_quote(ticker)


@mcp.tool()
def get_fundamentals(ticker: str) -> dict[str, Any]:
    """Get curated fundamentals for a ticker (market_cap, P/E, margin, as_of)."""
    return get_provider().fetch_fundamentals(ticker)


def main() -> None:
    """Serve streamable-HTTP MCP on 0.0.0.0:$PORT (default 8081)."""
    port = int(os.environ.get("PORT", "8081"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        streamable_http_path="/mcp",
    )


if __name__ == "__main__":
    main()
