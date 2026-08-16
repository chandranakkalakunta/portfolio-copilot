"""FastAPI dependencies (auth, repos, analysis engine)."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

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
from core.ports.agent_framework import AgentFrameworkPort
from core.ports.auth import AuthenticatedUser, AuthError, AuthPort
from core.ports.repositories import (
    PortfolioRepository,
    PositionRepository,
    ProfileRepository,
)
from core.ports.timeseries import TimeSeriesPort
from core.tracking.service import RecommendationLogService


def _build_auth_port() -> AuthPort:
    """Select AuthPort (Fake default; Firebase when configured).

    ``PCOPILOT_AUTH_BACKEND``: ``fake`` (default) | ``firebase``
    """
    backend = os.environ.get("PCOPILOT_AUTH_BACKEND", "fake").lower()
    if backend == "firebase":
        from adapters.firebase_auth.auth import FirebaseAuthAdapter

        return FirebaseAuthAdapter()
    return FakeAuthAdapter(
        token_map={
            FAKE_VALID_TOKEN: FAKE_USER,
            FAKE_TOKEN_BOB: FAKE_USER_BOB,
        }
    )


def _build_repos() -> tuple[ProfileRepository, PortfolioRepository, PositionRepository]:
    """Select repository backends.

    ``PCOPILOT_REPO_BACKEND``: ``memory`` (default) | ``firestore``
    """
    backend = os.environ.get("PCOPILOT_REPO_BACKEND", "memory").lower()
    if backend == "firestore":
        from adapters.firestore.repositories import (
            FirestorePortfolioRepository,
            FirestorePositionRepository,
            FirestoreProfileRepository,
        )

        return (
            FirestoreProfileRepository(),
            FirestorePortfolioRepository(),
            FirestorePositionRepository(),
        )
    profiles: ProfileRepository = InMemoryProfileRepository()
    portfolios = InMemoryPortfolioRepository()
    positions: PositionRepository = InMemoryPositionRepository(portfolios)
    return profiles, portfolios, positions


def _build_analysis_engine() -> AgentFrameworkPort:
    """Select analysis engine.

    ``PCOPILOT_ANALYSIS_BACKEND``: ``adk`` (default) | ``fake``
    """
    backend = os.environ.get("PCOPILOT_ANALYSIS_BACKEND", "adk").lower()
    if backend == "fake":
        from adapters.fake_analysis.engine import FakeAnalysisEngine

        return FakeAnalysisEngine()
    from adapters.agent_adk.engine import AdkAnalysisEngine

    return AdkAnalysisEngine()


def _build_timeseries_port() -> TimeSeriesPort:
    """Select TimeSeriesPort.

    ``PCOPILOT_TIMESERIES_BACKEND``: ``memory`` (default) | ``bigquery``
    """
    backend = os.environ.get("PCOPILOT_TIMESERIES_BACKEND", "memory").lower()
    if backend == "bigquery":
        from adapters.store_bigquery.store import BigQueryTimeSeriesStore

        return BigQueryTimeSeriesStore()
    from adapters.memory.timeseries import InMemoryTimeSeriesStore

    return InMemoryTimeSeriesStore()


def wire_app_state(app: object) -> None:
    """Initialize process-wide ports on ``app.state`` (idempotent)."""
    state = getattr(app, "state", None)
    if state is None:
        return
    if getattr(state, "auth_port", None) is None:
        state.auth_port = _build_auth_port()
    if getattr(state, "profile_repo", None) is None:
        profiles, portfolios, positions = _build_repos()
        state.profile_repo = profiles
        state.portfolio_repo = portfolios
        state.position_repo = positions
    # analysis_engine and timeseries_port are built on first use (cold-start).


def get_auth_port(request: Request) -> AuthPort:
    wire_app_state(request.app)
    return request.app.state.auth_port  # type: ignore[no-any-return]


def get_profile_repo(request: Request) -> ProfileRepository:
    wire_app_state(request.app)
    return request.app.state.profile_repo  # type: ignore[no-any-return]


def get_portfolio_repo(request: Request) -> PortfolioRepository:
    wire_app_state(request.app)
    return request.app.state.portfolio_repo  # type: ignore[no-any-return]


def get_position_repo(request: Request) -> PositionRepository:
    wire_app_state(request.app)
    return request.app.state.position_repo  # type: ignore[no-any-return]


def get_analysis_engine(request: Request) -> AgentFrameworkPort:
    wire_app_state(request.app)
    if getattr(request.app.state, "analysis_engine", None) is None:
        request.app.state.analysis_engine = _build_analysis_engine()
    return request.app.state.analysis_engine  # type: ignore[no-any-return]


def get_timeseries_port(request: Request) -> TimeSeriesPort:
    wire_app_state(request.app)
    if getattr(request.app.state, "timeseries_port", None) is None:
        request.app.state.timeseries_port = _build_timeseries_port()
    return request.app.state.timeseries_port  # type: ignore[no-any-return]


def get_recommendation_logger(
    request: Request,
) -> RecommendationLogService:
    store = get_timeseries_port(request)
    existing = getattr(request.app.state, "rec_logger", None)
    if existing is None:
        existing = RecommendationLogService(store)
        request.app.state.rec_logger = existing
    return existing


async def get_current_user(
    auth: Annotated[AuthPort, Depends(get_auth_port)],
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedUser:
    """Extract Bearer token and verify via AuthPort; 401 on missing/invalid."""
    if authorization is None or not authorization.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return await auth.verify_token(token.strip())
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
