from __future__ import annotations

from typing import Any

from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.core.exceptions import EntityNotFoundException
from app.core.security import generate_uuid
from app.models.ward import BLiffeWard
from app.repositories.ward_repo import WardRepository
from app.schemas.ward import (
    CreateWardSchema,
    UpdateWardSchema,
    WardIdentificationResultSchema,
    WardIdentifyRequestSchema,
    WardSchema,
)
from app.services.ward_service import identify_ward_from_coordinates

router = APIRouter(tags=["Wards"])


@router.post("/identify", response_model=WardIdentificationResultSchema)
async def identify_ward_post(body: WardIdentifyRequestSchema) -> WardIdentificationResultSchema:
    return identify_ward_from_coordinates(body.latitude, body.longitude)


@router.get("/identify", response_model=WardIdentificationResultSchema)
async def identify_ward_get(latitude: float, longitude: float) -> WardIdentificationResultSchema:
    return identify_ward_from_coordinates(latitude, longitude)


@router.get("", response_model=list[WardSchema])
@router.get("/", response_model=list[WardSchema], include_in_schema=False)
async def list_wards(
    session: SessionDep,
    projectId: str | None = None,
    district: str | None = None,
    search: str | None = None,
) -> list[dict[str, Any]]:
    repo = WardRepository(session)
    wards = await repo.list_wards(project_id=projectId, district=district, search=search)
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


@router.post("", response_model=WardSchema, status_code=status.HTTP_201_CREATED)
@router.post(
    "/", response_model=WardSchema, status_code=status.HTTP_201_CREATED, include_in_schema=False
)
async def create_ward(input_data: CreateWardSchema, session: SessionDep) -> dict[str, Any]:
    ward_id = input_data.id or generate_uuid()
    ward = BLiffeWard(
        id=ward_id,
        projectId=input_data.projectId,
        wardNumber=input_data.wardNumber.strip(),
        wardName=input_data.wardName.strip(),
        localBodyName=input_data.localBodyName.strip() if input_data.localBodyName else "",
        district=input_data.district.strip() if input_data.district else "",
        state=input_data.state.strip() if input_data.state else "",
        keyLandmarks=input_data.keyLandmarks.strip() if input_data.keyLandmarks else "",
        syncStatus=input_data.syncStatus.value if input_data.syncStatus else "synced",
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


@router.get("/{id}", response_model=WardSchema)
async def get_ward(id: str, session: SessionDep) -> dict[str, Any]:
    repo = WardRepository(session)
    ward = await repo.get_by_id(id)
    if not ward:
        raise EntityNotFoundException("Ward not found")

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


@router.put("/{id}", response_model=WardSchema)
async def update_ward(id: str, input_data: UpdateWardSchema, session: SessionDep) -> dict[str, Any]:
    repo = WardRepository(session)
    ward = await repo.get_by_id(id)
    if not ward:
        raise EntityNotFoundException("Ward not found")

    if input_data.wardNumber is not None:
        ward.wardNumber = input_data.wardNumber.strip()
    if input_data.wardName is not None:
        ward.wardName = input_data.wardName.strip()
    if input_data.localBodyName is not None:
        ward.localBodyName = input_data.localBodyName.strip()
    if input_data.district is not None:
        ward.district = input_data.district.strip()
    if input_data.state is not None:
        ward.state = input_data.state.strip()
    if input_data.keyLandmarks is not None:
        ward.keyLandmarks = input_data.keyLandmarks.strip()
    if input_data.syncStatus is not None:
        ward.syncStatus = (
            input_data.syncStatus.value
            if hasattr(input_data.syncStatus, "value")
            else input_data.syncStatus
        )

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


@router.delete("/{id}")
async def delete_ward(id: str, session: SessionDep) -> dict[str, Any]:
    repo = WardRepository(session)
    ward = await repo.get_by_id(id)
    if not ward:
        raise EntityNotFoundException("Ward not found")
    await repo.delete(ward)
    await session.commit()
    return {"success": True, "message": "Ward deleted successfully"}
