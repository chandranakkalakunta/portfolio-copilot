"""Integration: Firestore repository adapter against the Firestore emulator.

Requires ``FIRESTORE_EMULATOR_HOST`` (e.g. ``127.0.0.1:8080``). Skips if unset
so unit runs stay hermetic without Java/emulator.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import date

import pytest
from google.cloud.firestore import AsyncClient

from adapters.firestore.repositories import (
    FirestorePortfolioRepository,
    FirestorePositionRepository,
    FirestoreProfileRepository,
)
from core.portfolio.models import Portfolio, Position, Profile

pytestmark = pytest.mark.integration


def _require_emulator() -> None:
    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        pytest.skip("FIRESTORE_EMULATOR_HOST not set — start the Firestore emulator")


def _project() -> str:
    return os.environ.get("FIRESTORE_EMULATOR_PROJECT", "pcopilot-dev-emulator")


def test_profile_upsert_and_get() -> None:
    _require_emulator()

    async def _run() -> None:
        client = AsyncClient(project=_project())
        try:
            profiles = FirestoreProfileRepository(client=client)
            user_id = f"itest-user-{uuid.uuid4().hex[:8]}"
            profile = Profile(
                user_id=user_id,
                market="US",
                risk_profile="moderate",
                interests=["tech"],
                intent="growth",
            )
            await profiles.upsert(profile)
            got = await profiles.get(user_id)
            assert got is not None
            assert got.user_id == user_id
            assert got.intent == "growth"
            assert await profiles.get("missing-user-xyz") is None
        finally:
            await client.close()  # type: ignore[no-untyped-call]

    asyncio.run(_run())


def test_portfolio_create_positions_and_isolation() -> None:
    _require_emulator()

    async def _run() -> None:
        client = AsyncClient(project=_project())
        try:
            portfolios = FirestorePortfolioRepository(client=client)
            positions = FirestorePositionRepository(client=client)

            alice = f"alice-{uuid.uuid4().hex[:8]}"
            bob = f"bob-{uuid.uuid4().hex[:8]}"
            alice_pf = f"pf-a-{uuid.uuid4().hex[:8]}"
            bob_pf = f"pf-b-{uuid.uuid4().hex[:8]}"

            await portfolios.create(
                Portfolio(id=alice_pf, user_id=alice, type="paper", market="US", cash=1000.0)
            )
            await portfolios.create(
                Portfolio(id=bob_pf, user_id=bob, type="paper", market="US", cash=2000.0)
            )

            await positions.add(
                alice_pf,
                Position(
                    ticker="AAPL",
                    quantity=3.0,
                    cost_basis=150.0,
                    acquired=date(2024, 1, 2),
                ),
            )

            listed_pos = await positions.list(alice_pf)
            assert len(listed_pos) == 1
            assert listed_pos[0].ticker == "AAPL"

            alice_list = await portfolios.list_for_user(alice)
            bob_list = await portfolios.list_for_user(bob)
            assert {p.id for p in alice_list} == {alice_pf}
            assert {p.id for p in bob_list} == {bob_pf}
            assert all(p.user_id == alice for p in alice_list)
        finally:
            await client.close()  # type: ignore[no-untyped-call]

    asyncio.run(_run())
