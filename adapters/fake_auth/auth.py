"""Fake AuthPort — known tokens for tests/local (no network)."""

from __future__ import annotations

from core.ports.auth import AuthenticatedUser, AuthError

# Well-known fake bearer used in hermetic tests.
FAKE_VALID_TOKEN = "fake-token-alice"
FAKE_USER = AuthenticatedUser(user_id="alice", email="alice@example.com")


class FakeAuthAdapter:
    """Maps a canned token to a canned user; everything else is AuthError."""

    def __init__(
        self,
        *,
        valid_token: str = FAKE_VALID_TOKEN,
        user: AuthenticatedUser | None = None,
    ) -> None:
        self._valid_token = valid_token
        self._user = user or FAKE_USER

    async def verify_token(self, token: str) -> AuthenticatedUser:
        if not token or not token.strip():
            raise AuthError("missing token")
        if token == self._valid_token:
            return self._user.model_copy()
        raise AuthError("invalid or expired token")
