"""Minimal FastAPI hello service with health / ready / version (O31)."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import TypedDict

from fastapi import FastAPI

STARTED_AT: str = datetime.now(UTC).isoformat()
BUILD_ID: str = os.environ.get("BUILD_ID", "dev")
_DEPLOY_TIME: str | None = os.environ.get("DEPLOY_TIME")
deployed_at: str = _DEPLOY_TIME if _DEPLOY_TIME else STARTED_AT

app = FastAPI(title="portfolio-copilot")


class RootResponse(TypedDict):
    service: str
    status: str


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


@app.get("/")
def root() -> RootResponse:
    return {"service": "portfolio-copilot", "status": "ok"}


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
