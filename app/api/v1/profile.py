from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.user import ProfileUpdateInputSchema, UserProfileSchema
from app.services.auth_service import AuthService

router = APIRouter(tags=["Profile"])


@router.get("", response_model=UserProfileSchema)
@router.get("/", response_model=UserProfileSchema, include_in_schema=False)
async def get_profile(
    session: SessionDep,
    current_user: CurrentUserDep,
    authorization: Annotated[str | None, Header()] = None,
) -> UserProfileSchema:
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    service = AuthService(session)
    return await service.get_profile(current_user.user_id, token)


@router.put("", response_model=UserProfileSchema)
@router.put("/", response_model=UserProfileSchema, include_in_schema=False)
@router.patch("", response_model=UserProfileSchema)
@router.patch("/", response_model=UserProfileSchema, include_in_schema=False)
async def update_profile(
    input_data: ProfileUpdateInputSchema,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> UserProfileSchema:
    service = AuthService(session)
    return await service.update_profile(current_user.user_id, input_data)
