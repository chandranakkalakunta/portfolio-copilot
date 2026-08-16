"""Portfolio Copilot API — health (O31), /me (F58), domain routes, static UI (2.6)."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, TypedDict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles

from api.deps import get_current_user, wire_app_state
from api.routers import analyze, portfolios, positions, profile, recommendations
from core.config import FirebaseWebSettings
from core.ports.auth import AuthenticatedUser

WEB_DIR = Path(__file__).resolve().parent.parent / "web"

STARTED_AT: str = datetime.now(UTC).isoformat()
BUILD_ID: str = os.environ.get("BUILD_ID", "dev")
_DEPLOY_TIME: str | None = os.environ.get("DEPLOY_TIME")
deployed_at: str = _DEPLOY_TIME if _DEPLOY_TIME else STARTED_AT


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Wire auth, repos, and analysis engine at startup (config-selected)."""
    wire_app_state(app)
    yield


app = FastAPI(title="portfolio-copilot", lifespan=lifespan)
app.include_router(profile.router)
app.include_router(portfolios.router)
app.include_router(positions.router)
app.include_router(analyze.router)
app.include_router(recommendations.router)


class HealthResponse(TypedDict):
    status: str
    build_id: str
    deployed_at: str
    started_at: str


class ReadyResponse(TypedDict):
    status: str
    build_id: str


class VersionResponse(TypedDict):
    build_id: str
    deployed_at: str


class MeResponse(TypedDict):
    user_id: str
    email: str | None


class FirebaseWebConfigResponse(TypedDict):
    apiKey: str
    authDomain: str
    projectId: str


@app.get("/config")
def firebase_web_config() -> FirebaseWebConfigResponse:
    """Public Firebase web config for the browser SDK (apiKey is not a secret)."""
    settings = FirebaseWebSettings()
    if not settings.is_complete():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="firebase web config not set",
        )
    return {
        "apiKey": settings.api_key,
        "authDomain": settings.auth_domain,
        "projectId": settings.project_id,
    }


@app.get("/health")
def health() -> HealthResponse:
    return {
        "status": "ok",
        "build_id": BUILD_ID,
        "deployed_at": deployed_at,
        "started_at": STARTED_AT,
    }


@app.get("/ready")
def ready() -> ReadyResponse:
    return {"status": "ready", "build_id": BUILD_ID}


@app.get("/version")
def version() -> VersionResponse:
    return {"build_id": BUILD_ID, "deployed_at": deployed_at}


@app.get("/me")
async def me(user: Annotated[AuthenticatedUser, Depends(get_current_user)]) -> MeResponse:
    """Return the current authenticated user (Bearer Google/Firebase ID token)."""
    return {"user_id": user.user_id, "email": user.email}


# Last: catch-all static UI. API routes above take precedence.
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
