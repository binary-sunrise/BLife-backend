from __future__ import annotations

from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.observation import BLiffeObservation
from app.models.survey import BLiffeSurvey
from app.repositories.base import BaseRepository


class SurveyRepository(BaseRepository[BLiffeSurvey]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BLiffeSurvey, session)

    async def list_surveys(
        self,
        project_id: str | None = None,
        ward_id: str | None = None,
        lead_observer: str | None = None,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        obs_count_sq = (
            select(func.count(BLiffeObservation.id))
            .where(BLiffeObservation.surveyId == BLiffeSurvey.id)
            .correlate(BLiffeSurvey)
            .scalar_subquery()
        )

        query = select(BLiffeSurvey, obs_count_sq.label("observation_count"))

        if project_id:
            query = query.where(BLiffeSurvey.projectId == project_id)
        if ward_id:
            query = query.where(BLiffeSurvey.wardId == ward_id)
        if lead_observer:
            query = query.where(BLiffeSurvey.leadObserver.ilike(f"%{lead_observer}%"))
        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    BLiffeSurvey.leadObserver.ilike(search_pattern),
                    BLiffeSurvey.surveyMethod.ilike(search_pattern),
                    BLiffeSurvey.habitatType.ilike(search_pattern),
                    BLiffeSurvey.targetGroup.ilike(search_pattern),
                    BLiffeSurvey.weatherNotes.ilike(search_pattern),
                )
            )

        query = query.order_by(BLiffeSurvey.createdAt.desc())
        result = await self.session.execute(query)

        surveys = []
        for survey, obs_count in result.all():
            surveys.append(
                {
                    "id": survey.id,
                    "projectId": survey.projectId,
                    "wardId": survey.wardId,
                    "leadObserver": survey.leadObserver,
                    "teamMembers": survey.teamMembers,
                    "surveyMethod": survey.surveyMethod or "",
                    "habitatType": survey.habitatType or "",
                    "targetGroup": survey.targetGroup or "",
                    "startTime": survey.startTime,
                    "endTime": survey.endTime,
                    "weatherNotes": survey.weatherNotes or "",
                    "createdAt": survey.createdAt.isoformat() if survey.createdAt else "",
                    "updatedAt": survey.updatedAt.isoformat() if survey.updatedAt else "",
                    "syncStatus": survey.syncStatus,
                    "observationCount": obs_count or 0,
                }
            )
        return surveys

    async def get_by_id_with_counts(self, survey_id: str) -> dict[str, Any] | None:
        obs_count_sq = (
            select(func.count(BLiffeObservation.id))
            .where(BLiffeObservation.surveyId == BLiffeSurvey.id)
            .correlate(BLiffeSurvey)
            .scalar_subquery()
        )

        stmt = select(BLiffeSurvey, obs_count_sq.label("observation_count")).where(
            BLiffeSurvey.id == survey_id
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if not row:
            return None
        survey, obs_count = row
        return {
            "id": survey.id,
            "projectId": survey.projectId,
            "wardId": survey.wardId,
            "leadObserver": survey.leadObserver,
            "teamMembers": survey.teamMembers,
            "surveyMethod": survey.surveyMethod or "",
            "habitatType": survey.habitatType or "",
            "targetGroup": survey.targetGroup or "",
            "startTime": survey.startTime,
            "endTime": survey.endTime,
            "weatherNotes": survey.weatherNotes or "",
            "createdAt": survey.createdAt.isoformat() if survey.createdAt else "",
            "updatedAt": survey.updatedAt.isoformat() if survey.updatedAt else "",
            "syncStatus": survey.syncStatus,
            "observationCount": obs_count or 0,
        }
