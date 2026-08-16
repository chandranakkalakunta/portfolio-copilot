"""Extract structured quote fields (never parse citation detail strings)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any


def structured_price_from_quote(
    quote: dict[str, Any] | None,
) -> tuple[Decimal | None, datetime | None, str | None]:
    """Return (price, as_of, currency) from a get_quote payload."""
    if not quote:
        return None, None, None
    raw_price = quote.get("price")
    if raw_price is None:
        return None, None, None
    try:
        price = Decimal(str(raw_price))
    except (InvalidOperation, ValueError, TypeError):
        return None, None, None
    currency_raw = quote.get("currency")
    currency = currency_raw if isinstance(currency_raw, str) and currency_raw else None
    as_of = _parse_as_of(quote.get("as_of"))
    return price, as_of, currency


def _parse_as_of(raw: Any) -> datetime | None:
    if isinstance(raw, datetime):
        return raw
    if not isinstance(raw, str) or not raw or raw == "unknown":
        return None
    text = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None
