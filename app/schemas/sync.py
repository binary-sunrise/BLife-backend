from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.observation import CreateObservationSchema
from app.schemas.project import CreateProjectSchema
from app.schemas.survey import CreateSurveySchema
from app.schemas.ward import CreateWardSchema


class SyncSyncedCounts(BaseModel):
    projects: int = 0
    wards: int = 0
    surveys: int = 0
    observations: int = 0


class SyncPayloadSchema(BaseModel):
    projects: list[CreateProjectSchema] = Field(default_factory=list)
    wards: list[CreateWardSchema] = Field(default_factory=list)
    surveys: list[CreateSurveySchema] = Field(default_factory=list)
    observations: list[CreateObservationSchema] = Field(default_factory=list)


class SyncResponseSchema(BaseModel):
    success: bool
    timestamp: str
    synced: SyncSyncedCounts


class SyncStatusResponseSchema(BaseModel):
    status: str
    timestamp: str
    counts: SyncSyncedCounts
