from __future__ import annotations

from typing import Any

from sqlalchemy import any_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observation import BLiffeObservation
from app.repositories.base import BaseRepository


class ObservationRepository(BaseRepository[BLiffeObservation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BLiffeObservation, session)

    async def list_observations(
        self,
        project_id: str | None = None,
        ward_id: str | None = None,
        survey_id: str | None = None,
        status: str | None = None,
        identification_status: str | None = None,
        organism_status: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BLiffeObservation]:
        query = select(BLiffeObservation)

        if project_id:
            query = query.where(
                or_(
                    BLiffeObservation.projectId == project_id,
                    any_(BLiffeObservation.projectIds) == project_id,
                )
            )

        if ward_id:
            query = query.where(BLiffeObservation.wardId == ward_id)

        if survey_id:
            query = query.where(BLiffeObservation.surveyId == survey_id)

        filter_status = status or identification_status
        if filter_status and filter_status != "All":
            query = query.where(BLiffeObservation.identificationStatus == filter_status)

        if organism_status and organism_status != "All":
            query = query.where(BLiffeObservation.organismStatus == organism_status)

        if tag:
            query = query.where(any_(BLiffeObservation.tags) == tag)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    BLiffeObservation.speciesName.ilike(search_pattern),
                    BLiffeObservation.scientificName.ilike(search_pattern),
                    BLiffeObservation.localName.ilike(search_pattern),
                    BLiffeObservation.notes.ilike(search_pattern),
                )
            )

        query = query.order_by(BLiffeObservation.createdAt.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def upsert(self, obs_data: dict[str, Any]) -> BLiffeObservation:
        obs_id = obs_data.get("id")
        existing: BLiffeObservation | None = None
        if obs_id:
            existing = await self.get_by_id(obs_id)

        if existing:
            for key, val in obs_data.items():
                if hasattr(existing, key) and val is not None:
                    setattr(existing, key, val)
            await self.session.flush()
            return existing

        new_obs = BLiffeObservation(**obs_data)
        self.session.add(new_obs)
        await self.session.flush()
        return new_obs
