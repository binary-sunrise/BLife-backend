from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import AvatarPresetId, AvatarType


class UserProfileSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    fullName: str
    name: str | None = None
    displayName: str
    email: str
    bio: str = ""
    avatarType: AvatarType = AvatarType.PRESET
    avatarPresetId: AvatarPresetId = AvatarPresetId.USER
    avatarCustomUrl: str | None = None
    updatedAt: str


class ProfileUpdateInputSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fullName: str = Field(min_length=1)
    displayName: str | None = None
    bio: str | None = ""
    avatarType: AvatarType = AvatarType.PRESET
    avatarPresetId: AvatarPresetId = AvatarPresetId.USER
    avatarCustomUrl: str | None = None


class RegisterInputSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    fullName: str = Field(min_length=2)
    email: EmailStr
    password: str = Field(min_length=6)


class LoginInputSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    email: EmailStr
    password: str = Field(min_length=6)


class AuthResponseSchema(BaseModel):
    user: UserProfileSchema
    token: str
    message: str | None = None
