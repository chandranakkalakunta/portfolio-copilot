"""Hermetic tests for market-data provider (mocked yfinance — no network)."""

from __future__ import annotations

from typing import Any

import pytest

from market_data.provider import MarketDataProvider


class _FastInfo:
    def __init__(self, last_price: float | None, currency: str) -> None:
        self.last_price = last_price
        self.currency = currency

    def get(self, key: str, default: Any = None) -> Any:
        mapping = {
            "lastPrice": self.last_price,
            "last_price": self.last_price,
            "currency": self.currency,
        }
        return mapping.get(key, default)


class _History:
    def __init__(self, *, empty: bool, last_close: float | None) -> None:
        self.empty = empty
        self._last_close = last_close

    def __getitem__(self, key: str) -> Any:
        if key != "Close":
            raise KeyError(key)

        class _Close:
            def __init__(self, value: float | None) -> None:
                self.iloc = [value]

        return _Close(self._last_close)


class _FakeTicker:
    def __init__(
        self,
        *,
        last_price: float | None = 232.1,
        currency: str = "USD",
        info: dict[str, Any] | None = None,
        history_empty: bool = False,
    ) -> None:
        self._last_price = last_price
        self._currency = currency
        self._info = (
            info
            if info is not None
            else {
                "symbol": "AAPL",
                "shortName": "Apple Inc.",
                "marketCap": 3_000_000_000_000,
                "trailingPE": 28.5,
                "forwardPE": 26.0,
                "profitMargins": 0.25,
                "currency": currency,
                "regularMarketPrice": last_price,
            }
        )
        self._history_empty = history_empty
        self.calls = 0

    @property
    def fast_info(self) -> Any:
        self.calls += 1
        return _FastInfo(self._last_price, self._currency)

    @property
    def info(self) -> dict[str, Any]:
        self.calls += 1
        return dict(self._info)

    def history(self, *args: Any, **kwargs: Any) -> Any:
        self.calls += 1
        if self._history_empty or self._last_price is None:
            return _History(empty=True, last_close=None)
        return _History(empty=False, last_close=self._last_price)


def test_fetch_quote_maps_fields_and_as_of() -> None:
    fake = _FakeTicker(last_price=232.1, currency="USD")
    provider = MarketDataProvider(ticker_factory=lambda _t: fake)
    quote = provider.fetch_quote("aapl")
    assert quote["ticker"] == "AAPL"
    assert quote["price"] == 232.1
    assert quote["currency"] == "USD"
    assert "as_of" in quote
    assert "T" in quote["as_of"]  # ISO-8601-ish


def test_fetch_quote_unknown_ticker_raises_clear_error() -> None:
    fake = _FakeTicker(last_price=None, history_empty=True, info={})
    # Make _resolve fail: no price anywhere
    fake._info = {}
    provider = MarketDataProvider(ticker_factory=lambda _t: fake)
    with pytest.raises(ValueError, match=r"no market data for XYZ"):
        provider.fetch_quote("xyz")


def test_fetch_quote_cache_within_ttl_calls_factory_once() -> None:
    fake = _FakeTicker(last_price=100.0)
    factory_calls = {"n": 0}

    def factory(symbol: str) -> _FakeTicker:
        factory_calls["n"] += 1
        assert symbol == "AAPL"
        return fake

    provider = MarketDataProvider(quote_ttl_seconds=60.0, ticker_factory=factory)
    q1 = provider.fetch_quote("AAPL")
    q2 = provider.fetch_quote("AAPL")
    assert q1["price"] == q2["price"] == 100.0
    assert factory_calls["n"] == 1


def test_fetch_fundamentals_maps_fields() -> None:
    fake = _FakeTicker()
    provider = MarketDataProvider(ticker_factory=lambda _t: fake)
    data = provider.fetch_fundamentals("AAPL")
    assert data["ticker"] == "AAPL"
    assert data["market_cap"] == 3_000_000_000_000
    assert data["trailing_pe"] == 28.5
    assert data["forward_pe"] == 26.0
    assert data["profit_margin"] == 0.25
    assert "as_of" in data


def test_fetch_fundamentals_missing_fields_are_null() -> None:
    fake = _FakeTicker(
        info={
            "symbol": "AAPL",
            "shortName": "Apple Inc.",
            "regularMarketPrice": 232.1,
            # no PE / margin / cap
        }
    )
    provider = MarketDataProvider(ticker_factory=lambda _t: fake)
    data = provider.fetch_fundamentals("AAPL")
    assert data["market_cap"] is None
    assert data["trailing_pe"] is None
    assert data["forward_pe"] is None
    assert data["profit_margin"] is None
