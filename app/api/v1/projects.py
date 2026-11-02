from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.core.exceptions import EntityNotFoundException
from app.core.security import generate_uuid
from app.models.project import BLiffeProject
from app.models.ward import BLiffeWard
from app.repositories.project_repo import ProjectRepository
from app.repositories.ward_repo import WardRepository
from app.schemas.project import (
    CreateProjectSchema,
    ProjectDetailSchema,
    ProjectSchema,
    UpdateProjectSchema,
)
from app.schemas.ward import CreateWardSchema, WardSchema

router = APIRouter(tags=["Projects"])


@router.get("", response_model=list[ProjectSchema])
@router.get("/", response_model=list[ProjectSchema], include_in_schema=False)
async def list_projects(
    session: SessionDep,
    status: str | None = None,
    search: str | None = None,
    q: str | None = None,
    organization: str | None = None,
    targetRegion: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
) -> list[dict[str, Any]]:
    repo = ProjectRepository(session)
    search_term = search or q
    return await repo.list_projects(
        status=status,
        search=search_term,
        organization=organization,
        target_region=targetRegion,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
@router.post(
    "/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED, include_in_schema=False
)
async def create_project(input_data: CreateProjectSchema, session: SessionDep) -> dict[str, Any]:
    project_id = input_data.id or generate_uuid()
    project = BLiffeProject(
        id=project_id,
        name=input_data.name.strip(),
        description=input_data.description.strip() if input_data.description else "",
        startDate=input_data.startDate,
        status=(input_data.status.value if input_data.status else "active"),
        organization=input_data.organization.strip() if input_data.organization else "",
        targetRegion=input_data.targetRegion.strip() if input_data.targetRegion else "",
        syncStatus=(input_data.syncStatus.value if input_data.syncStatus else "synced"),
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)

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
        "observationCount": 0,
        "wardCount": 0,
        "surveyCount": 0,
    }


@router.get("/{id}", response_model=ProjectDetailSchema)
async def get_project(id: str, session: SessionDep) -> dict[str, Any]:
    repo = ProjectRepository(session)
    project = await repo.get_by_id_with_details(id)
    if not project:
        raise EntityNotFoundException("Project not found")
    return project


@router.put("/{id}", response_model=ProjectSchema)
async def update_project(
    id: str, input_data: UpdateProjectSchema, session: SessionDep
) -> dict[str, Any]:
    repo = ProjectRepository(session)
    project = await repo.get_by_id(id)
    if not project:
        raise EntityNotFoundException("Project not found")

    if input_data.name is not None:
        project.name = input_data.name.strip()
    if input_data.description is not None:
        project.description = input_data.description.strip()
    if input_data.startDate is not None:
        project.startDate = input_data.startDate
    if input_data.status is not None:
        project.status = (
            input_data.status.value if hasattr(input_data.status, "value") else input_data.status
        )
    if input_data.organization is not None:
        project.organization = input_data.organization.strip()
    if input_data.targetRegion is not None:
        project.targetRegion = input_data.targetRegion.strip()
    if input_data.syncStatus is not None:
        project.syncStatus = (
            input_data.syncStatus.value
            if hasattr(input_data.syncStatus, "value")
            else input_data.syncStatus
        )

    await session.commit()
    details = await repo.get_by_id_with_details(id)
    assert details is not None
    return details


@router.delete("/{id}")
async def delete_project(id: str, session: SessionDep) -> dict[str, Any]:
    repo = ProjectRepository(session)
    project = await repo.get_by_id(id)
    if not project:
        raise EntityNotFoundException("Project not found")
    await repo.delete(project)
    await session.commit()
    return {"success": True, "message": "Project deleted successfully"}


@router.get("/{project_id}/wards", response_model=list[WardSchema])
async def list_project_wards(project_id: str, session: SessionDep) -> list[dict[str, Any]]:
    repo = WardRepository(session)
    wards = await repo.list_wards(project_id=project_id)
    return [
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
        for w in wards
    ]


@router.post("/{project_id}/wards", response_model=WardSchema, status_code=status.HTTP_201_CREATED)
async def create_project_ward(
    project_id: str, input_data: CreateWardSchema, session: SessionDep
) -> dict[str, Any]:
    ward_id = input_data.id or generate_uuid()
    ward = BLiffeWard(
        id=ward_id,
        projectId=project_id,
        wardNumber=input_data.wardNumber.strip(),
        wardName=input_data.wardName.strip(),
        localBodyName=input_data.localBodyName.strip() if input_data.localBodyName else "",
        district=input_data.district.strip() if input_data.district else "",
        state=input_data.state.strip() if input_data.state else "",
        keyLandmarks=input_data.keyLandmarks.strip() if input_data.keyLandmarks else "",
        syncStatus=(input_data.syncStatus.value if input_data.syncStatus else "synced"),
    )
    session.add(ward)
    await session.commit()
    await session.refresh(ward)

    return {
        "id": ward.id,
        "projectId": ward.projectId,
        "wardNumber": ward.wardNumber,
        "wardName": ward.wardName,
        "localBodyName": ward.localBodyName or "",
        "district": ward.district or "",
        "state": ward.state or "",
        "keyLandmarks": ward.keyLandmarks or "",
        "createdAt": ward.createdAt.isoformat() if ward.createdAt else "",
        "updatedAt": ward.updatedAt.isoformat() if ward.updatedAt else "",
        "syncStatus": ward.syncStatus,
    }
