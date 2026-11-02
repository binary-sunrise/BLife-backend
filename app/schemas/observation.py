from __future__ import annotations

from datetime import UTC

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ObservationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    surveyId: str | None = None
    wardId: str | None = None
    wardName: str | None = None
    projectId: str | None = None
    projectIds: list[str] = Field(default_factory=list)

    speciesName: str = Field(min_length=1)
    scientificName: str | None = ""
    localName: str | None = ""
    speciesGroup: str | None = ""
    speciesGroups: str | None = ""
    otherSpeciesGroup: str | None = ""
    identificationStatus: str | None = "Identified"
    organismStatus: str | None = "Wild"
    locationVisibility: str | None = "Open"
    basis_of_record: str = "HumanObservation"
    tags: list[str] = Field(default_factory=list)
    notes: str = ""

    individualCount: int = 1
    lifeStage: str | None = ""
    microHabitat: str | None = ""
    otherMicroHabitat: str | None = ""

    hasTraditionalKnowledge: str | None = "No"
    traditionalKnowledgeSource: str | None = ""
    otherTraditionalKnowledgeSource: str | None = ""

    gps_latitude: float | None = None
    gps_longitude: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_source: str | None = "GPS"
    accuracyMeters: float | None = None

    observationAt: str
    recordedAt: str

    photos: list[str] = Field(default_factory=list)

    verificationStatus: str | None = "Unreviewed"
    verifiedBy: str | None = ""
    verificationNotes: str | None = ""

    syncStatus: str = "synced"
    userId: str | None = None
    createdAt: str | None = None
    updatedAt: str | None = None


class CreateObservationSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    surveyId: str | None = None
    wardId: str | None = None
    wardName: str | None = None
    projectId: str | None = None
    projectIds: list[str] = Field(default_factory=list)

    speciesName: str = Field(min_length=1)
    scientificName: str | None = ""
    localName: str | None = ""
    speciesGroup: str | None = ""
    speciesGroups: str | None = ""
    otherSpeciesGroup: str | None = ""
    identificationStatus: str | None = "Identified"
    organismStatus: str | None = "Wild"
    locationVisibility: str | None = "Open"
    basis_of_record: str = "HumanObservation"
    tags: list[str] = Field(default_factory=list)
    notes: str = ""

    individualCount: int = 1
    lifeStage: str | None = ""
    microHabitat: str | None = ""
    otherMicroHabitat: str | None = ""

    hasTraditionalKnowledge: str | None = "No"
    traditionalKnowledgeSource: str | None = ""
    otherTraditionalKnowledgeSource: str | None = ""

    gps_latitude: float | None = None
    gps_longitude: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_source: str | None = "GPS"
    accuracyMeters: float | None = None

    observationAt: str | None = None
    recordedAt: str | None = None

    photos: list[str] = Field(default_factory=list)
    photo: str | None = None

    verificationStatus: str | None = "Unreviewed"
    verifiedBy: str | None = ""
    verificationNotes: str | None = ""

    syncStatus: str | None = "synced"
    userId: str | None = None

    @model_validator(mode="after")
    def populate_photos_and_dates(self) -> CreateObservationSchema:
        if self.photo and not self.photos:
            self.photos = [self.photo]
        from datetime import datetime

        now_iso = datetime.now(UTC).isoformat()
        if not self.observationAt:
            self.observationAt = now_iso
        if not self.recordedAt:
            self.recordedAt = now_iso
        return self


class UpdateObservationSchema(BaseModel):
    surveyId: str | None = None
    wardId: str | None = None
    wardName: str | None = None
    projectId: str | None = None
    projectIds: list[str] | None = None
    speciesName: str | None = None
    scientificName: str | None = None
    localName: str | None = None
    speciesGroup: str | None = None
    speciesGroups: str | None = None
    otherSpeciesGroup: str | None = None
    identificationStatus: str | None = None
    organismStatus: str | None = None
    locationVisibility: str | None = None
    basis_of_record: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    individualCount: int | None = None
    lifeStage: str | None = None
    microHabitat: str | None = None
    otherMicroHabitat: str | None = None
    hasTraditionalKnowledge: str | None = None
    traditionalKnowledgeSource: str | None = None
    otherTraditionalKnowledgeSource: str | None = None
    gps_latitude: float | None = None
    gps_longitude: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    location_source: str | None = None
    accuracyMeters: float | None = None
    observationAt: str | None = None
    recordedAt: str | None = None
    photos: list[str] | None = None
    photo: str | None = None
    verificationStatus: str | None = None
    verifiedBy: str | None = None
    verificationNotes: str | None = None
    syncStatus: str | None = None


class ObservationQuerySchema(BaseModel):
    projectId: str | None = None
    wardId: str | None = None
    surveyId: str | None = None
    status: str | None = None
    identificationStatus: str | None = None
    organismStatus: str | None = None
    tag: str | None = None
    q: str | None = None
    search: str | None = None
    limit: int = 100
    offset: int = 0
