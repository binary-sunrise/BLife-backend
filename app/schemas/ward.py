from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import SyncStatus


class WardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    projectId: str
    wardNumber: str
    wardName: str
    localBodyName: str | None = ""
    district: str | None = ""
    state: str | None = ""
    keyLandmarks: str | None = ""
    createdAt: str
    updatedAt: str
    syncStatus: SyncStatus = SyncStatus.SYNCED


class CreateWardSchema(BaseModel):
    id: str | None = None
    projectId: str = Field(min_length=1)
    wardNumber: str = Field(min_length=1)
    wardName: str = Field(min_length=1)
    localBodyName: str | None = ""
    district: str | None = ""
    state: str | None = ""
    keyLandmarks: str | None = ""
    syncStatus: SyncStatus | None = SyncStatus.SYNCED


class UpdateWardSchema(BaseModel):
    wardNumber: str | None = None
    wardName: str | None = None
    localBodyName: str | None = None
    district: str | None = None
    state: str | None = None
    keyLandmarks: str | None = None
    syncStatus: SyncStatus | None = None


class WardIdentifyRequestSchema(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class IdentifiedWardSchema(BaseModel):
    wardId: str
    wardNumber: str
    wardName: str
    localBodyName: str | None = None


class WardIdentificationResultSchema(BaseModel):
    status: str
    ward: IdentifiedWardSchema | None = None
    message: str
