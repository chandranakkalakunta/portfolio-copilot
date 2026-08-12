"""yfinance market-data provider with TTL cache and semantic errors.

Display-only; not for execution. Swap later behind MarketDataPort (F57).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from contextlib import suppress
from datetime import UTC, datetime
from typing import Any, Protocol

import yfinance as yf

QuoteDict = dict[str, Any]
FundamentalsDict = dict[str, Any]


class _TickerLike(Protocol):
    """Minimal surface of yfinance.Ticker used by this provider."""

    @property
    def fast_info(self) -> Any: ...

    @property
    def info(self) -> dict[str, Any]: ...

    def history(self, *args: Any, **kwargs: Any) -> Any: ...


TickerFactory = Callable[[str], _TickerLike]


class _CacheEntry:
    __slots__ = ("expires_at", "value")

    def __init__(self, value: dict[str, Any], expires_at: float) -> None:
        self.value = value
        self.expires_at = expires_at


class MarketDataProvider:
    """Wraps yfinance with small in-memory TTL caches and clean error mapping."""

    def __init__(
        self,
        *,
        quote_ttl_seconds: float = 60.0,
        fundamentals_ttl_seconds: float = 3600.0,
        ticker_factory: TickerFactory | None = None,
    ) -> None:
        self._quote_ttl = quote_ttl_seconds
        self._fundamentals_ttl = fundamentals_ttl_seconds
        self._ticker_factory: TickerFactory = ticker_factory or yf.Ticker
        self._quote_cache: dict[str, _CacheEntry] = {}
        self._fundamentals_cache: dict[str, _CacheEntry] = {}

    @staticmethod
    def _normalize_ticker(ticker: str) -> str:
        symbol = ticker.strip().upper()
        if not symbol:
            raise ValueError("no market data for ")
        return symbol

    @staticmethod
    def _as_of_now() -> str:
        return datetime.now(UTC).isoformat()

    def _cache_get(self, cache: dict[str, _CacheEntry], key: str) -> dict[str, Any] | None:
        entry = cache.get(key)
        if entry is None:
            return None
        if time.monotonic() >= entry.expires_at:
            del cache[key]
            return None
        return dict(entry.value)

    def _cache_set(
        self,
        cache: dict[str, _CacheEntry],
        key: str,
        value: dict[str, Any],
        ttl: float,
    ) -> None:
        cache[key] = _CacheEntry(value=dict(value), expires_at=time.monotonic() + ttl)

    def _resolve_price_and_currency(self, stock: _TickerLike, symbol: str) -> tuple[float, str]:
        price: float | None = None
        currency: str | None = None

        with suppress(TypeError, ValueError, AttributeError, KeyError, OSError):
            fast = stock.fast_info
            raw_price = getattr(fast, "last_price", None)
            if raw_price is None and hasattr(fast, "get"):
                raw_price = fast.get("lastPrice") or fast.get("last_price")
            if isinstance(raw_price, (int, float)) and not isinstance(raw_price, bool):
                price = float(raw_price)
            raw_ccy = getattr(fast, "currency", None)
            if raw_ccy is None and hasattr(fast, "get"):
                raw_ccy = fast.get("currency")
            if isinstance(raw_ccy, str) and raw_ccy:
                currency = raw_ccy

        if price is None:
            with suppress(TypeError, ValueError, AttributeError, KeyError, OSError, IndexError):
                hist = stock.history(period="5d")
                if hist is not None and getattr(hist, "empty", True) is False:
                    close_last = hist["Close"].iloc[-1]
                    if isinstance(close_last, (int, float)) and not isinstance(close_last, bool):
                        price = float(close_last)

        info: dict[str, Any] = {}
        with suppress(TypeError, ValueError, AttributeError, OSError):
            info = dict(stock.info or {})

        if price is None:
            for key in ("currentPrice", "regularMarketPrice", "previousClose"):
                raw = info.get(key)
                if raw is not None:
                    try:
                        price = float(raw)
                        break
                    except (TypeError, ValueError):
                        continue

        if currency is None:
            raw_ccy = info.get("currency")
            if isinstance(raw_ccy, str) and raw_ccy:
                currency = raw_ccy

        if price is None:
            raise ValueError(f"no market data for {symbol}")

        return price, currency or "USD"

    def fetch_quote(self, ticker: str) -> QuoteDict:
        """Return latest quote fields with as-of timestamp (UTC ISO-8601).

        Raises:
            ValueError: when the ticker is invalid or has no price data.
        """
        symbol = self._normalize_ticker(ticker)
        cached = self._cache_get(self._quote_cache, symbol)
        if cached is not None:
            return cached

        stock = self._ticker_factory(symbol)
        price, currency = self._resolve_price_and_currency(stock, symbol)
        result: QuoteDict = {
            "ticker": symbol,
            "price": price,
            "currency": currency,
            "as_of": self._as_of_now(),
        }
        self._cache_set(self._quote_cache, symbol, result, self._quote_ttl)
        return result

    def fetch_fundamentals(self, ticker: str) -> FundamentalsDict:
        """Return a small curated fundamentals set; missing fields are null.

        Raises:
            ValueError: when the ticker is invalid or yfinance returns no usable info.
        """
        symbol = self._normalize_ticker(ticker)
        cached = self._cache_get(self._fundamentals_cache, symbol)
        if cached is not None:
            return cached

        stock = self._ticker_factory(symbol)
        try:
            info = dict(stock.info or {})
        except (TypeError, ValueError, AttributeError, OSError) as exc:
            raise ValueError(f"no market data for {symbol}") from exc

        # Empty / useless info: still require that a price can be resolved (ticker exists).
        has_identity = bool(info.get("symbol") or info.get("shortName") or info.get("marketCap"))
        if not info or not has_identity:
            try:
                self._resolve_price_and_currency(stock, symbol)
            except ValueError as exc:
                raise ValueError(f"no market data for {symbol}") from exc

        def _num(key: str) -> float | None:
            raw = info.get(key)
            if raw is None:
                return None
            try:
                return float(raw)
            except (TypeError, ValueError):
                return None

        result: FundamentalsDict = {
            "ticker": symbol,
            "market_cap": _num("marketCap"),
            "trailing_pe": _num("trailingPE"),
            "forward_pe": _num("forwardPE"),
            "profit_margin": _num("profitMargins"),
            "as_of": self._as_of_now(),
        }
        self._cache_set(self._fundamentals_cache, symbol, result, self._fundamentals_ttl)
        return result
