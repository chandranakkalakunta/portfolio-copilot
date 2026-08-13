"""Fake AuthPort — known tokens for tests/local (no network)."""

from __future__ import annotations

from core.ports.auth import AuthenticatedUser, AuthError

# Well-known fake bearers used in hermetic tests / local smoke.
FAKE_VALID_TOKEN = "fake-token-alice"
FAKE_TOKEN_BOB = "fake-token-bob"
FAKE_USER = AuthenticatedUser(user_id="alice", email="alice@example.com")
FAKE_USER_BOB = AuthenticatedUser(user_id="bob", email="bob@example.com")


class FakeAuthAdapter:
    """Maps known tokens to users; everything else is AuthError."""

    def __init__(
        self,
        *,
        valid_token: str = FAKE_VALID_TOKEN,
        user: AuthenticatedUser | None = None,
        token_map: dict[str, AuthenticatedUser] | None = None,
    ) -> None:
        if token_map is not None:
            self._token_map = {k: v.model_copy() for k, v in token_map.items()}
        else:
            self._token_map = {valid_token: (user or FAKE_USER).model_copy()}

    async def verify_token(self, token: str) -> AuthenticatedUser:
        if not token or not token.strip():
            raise AuthError("missing token")
        user = self._token_map.get(token)
        if user is not None:
            return user.model_copy()
        raise AuthError("invalid or expired token")
