from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ward import BLiffeWard
from app.repositories.base import BaseRepository


class WardRepository(BaseRepository[BLiffeWard]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BLiffeWard, session)

    async def list_wards(
        self,
        project_id: str | None = None,
        district: str | None = None,
        search: str | None = None,
    ) -> list[BLiffeWard]:
        query = select(BLiffeWard)
        if project_id:
            query = query.where(BLiffeWard.projectId == project_id)
        if district:
            query = query.where(BLiffeWard.district.ilike(f"%{district}%"))
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    BLiffeWard.wardName.ilike(search_pattern),
                    BLiffeWard.wardNumber.ilike(search_pattern),
                    BLiffeWard.localBodyName.ilike(search_pattern),
                )
            )

        query = query.order_by(BLiffeWard.wardNumber.asc())
        result = await self.session.execute(query)
        return list(result.scalars().all())
