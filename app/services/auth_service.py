from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, AuthenticationException
from app.core.security import (
    calculate_session_expiration,
    generate_session_token,
    generate_uuid,
    hash_password,
    verify_password,
)
from app.models.user import Account, Session, User, UserProfile
from app.repositories.user_repo import UserRepository
from app.schemas.user import (
    AuthResponseSchema,
    LoginInputSchema,
    ProfileUpdateInputSchema,
    RegisterInputSchema,
    UserProfileSchema,
)
from app.services.s3_service import S3StorageService

DEFAULT_MOCK_PROFILE = UserProfileSchema(
    id="bliffe-demo-user",
    fullName="Veena V",
    displayName="Veena",
    email="veena@field.b-liffe.org",
    bio="Biodiversity enthusiast & field observer documenting flora, fauna, and local ecosystems.",
    avatarType="preset",
    avatarPresetId="user",
    avatarCustomUrl=None,
    updatedAt=datetime.now(UTC).isoformat(),
)


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, input_data: RegisterInputSchema) -> AuthResponseSchema:
        normalized_email = input_data.email.lower().strip()
        existing = await self.user_repo.get_by_email(normalized_email)
        if existing:
            raise AppException("User with this email already exists", status_code=400)

        # Check if profile with email exists
        existing_profile = await self.user_repo.get_profile_by_email(normalized_email)

        user_id = generate_uuid()
        hashed = hash_password(input_data.password)
        first_name = re.split(r"\s+", input_data.fullName.strip())[0]

        user = User(
            id=user_id,
            email=normalized_email,
            name=input_data.fullName.strip(),
            givenName=first_name,
            emailVerified=True,
        )
        self.session.add(user)
        await self.session.flush()

        account = Account(
            id=generate_uuid(),
            accountId=normalized_email,
            providerId="credential",
            password=hashed,
            userId=user.id,
        )
        self.session.add(account)

        if existing_profile:
            profile = existing_profile
            profile.userId = user.id
            profile.fullName = input_data.fullName.strip()
            profile.displayName = first_name
        else:
            profile = UserProfile(
                id=generate_uuid(),
                userId=user.id,
                fullName=input_data.fullName.strip(),
                displayName=first_name,
                email=normalized_email,
                bio="Biodiversity enthusiast & field observer documenting flora, fauna, and local ecosystems.",
                avatarType="preset",
                avatarPresetId="user",
                avatarCustomUrl=None,
            )
            self.session.add(profile)

        token = generate_session_token()
        session_obj = Session(
            id=generate_uuid(),
            userId=user.id,
            token=token,
            expiresAt=calculate_session_expiration(),
        )
        self.session.add(session_obj)
        await self.session.commit()

        user_profile_schema = UserProfileSchema(
            id=profile.id,
            fullName=profile.fullName,
            name=profile.fullName,
            displayName=profile.displayName,
            email=profile.email,
            bio=profile.bio,
            avatarType=profile.avatarType,
            avatarPresetId=profile.avatarPresetId,
            avatarCustomUrl=profile.avatarCustomUrl,
            updatedAt=profile.updatedAt.isoformat()
            if profile.updatedAt
            else datetime.now(UTC).isoformat(),
        )

        return AuthResponseSchema(
            user=user_profile_schema,
            token=token,
            message="Account created successfully",
        )

    async def login(self, input_data: LoginInputSchema) -> AuthResponseSchema:
        normalized_email = input_data.email.lower().strip()
        user = await self.user_repo.get_by_email(normalized_email)
        if not user:
            raise AuthenticationException("Invalid email or password")

        # Find credential account
        cred_account = next((acc for acc in user.accounts if acc.providerId == "credential"), None)
        if not cred_account or not verify_password(input_data.password, cred_account.password):
            raise AuthenticationException("Invalid email or password")

        # Ensure user profile exists
        profile = user.profile
        if not profile:
            first_name = (
                user.givenName or user.name.split()[0]
                if user.name
                else normalized_email.split("@")[0]
            )
            profile = UserProfile(
                id=generate_uuid(),
                userId=user.id,
                fullName=user.name or normalized_email.split("@")[0],
                displayName=first_name,
                email=user.email,
                bio="Biodiversity enthusiast & field observer documenting flora, fauna, and local ecosystems.",
                avatarType="preset",
                avatarPresetId="user",
                avatarCustomUrl=None,
            )
            self.session.add(profile)
            await self.session.flush()

        token = generate_session_token()
        session_obj = Session(
            id=generate_uuid(),
            userId=user.id,
            token=token,
            expiresAt=calculate_session_expiration(),
        )
        self.session.add(session_obj)
        await self.session.commit()

        user_profile_schema = UserProfileSchema(
            id=profile.id,
            fullName=profile.fullName,
            name=profile.fullName,
            displayName=profile.displayName,
            email=profile.email,
            bio=profile.bio,
            avatarType=profile.avatarType,
            avatarPresetId=profile.avatarPresetId,
            avatarCustomUrl=profile.avatarCustomUrl,
            updatedAt=profile.updatedAt.isoformat()
            if profile.updatedAt
            else datetime.now(UTC).isoformat(),
        )

        return AuthResponseSchema(
            user=user_profile_schema,
            token=token,
            message="Logged in successfully",
        )

    async def logout(self, token: str | None) -> dict[str, Any]:
        if token:
            await self.user_repo.delete_sessions_by_token(token)
            await self.session.commit()
        return {"success": True, "message": "Logged out successfully"}

    async def get_profile(self, user_id: str | None, token: str | None) -> UserProfileSchema:
        if token:
            session_obj = await self.user_repo.get_session_by_token(token)
            if session_obj and session_obj.expiresAt > datetime.now(UTC).replace(tzinfo=None):
                user_id = session_obj.userId

        if user_id:
            profile = await self.user_repo.get_profile_by_user_id(user_id)
            if profile:
                return UserProfileSchema(
                    id=profile.id,
                    fullName=profile.fullName,
                    displayName=profile.displayName,
                    email=profile.email,
                    bio=profile.bio,
                    avatarType=profile.avatarType,
                    avatarPresetId=profile.avatarPresetId,
                    avatarCustomUrl=profile.avatarCustomUrl,
                    updatedAt=profile.updatedAt.isoformat()
                    if profile.updatedAt
                    else datetime.now(UTC).isoformat(),
                )

        any_profile = await self.user_repo.get_any_profile()
        if any_profile:
            return UserProfileSchema(
                id=any_profile.id,
                fullName=any_profile.fullName,
                displayName=any_profile.displayName,
                email=any_profile.email,
                bio=any_profile.bio,
                avatarType=any_profile.avatarType,
                avatarPresetId=any_profile.avatarPresetId,
                avatarCustomUrl=any_profile.avatarCustomUrl,
                updatedAt=any_profile.updatedAt.isoformat()
                if any_profile.updatedAt
                else datetime.now(UTC).isoformat(),
            )

        return DEFAULT_MOCK_PROFILE

    async def update_profile(
        self, user_id: str | None, input_data: ProfileUpdateInputSchema
    ) -> UserProfileSchema:
        profile: UserProfile | None = None
        if user_id:
            profile = await self.user_repo.get_profile_by_user_id(user_id)

        if not profile:
            profile = await self.user_repo.get_any_profile()

        trimmed_full_name = input_data.fullName.strip()
        display_name = (
            input_data.displayName.strip()
            if input_data.displayName
            else trimmed_full_name.split()[0]
        )
        bio = (input_data.bio or "").strip()
        avatar_custom_url = (
            input_data.avatarCustomUrl if input_data.avatarType == "upload" else None
        )
        if avatar_custom_url:
            s3_service = S3StorageService()
            avatar_custom_url = s3_service.upload_base64_if_needed(
                avatar_custom_url, folder="avatars"
            )

        if profile:
            profile.fullName = trimmed_full_name
            profile.displayName = display_name
            profile.bio = bio
            profile.avatarType = (
                input_data.avatarType.value
                if hasattr(input_data.avatarType, "value")
                else str(input_data.avatarType)
            )
            profile.avatarPresetId = (
                input_data.avatarPresetId.value
                if hasattr(input_data.avatarPresetId, "value")
                else str(input_data.avatarPresetId)
            )
            profile.avatarCustomUrl = avatar_custom_url
        else:
            profile = UserProfile(
                id=generate_uuid(),
                userId=user_id,
                fullName=trimmed_full_name,
                displayName=display_name,
                email=DEFAULT_MOCK_PROFILE.email,
                bio=bio,
                avatarType=input_data.avatarType.value
                if hasattr(input_data.avatarType, "value")
                else str(input_data.avatarType),
                avatarPresetId=input_data.avatarPresetId.value
                if hasattr(input_data.avatarPresetId, "value")
                else str(input_data.avatarPresetId),
                avatarCustomUrl=avatar_custom_url,
            )
            self.session.add(profile)

        await self.session.commit()
        await self.session.refresh(profile)

        return UserProfileSchema(
            id=profile.id,
            fullName=profile.fullName,
            displayName=profile.displayName,
            email=profile.email,
            bio=profile.bio,
            avatarType=profile.avatarType,
            avatarPresetId=profile.avatarPresetId,
            avatarCustomUrl=profile.avatarCustomUrl,
            updatedAt=profile.updatedAt.isoformat()
            if profile.updatedAt
            else datetime.now(UTC).isoformat(),
        )
