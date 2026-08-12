"""Firebase AuthPort — verify Google/Firebase ID tokens (keyless ADC)."""

from __future__ import annotations

import asyncio
from typing import Any

import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

from core.config import LLMSettings
from core.ports.auth import AuthenticatedUser, AuthError

_app_initialized = False


def _ensure_firebase_app(project_id: str) -> None:
    """Initialize the default firebase_admin app once (ADC / ApplicationDefault)."""
    global _app_initialized
    if _app_initialized:
        return
    try:
        firebase_admin.get_app()
        _app_initialized = True
        return
    except ValueError:
        pass
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, options={"projectId": project_id})
    _app_initialized = True


class FirebaseAuthAdapter:
    """AuthPort backed by firebase_admin.auth.verify_id_token."""

    def __init__(self, *, project_id: str | None = None) -> None:
        settings = LLMSettings()
        self._project_id = project_id or settings.gcp_project
        _ensure_firebase_app(self._project_id)

    async def verify_token(self, token: str) -> AuthenticatedUser:
        if not token or not token.strip():
            raise AuthError("missing token")

        def _verify() -> dict[str, Any]:
            try:
                decoded: dict[str, Any] = firebase_auth.verify_id_token(token)
                return decoded
            except firebase_auth.ExpiredIdTokenError:
                raise AuthError("token expired") from None
            except firebase_auth.InvalidIdTokenError:
                raise AuthError("invalid token") from None
            except firebase_auth.RevokedIdTokenError:
                raise AuthError("token revoked") from None
            except (ValueError, TypeError, OSError, RuntimeError):
                # Do not leak stack or provider details to callers (§5.24).
                raise AuthError("invalid or expired token") from None

        decoded = await asyncio.to_thread(_verify)
        uid = decoded.get("uid") or decoded.get("user_id") or decoded.get("sub")
        if not isinstance(uid, str) or not uid:
            raise AuthError("invalid token")
        email_raw = decoded.get("email")
        email = email_raw if isinstance(email_raw, str) else None
        return AuthenticatedUser(user_id=uid, email=email)
