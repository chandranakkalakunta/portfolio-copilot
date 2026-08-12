"""STUB market-data tools for the Phase 1 framework spike.

Real market-data MCP is Phase 2 — these return canned quotes only.
"""

from __future__ import annotations

from pydantic import BaseModel

GET_QUOTE_TOOL_DESCRIPTION: str = "Get the latest stock quote for a ticker symbol."

_CANNED: dict[str, tuple[float, str]] = {
    "AAPL": (232.10, "USD"),
    "INFY": (1650.0, "INR"),
}


class Quote(BaseModel):
    """A canned stock quote (spike stub)."""

    ticker: str
    price: float
    currency: str


def get_quote(ticker: str) -> Quote:
    """Return a canned quote for the ticker (STUB — Phase 1 spike only).

    Real market-data MCP arrives in Phase 2. Unknown tickers get a default quote.
    """
    symbol = ticker.upper()
    price, currency = _CANNED.get(symbol, (100.0, "USD"))
    return Quote(ticker=symbol, price=price, currency=currency)
