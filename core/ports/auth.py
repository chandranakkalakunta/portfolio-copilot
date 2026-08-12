"""Auth port — provider-agnostic token verification (F58, ADR-0001).

Firebase/Google SDKs live only in adapters/ (F55). Invalid tokens raise AuthError.
"""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    """Verified identity extracted from an ID token."""

    user_id: str
    email: str | None = None


class AuthError(Exception):
    """Token missing, invalid, or expired (safe to surface as 401)."""

    def __init__(self, message: str = "invalid or expired token") -> None:
        super().__init__(message)
        self.message = message


class AuthPort(Protocol):
    """Verify bearer ID tokens and return the authenticated user."""

    async def verify_token(self, token: str) -> AuthenticatedUser:
        """Validate ``token`` and return the user.

        Raises:
            AuthError: if the token is invalid, expired, or otherwise untrusted.
        """
        ...
