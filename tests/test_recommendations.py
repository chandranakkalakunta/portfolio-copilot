"""Hermetic recommendation logging tests (F29) — fake TimeSeriesPort."""

from __future__ import annotations

import asyncio
from collections.abc import Iterator
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from adapters.fake_analysis.engine import FakeAnalysisEngine
from adapters.fake_auth.auth import (
    FAKE_TOKEN_BOB,
    FAKE_USER,
    FAKE_USER_BOB,
    FAKE_VALID_TOKEN,
    FakeAuthAdapter,
)
from adapters.memory.repositories import (
    InMemoryPortfolioRepository,
    InMemoryPositionRepository,
    InMemoryProfileRepository,
)
from adapters.memory.timeseries import InMemoryTimeSeriesStore
from api.main import app
from core.ports.agent_framework import AnalysisResult
from core.ports.auth import AuthenticatedUser
from core.tracking.models import Recommendation
from core.tracking.service import RecommendationLogService


class _RaisingStore(InMemoryTimeSeriesStore):
    async def write_recommendation(self, rec: Recommendation) -> None:
        raise RuntimeError("bq unavailable")


@pytest.fixture
def store() -> InMemoryTimeSeriesStore:
    return InMemoryTimeSeriesStore()


@pytest.fixture
def client(store: InMemoryTimeSeriesStore) -> Iterator[TestClient]:
    profiles = InMemoryProfileRepository()
    portfolios = InMemoryPortfolioRepository()
    positions = InMemoryPositionRepository(portfolios)
    logger = RecommendationLogService(store)
    with TestClient(app) as test_client:
        app.state.auth_port = FakeAuthAdapter(
            token_map={
                FAKE_VALID_TOKEN: FAKE_USER,
                FAKE_TOKEN_BOB: FAKE_USER_BOB,
            }
        )
        app.state.profile_repo = profiles
        app.state.portfolio_repo = portfolios
        app.state.position_repo = positions
        app.state.analysis_engine = FakeAnalysisEngine()
        app.state.timeseries_port = store
        app.state.rec_logger = logger
        yield test_client


def _auth(token: str = FAKE_VALID_TOKEN) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_log_from_analysis_mapping() -> None:
    async def _run() -> None:
        store = InMemoryTimeSeriesStore()
        service = RecommendationLogService(store)
        issued_src = datetime(2026, 8, 16, 12, 0, tzinfo=UTC)
        result = AnalysisResult(
            ticker="NVDA",
            summary="note",
            tool_calls=["get_quote"],
            framework="adk",
            rating="informational",
            price_at_issue=Decimal("178.40"),
            price_as_of=issued_src,
            currency="USD",
        )
        rec = await service.log_from_analysis(
            result, AuthenticatedUser(user_id="alice", email="alice@example.com")
        )
        assert rec is not None
        assert rec.user_id == "alice"
        assert rec.portfolio_id is None
        assert rec.ticker == "NVDA"
        assert rec.market == "US"
        assert rec.action == "informational"
        assert rec.rating == "informational"
        assert rec.price_at_issue == Decimal("178.40")
        assert rec.price_as_of == issued_src
        assert rec.currency == "USD"
        assert rec.note_ref == rec.rec_id
        assert rec.model_attribution == "adk"
        assert rec.schema_version == 1
        assert service.writes_ok == 1
        rows = await store.query_recommendations(user_id="alice")
        assert len(rows) == 1
        assert rows[0].rec_id == rec.rec_id

    asyncio.run(_run())


def test_skip_if_no_price() -> None:
    async def _run() -> None:
        store = InMemoryTimeSeriesStore()
        service = RecommendationLogService(store)
        result = AnalysisResult(
            ticker="AAPL",
            summary="note",
            tool_calls=[],
            framework="fake",
            price_at_issue=None,
        )
        rec = await service.log_from_analysis(result, AuthenticatedUser(user_id="alice"))
        assert rec is None
        assert service.skipped_no_price == 1
        assert service.writes_ok == 0
        assert await store.query_recommendations(user_id="alice") == []

    asyncio.run(_run())


def test_analyze_still_returns_when_write_fails() -> None:
    store = _RaisingStore()
    logger = RecommendationLogService(store)
    with TestClient(app) as test_client:
        app.state.auth_port = FakeAuthAdapter()
        app.state.analysis_engine = FakeAnalysisEngine()
        app.state.timeseries_port = store
        app.state.rec_logger = logger
        response = test_client.post(
            "/analyze",
            headers=_auth(),
            json={"ticker": "AAPL"},
        )
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"
    assert logger.write_failures == 1
    assert logger.writes_ok == 0


def test_analyze_money_serializes_as_string(client: TestClient) -> None:
    response = client.post("/analyze", headers=_auth(), json={"ticker": "AAPL"})
    assert response.status_code == 200
    body = response.json()
    assert body["price_at_issue"] == "100.0"
    assert isinstance(body["price_at_issue"], str)


def test_get_recommendations_user_scoped(
    client: TestClient, store: InMemoryTimeSeriesStore
) -> None:
    alice = client.post("/analyze", headers=_auth(), json={"ticker": "AAPL"})
    assert alice.status_code == 200
    bob = client.post("/analyze", headers=_auth(FAKE_TOKEN_BOB), json={"ticker": "NVDA"})
    assert bob.status_code == 200

    alice_rows = client.get("/recommendations", headers=_auth())
    assert alice_rows.status_code == 200
    alice_body = alice_rows.json()
    assert len(alice_body) == 1
    assert alice_body[0]["ticker"] == "AAPL"
    assert alice_body[0]["user_id"] == "alice"
    assert alice_body[0]["price_at_issue"] == "100.0"
    assert isinstance(alice_body[0]["price_at_issue"], str)

    bob_rows = client.get("/recommendations", headers=_auth(FAKE_TOKEN_BOB))
    assert bob_rows.status_code == 200
    bob_body = bob_rows.json()
    assert len(bob_body) == 1
    assert bob_body[0]["ticker"] == "NVDA"
    assert bob_body[0]["user_id"] == "bob"

    filtered = client.get("/recommendations", headers=_auth(), params={"ticker": "NVDA"})
    assert filtered.status_code == 200
    assert filtered.json() == []


def test_recommendations_401_without_token(client: TestClient) -> None:
    assert client.get("/recommendations").status_code == 401
