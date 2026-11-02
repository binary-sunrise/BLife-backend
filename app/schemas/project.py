from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import ProjectStatus, SyncStatus


class ProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    name: str
    description: str | None = ""
    startDate: str | None = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    organization: str | None = ""
    targetRegion: str | None = ""
    createdAt: str
    updatedAt: str
    syncStatus: SyncStatus = SyncStatus.SYNCED
    observationCount: int | None = 0
    wardCount: int | None = 0
    surveyCount: int | None = 0


class CreateProjectSchema(BaseModel):
    id: str | None = None
    name: str = Field(min_length=1)
    description: str | None = ""
    startDate: str | None = None
    status: ProjectStatus | None = ProjectStatus.ACTIVE
    organization: str | None = ""
    targetRegion: str | None = ""
    syncStatus: SyncStatus | None = SyncStatus.SYNCED


class UpdateProjectSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    startDate: str | None = None
    status: ProjectStatus | None = None
    organization: str | None = None
    targetRegion: str | None = None
    syncStatus: SyncStatus | None = None


class ProjectDetailSchema(ProjectSchema):
    wards: list[dict[str, Any]] = Field(default_factory=list)
    surveys: list[dict[str, Any]] = Field(default_factory=list)
