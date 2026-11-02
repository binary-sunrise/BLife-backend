from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.core.exceptions import EntityNotFoundException
from app.core.security import generate_uuid
from app.models.survey import BLiffeSurvey
from app.repositories.survey_repo import SurveyRepository
from app.schemas.survey import (
    CreateSurveySchema,
    SurveySchema,
    UpdateSurveySchema,
)

router = APIRouter(tags=["Surveys"])


@router.get("", response_model=list[SurveySchema])
@router.get("/", response_model=list[SurveySchema], include_in_schema=False)
async def list_surveys(
    session: SessionDep,
    projectId: str | None = None,
    wardId: str | None = None,
    leadObserver: str | None = None,
    search: str | None = None,
) -> list[dict[str, Any]]:
    repo = SurveyRepository(session)
    return await repo.list_surveys(
        project_id=projectId,
        ward_id=wardId,
        lead_observer=leadObserver,
        search=search,
    )


@router.post("", response_model=SurveySchema, status_code=status.HTTP_201_CREATED)
@router.post(
    "/", response_model=SurveySchema, status_code=status.HTTP_201_CREATED, include_in_schema=False
)
async def create_survey(input_data: CreateSurveySchema, session: SessionDep) -> dict[str, Any]:
    survey_id = input_data.id or generate_uuid()
    survey = BLiffeSurvey(
        id=survey_id,
        projectId=input_data.projectId,
        wardId=input_data.wardId,
        leadObserver=input_data.leadObserver.strip(),
        teamMembers=input_data.teamMembers,
        surveyMethod=input_data.surveyMethod or "Opportunistic Encounter",
        habitatType=input_data.habitatType or "Urban Park / Garden",
        targetGroup=input_data.targetGroup or "All Biodiversity",
        startTime=input_data.startTime,
        endTime=input_data.endTime,
        weatherNotes=input_data.weatherNotes.strip() if input_data.weatherNotes else "",
        syncStatus=(input_data.syncStatus.value if input_data.syncStatus else "synced"),
    )
    session.add(survey)
    await session.commit()
    await session.refresh(survey)

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
        "observationCount": 0,
    }


@router.get("/{id}", response_model=SurveySchema)
async def get_survey(id: str, session: SessionDep) -> dict[str, Any]:
    repo = SurveyRepository(session)
    survey = await repo.get_by_id_with_counts(id)
    if not survey:
        raise EntityNotFoundException("Survey not found")
    return survey


@router.put("/{id}", response_model=SurveySchema)
async def update_survey(
    id: str, input_data: UpdateSurveySchema, session: SessionDep
) -> dict[str, Any]:
    repo = SurveyRepository(session)
    survey = await repo.get_by_id(id)
    if not survey:
        raise EntityNotFoundException("Survey not found")

    if input_data.leadObserver is not None:
        survey.leadObserver = input_data.leadObserver.strip()
    if input_data.teamMembers is not None:
        survey.teamMembers = input_data.teamMembers
    if input_data.surveyMethod is not None:
        survey.surveyMethod = input_data.surveyMethod
    if input_data.habitatType is not None:
        survey.habitatType = input_data.habitatType
    if input_data.targetGroup is not None:
        survey.targetGroup = input_data.targetGroup
    if input_data.startTime is not None:
        survey.startTime = input_data.startTime
    if input_data.endTime is not None:
        survey.endTime = input_data.endTime
    if input_data.weatherNotes is not None:
        survey.weatherNotes = input_data.weatherNotes
    if input_data.syncStatus is not None:
        survey.syncStatus = (
            input_data.syncStatus.value
            if hasattr(input_data.syncStatus, "value")
            else input_data.syncStatus
        )

    await session.commit()
    updated = await repo.get_by_id_with_counts(id)
    assert updated is not None
    return updated


@router.delete("/{id}")
async def delete_survey(id: str, session: SessionDep) -> dict[str, Any]:
    repo = SurveyRepository(session)
    survey = await repo.get_by_id(id)
    if not survey:
        raise EntityNotFoundException("Survey not found")
    await repo.delete(survey)
    await session.commit()
    return {"success": True, "message": "Survey deleted successfully"}
