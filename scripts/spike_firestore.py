"""LIVE Firestore smoke: profile + portfolio + position round-trip (ADC)."""

from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from adapters.firestore.repositories import (
    FirestorePortfolioRepository,
    FirestorePositionRepository,
    FirestoreProfileRepository,
)
from core.portfolio.models import Portfolio, Position, Profile


async def main() -> None:
    suffix = uuid.uuid4().hex[:8]
    user_id = f"spike-user-{suffix}"
    portfolio_id = f"spike-pf-{suffix}"

    profiles = FirestoreProfileRepository()
    portfolios = FirestorePortfolioRepository()
    positions = FirestorePositionRepository()

    profile = Profile(
        user_id=user_id,
        market="US",
        risk_profile="moderate",
        interests=["tech", "dividends"],
        intent="long-term growth",
    )
    await profiles.upsert(profile)

    portfolio = Portfolio(
        id=portfolio_id,
        user_id=user_id,
        type="paper",
        market="US",
        cash=10_000.0,
    )
    await portfolios.create(portfolio)

    position = Position(
        ticker="AAPL",
        quantity=10.0,
        cost_basis=180.0,
        acquired=date(2024, 1, 15),
    )
    await positions.add(portfolio_id, position)

    got_profile = await profiles.get(user_id)
    got_portfolio = await portfolios.get(portfolio_id)
    listed = await portfolios.list_for_user(user_id)
    got_positions = await positions.list(portfolio_id)

    out = {
        "user_id": user_id,
        "portfolio_id": portfolio_id,
        "profile": got_profile.model_dump() if got_profile else None,
        "portfolio": got_portfolio.model_dump() if got_portfolio else None,
        "list_for_user_ids": [p.id for p in listed],
        "positions": [p.model_dump(mode="json") for p in got_positions],
    }
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
