"""LIVE smoke: real yfinance network calls for AAPL quote + fundamentals."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_MCP_DIR = _ROOT / "mcp"
for path in (_ROOT, _MCP_DIR):
    s = str(path)
    if s not in sys.path:
        sys.path.insert(0, s)

from market_data.provider import MarketDataProvider


def main() -> None:
    provider = MarketDataProvider()
    quote = provider.fetch_quote("AAPL")
    fundamentals = provider.fetch_fundamentals("AAPL")
    print(json.dumps({"quote": quote, "fundamentals": fundamentals}, indent=2))


if __name__ == "__main__":
    main()
