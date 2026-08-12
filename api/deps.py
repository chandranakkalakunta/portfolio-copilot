"""FastAPI dependencies (auth, settings wiring)."""

from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from adapters.fake_auth.auth import FakeAuthAdapter
from core.ports.auth import AuthenticatedUser, AuthError, AuthPort


def _build_auth_port() -> AuthPort:
    """Select AuthPort implementation (Fake for tests/local, Firebase for real).

    Controlled by env ``PCOPILOT_AUTH_BACKEND``:
      - ``fake`` (default) → FakeAuthAdapter
      - ``firebase`` → FirebaseAuthAdapter
    """
    backend = os.environ.get("PCOPILOT_AUTH_BACKEND", "fake").lower()
    if backend == "firebase":
        from adapters.firebase_auth.auth import FirebaseAuthAdapter

        return FirebaseAuthAdapter()
    return FakeAuthAdapter()


def get_auth_port(request: Request) -> AuthPort:
    """Return the process-wide AuthPort (set on app.state at startup)."""
    auth: AuthPort | None = getattr(request.app.state, "auth_port", None)
    if auth is None:
        auth = _build_auth_port()
        request.app.state.auth_port = auth
    return auth


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
