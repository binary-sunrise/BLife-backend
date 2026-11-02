from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.user import (
    AuthResponseSchema,
    LoginInputSchema,
    RegisterInputSchema,
    UserProfileSchema,
)
from app.services.auth_service import AuthService

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=AuthResponseSchema, status_code=status.HTTP_201_CREATED)
async def register(input_data: RegisterInputSchema, session: SessionDep) -> AuthResponseSchema:
    service = AuthService(session)
    return await service.register(input_data)


@router.post("/login", response_model=AuthResponseSchema)
async def login(input_data: LoginInputSchema, session: SessionDep) -> AuthResponseSchema:
    service = AuthService(session)
    return await service.login(input_data)


@router.post("/logout")
async def logout(
    session: SessionDep,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, str | bool]:
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    service = AuthService(session)
    return await service.logout(token)


@router.get("/me", response_model=UserProfileSchema)
async def get_me(
    session: SessionDep,
    current_user: CurrentUserDep,
    authorization: Annotated[str | None, Header()] = None,
) -> UserProfileSchema:
    token: str | None = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    service = AuthService(session)
    return await service.get_profile(current_user.user_id, token)
