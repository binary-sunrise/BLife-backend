from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    pass


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sub: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    givenName: Mapped[str | None] = mapped_column(String, nullable=True)
    familyName: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    emailVerified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    customUserId: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar: Mapped[str | None] = mapped_column(String, nullable=True)
    organisation: Mapped[str | None] = mapped_column(String, nullable=True)

    sessions: Mapped[list[Session]] = relationship(
        "Session", back_populates="user", cascade="all, delete-orphan"
    )
    accounts: Mapped[list[Account]] = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )
    profile: Mapped[UserProfile | None] = relationship(
        "UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    userId: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True
    )
    fullName: Mapped[str] = mapped_column(String, nullable=False)
    displayName: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    avatarType: Mapped[str] = mapped_column(String, default="preset", nullable=False)
    avatarPresetId: Mapped[str] = mapped_column(String, default="user", nullable=False)
    avatarCustomUrl: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped[User | None] = relationship("User", back_populates="profile")


class Session(Base, TimestampMixin):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    expiresAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    ipAddress: Mapped[str | None] = mapped_column(String, nullable=True)
    userAgent: Mapped[str | None] = mapped_column(String, nullable=True)
    userId: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    user: Mapped[User] = relationship("User", back_populates="sessions")


class Account(Base, TimestampMixin):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    accountId: Mapped[str] = mapped_column(String, nullable=False)
    providerId: Mapped[str] = mapped_column(String, nullable=False)
    userId: Mapped[str] = mapped_column(
        String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    accessToken: Mapped[str | None] = mapped_column(Text, nullable=True)
    refreshToken: Mapped[str | None] = mapped_column(Text, nullable=True)
    idToken: Mapped[str | None] = mapped_column(Text, nullable=True)
    accessTokenExpiresAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    refreshTokenExpiresAt: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    scope: Mapped[str | None] = mapped_column(String, nullable=True)
    password: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="accounts")


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    identifier: Mapped[str] = mapped_column(String, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String, nullable=False)
    expiresAt: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    createdAt: Mapped[datetime | None] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=True
    )
    updatedAt: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=True,
    )
