from __future__ import annotations

from typing import Any

from sqlalchemy import any_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.observation import BLiffeObservation
from app.models.project import BLiffeProject
from app.models.survey import BLiffeSurvey
from app.models.ward import BLiffeWard
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[BLiffeProject]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(BLiffeProject, session)

    async def list_projects(
        self,
        status: str | None = None,
        search: str | None = None,
        organization: str | None = None,
        target_region: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        # Correlated subqueries for counts to avoid cartesian product
        obs_count_sq = (
            select(func.count(BLiffeObservation.id))
            .where(
                or_(
                    BLiffeObservation.projectId == BLiffeProject.id,
                    BLiffeProject.id == any_(BLiffeObservation.projectIds),
                )
            )
            .correlate(BLiffeProject)
            .scalar_subquery()
        )

        wards_count_sq = (
            select(func.count(BLiffeWard.id))
            .where(BLiffeWard.projectId == BLiffeProject.id)
            .correlate(BLiffeProject)
            .scalar_subquery()
        )

        surveys_count_sq = (
            select(func.count(BLiffeSurvey.id))
            .where(BLiffeSurvey.projectId == BLiffeProject.id)
            .correlate(BLiffeProject)
            .scalar_subquery()
        )

        query = select(
            BLiffeProject,
            obs_count_sq.label("observation_count"),
            wards_count_sq.label("ward_count"),
            surveys_count_sq.label("survey_count"),
        )

        if status:
            query = query.where(BLiffeProject.status == status)

        if search:
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    BLiffeProject.name.ilike(search_pattern),
                    BLiffeProject.description.ilike(search_pattern),
                    BLiffeProject.organization.ilike(search_pattern),
                    BLiffeProject.targetRegion.ilike(search_pattern),
                )
            )

        if organization:
            query = query.where(BLiffeProject.organization.ilike(f"%{organization}%"))

        if target_region:
            query = query.where(BLiffeProject.targetRegion.ilike(f"%{target_region}%"))

        query = query.order_by(BLiffeProject.createdAt.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)

        projects_with_counts = []
        for project, obs_count, ward_count, survey_count in result.all():
            projects_with_counts.append(
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description or "",
                    "startDate": project.startDate,
                    "status": project.status,
                    "organization": project.organization or "",
                    "targetRegion": project.targetRegion or "",
                    "createdAt": project.createdAt.isoformat() if project.createdAt else "",
                    "updatedAt": project.updatedAt.isoformat() if project.updatedAt else "",
                    "syncStatus": project.syncStatus,
                    "observationCount": obs_count or 0,
                    "wardCount": ward_count or 0,
                    "surveyCount": survey_count or 0,
                }
            )

        return projects_with_counts

    async def get_by_id_with_details(self, project_id: str) -> dict[str, Any] | None:
        stmt = (
            select(BLiffeProject)
            .where(BLiffeProject.id == project_id)
            .options(
                selectinload(BLiffeProject.wards),
                selectinload(BLiffeProject.surveys),
            )
        )
        result = await self.session.execute(stmt)
        project = result.scalars().first()
        if not project:
            return None

        # Fetch counts
        obs_res = await self.session.execute(
            select(func.count(BLiffeObservation.id)).where(
                or_(
                    BLiffeObservation.projectId == project.id,
                    any_(BLiffeObservation.projectIds) == project.id,
                )
            )
        )
        obs_count = obs_res.scalar_one()

        return {
            "id": project.id,
            "name": project.name,
            "description": project.description or "",
            "startDate": project.startDate,
            "status": project.status,
            "organization": project.organization or "",
            "targetRegion": project.targetRegion or "",
            "createdAt": project.createdAt.isoformat() if project.createdAt else "",
            "updatedAt": project.updatedAt.isoformat() if project.updatedAt else "",
            "syncStatus": project.syncStatus,
            "observationCount": obs_count or 0,
            "wardCount": len(project.wards),
            "surveyCount": len(project.surveys),
            "wards": [
                {
                    "id": w.id,
                    "projectId": w.projectId,
                    "wardNumber": w.wardNumber,
                    "wardName": w.wardName,
                    "localBodyName": w.localBodyName or "",
                    "district": w.district or "",
                    "state": w.state or "",
                    "keyLandmarks": w.keyLandmarks or "",
                    "createdAt": w.createdAt.isoformat() if w.createdAt else "",
                    "updatedAt": w.updatedAt.isoformat() if w.updatedAt else "",
                    "syncStatus": w.syncStatus,
                }
                for w in project.wards
            ],
            "surveys": [
                {
                    "id": s.id,
                    "projectId": s.projectId,
                    "wardId": s.wardId,
                    "leadObserver": s.leadObserver,
                    "teamMembers": s.teamMembers,
                    "surveyMethod": s.surveyMethod or "",
                    "habitatType": s.habitatType or "",
                    "targetGroup": s.targetGroup or "",
                    "startTime": s.startTime,
                    "endTime": s.endTime,
                    "weatherNotes": s.weatherNotes or "",
                    "createdAt": s.createdAt.isoformat() if s.createdAt else "",
                    "updatedAt": s.updatedAt.isoformat() if s.updatedAt else "",
                    "syncStatus": s.syncStatus,
                }
                for s in project.surveys
            ],
        }
