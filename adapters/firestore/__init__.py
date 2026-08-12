"""Firestore adapters (cloud SDK allowed here only — F55)."""

from adapters.firestore.repositories import (
    FirestorePortfolioRepository,
    FirestorePositionRepository,
    FirestoreProfileRepository,
)

__all__ = [
    "FirestorePortfolioRepository",
    "FirestorePositionRepository",
    "FirestoreProfileRepository",
]
