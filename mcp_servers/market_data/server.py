"""Market-data MCP server (stdio) — get_quote + get_fundamentals (ADR-0005).

Run (stdio)::

    PYTHONPATH=mcp_servers uv run python -m market_data.server

Monorepo path is ``mcp_servers/market_data/``. Import package is ``market_data``.
The directory is ``mcp_servers/`` (not ``mcp/``) so ``import mcp`` always resolves
to the official PyPI MCP SDK.
"""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from market_data.provider import MarketDataProvider

mcp = MCPServer("market-data")
_provider = MarketDataProvider()


@mcp.tool()
def get_quote(ticker: str) -> dict[str, Any]:
    """Get the latest stock quote for a ticker (price, currency, as_of)."""
    return _provider.fetch_quote(ticker)


@mcp.tool()
def get_fundamentals(ticker: str) -> dict[str, Any]:
    """Get curated fundamentals for a ticker (market_cap, P/E, margin, as_of)."""
    return _provider.fetch_fundamentals(ticker)


def main() -> None:
    """Serve over stdio (MCP default for local/dev)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
