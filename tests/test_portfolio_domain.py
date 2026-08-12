"""Hermetic portfolio/profile domain tests (in-memory repos — no GCP)."""

from __future__ import annotations

import asyncio
from datetime import date

import pytest
from pydantic import ValidationError

from adapters.memory.repositories import (
    InMemoryPortfolioRepository,
    InMemoryPositionRepository,
    InMemoryProfileRepository,
)
from core.portfolio.models import Portfolio, Position, Profile
from core.ports.repositories import (
    PortfolioRepository,
    PositionRepository,
    ProfileRepository,
)


def test_profile_model_validation() -> None:
    profile = Profile(
        user_id="u1",
        market="US",
        risk_profile="moderate",
        interests=["tech"],
        intent="growth",
    )
    assert profile.market == "US"
    with pytest.raises(ValidationError):
        Profile(
            user_id="u1",
            market="EU",  # type: ignore[arg-type]
            risk_profile="moderate",
            interests=[],
            intent="x",
        )


def test_portfolio_and_position_models() -> None:
    pf = Portfolio(id="p1", user_id="u1", type="paper", market="IN", cash=100.0)
    pos = Position(ticker="INFY", quantity=5.0, cost_basis=1500.0, acquired=date(2023, 6, 1))
    assert pf.type == "paper"
    assert pos.ticker == "INFY"


def test_inmemory_repos_satisfy_protocols() -> None:
    profiles: ProfileRepository = InMemoryProfileRepository()
    portfolios: PortfolioRepository = InMemoryPortfolioRepository()
    assert isinstance(portfolios, InMemoryPortfolioRepository)
    positions: PositionRepository = InMemoryPositionRepository(portfolios)
    assert callable(profiles.get)
    assert callable(portfolios.create)
    assert callable(positions.add)


def test_upsert_and_get_profile() -> None:
    async def _run() -> None:
        repo = InMemoryProfileRepository()
        profile = Profile(
            user_id="alice",
            market="US",
            risk_profile="conservative",
            interests=["bonds"],
            intent="income",
        )
        await repo.upsert(profile)
        got = await repo.get("alice")
        assert got is not None
        assert got.intent == "income"
        assert await repo.get("missing") is None

    asyncio.run(_run())


def test_create_portfolio_add_list_positions() -> None:
    async def _run() -> None:
        portfolios = InMemoryPortfolioRepository()
        positions = InMemoryPositionRepository(portfolios)
        pf = Portfolio(id="pf-1", user_id="alice", type="real", market="US", cash=500.0)
        assert await portfolios.create(pf) == "pf-1"
        await positions.add(
            "pf-1",
            Position(ticker="AAPL", quantity=2.0, cost_basis=150.0, acquired=date(2024, 1, 1)),
        )
        listed = await positions.list("pf-1")
        assert len(listed) == 1
        assert listed[0].ticker == "AAPL"

    asyncio.run(_run())


def test_list_for_user_isolation() -> None:
    async def _run() -> None:
        portfolios = InMemoryPortfolioRepository()
        await portfolios.create(
            Portfolio(id="a1", user_id="alice", type="paper", market="US", cash=1.0)
        )
        await portfolios.create(
            Portfolio(id="b1", user_id="bob", type="paper", market="US", cash=2.0)
        )
        alice_list = await portfolios.list_for_user("alice")
        bob_list = await portfolios.list_for_user("bob")
        assert [p.id for p in alice_list] == ["a1"]
        assert [p.id for p in bob_list] == ["b1"]
        # Alice must not see Bob's portfolio via list_for_user
        assert all(p.user_id == "alice" for p in alice_list)

    asyncio.run(_run())
