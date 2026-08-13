"""Profile endpoints (auth-protected, per-user isolation)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_current_user, get_profile_repo
from api.schemas import ProfileBody
from core.portfolio.models import Profile
from core.ports.auth import AuthenticatedUser
from core.ports.repositories import ProfileRepository

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    repo: Annotated[ProfileRepository, Depends(get_profile_repo)],
) -> Profile:
    profile = await repo.get(user.user_id)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="profile not found")
    return profile


@router.put("")
async def put_profile(
    body: ProfileBody,
    user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    repo: Annotated[ProfileRepository, Depends(get_profile_repo)],
) -> Profile:
    profile = Profile(user_id=user.user_id, **body.model_dump())
    await repo.upsert(profile)
    return profile
