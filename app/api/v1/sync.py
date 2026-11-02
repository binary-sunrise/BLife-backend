from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.schemas.sync import (
    SyncPayloadSchema,
    SyncResponseSchema,
    SyncStatusResponseSchema,
)
from app.services.sync_service import SyncService

router = APIRouter(tags=["Offline Sync"])


@router.post("", response_model=SyncResponseSchema)
@router.post("/", response_model=SyncResponseSchema, include_in_schema=False)
async def sync_all(payload: SyncPayloadSchema, session: SessionDep) -> SyncResponseSchema:
    service = SyncService(session)
    return await service.sync_all(payload)


@router.get("/status", response_model=SyncStatusResponseSchema)
async def sync_status(session: SessionDep) -> SyncStatusResponseSchema:
    service = SyncService(session)
    return await service.get_status()
