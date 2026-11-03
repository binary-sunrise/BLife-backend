from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import SyncStatus


class SurveySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    projectId: str
    wardId: str
    leadObserver: str
    teamMembers: list[str] = Field(default_factory=list)
    surveyMethod: str | None = "Opportunistic Encounter"
    habitatType: str | None = "Urban Park / Garden"
    targetGroup: str | None = "All Biodiversity"
    startTime: str
    endTime: str | None = None
    weatherNotes: str | None = ""
    createdAt: str
    updatedAt: str
    syncStatus: SyncStatus = SyncStatus.SYNCED
    observationCount: int | None = 0


class CreateSurveySchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    projectId: str = Field(min_length=1)
    wardId: str = Field(min_length=1)
    leadObserver: str = Field(min_length=1)
    teamMembers: list[str] = Field(default_factory=list)
    surveyMethod: str | None = "Opportunistic Encounter"
    habitatType: str | None = "Urban Park / Garden"
    targetGroup: str | None = "All Biodiversity"
    startTime: str | None = None
    endTime: str | None = None
    weatherNotes: str | None = ""
    syncStatus: SyncStatus | None = SyncStatus.SYNCED

    @model_validator(mode="after")
    def populate_start_time(self) -> CreateSurveySchema:
        if not self.startTime:
            from datetime import UTC, datetime

            self.startTime = datetime.now(UTC).isoformat()
        return self


class UpdateSurveySchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    leadObserver: str | None = None
    teamMembers: list[str] | None = None
    surveyMethod: str | None = None
    habitatType: str | None = None
    targetGroup: str | None = None
    startTime: str | None = None
    endTime: str | None = None
    weatherNotes: str | None = None
    syncStatus: SyncStatus | None = None
