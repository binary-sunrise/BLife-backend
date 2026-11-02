from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import Session, User, UserProfile
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email.lower().strip())
            .options(
                selectinload(User.accounts),
                selectinload(User.profile),
                selectinload(User.sessions),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_id_with_relations(self, user_id: str) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.accounts),
                selectinload(User.profile),
                selectinload(User.sessions),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_profile_by_user_id(self, user_id: str) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.userId == user_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_profile_by_email(self, email: str) -> UserProfile | None:
        stmt = select(UserProfile).where(UserProfile.email == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_any_profile(self) -> UserProfile | None:
        stmt = select(UserProfile).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_session_by_token(self, token: str) -> Session | None:
        stmt = (
            select(Session)
            .where(Session.token == token)
            .options(
                selectinload(Session.user).selectinload(User.profile),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def delete_sessions_by_token(self, token: str) -> int:
        stmt = delete(Session).where(Session.token == token)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return getattr(res, "rowcount", 0) or 0
