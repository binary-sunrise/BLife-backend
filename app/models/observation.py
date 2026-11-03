from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import BLiffeProject
    from app.models.survey import BLiffeSurvey
    from app.models.ward import BLiffeWard


class BLiffeObservation(Base, TimestampMixin):
    __tablename__ = "bliffe_observations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    surveyId: Mapped[str | None] = mapped_column(
        String, ForeignKey("bliffe_surveys.id", ondelete="SET NULL"), nullable=True, index=True
    )
    wardId: Mapped[str | None] = mapped_column(
        String, ForeignKey("bliffe_wards.id", ondelete="SET NULL"), nullable=True, index=True
    )
    wardName: Mapped[str | None] = mapped_column(String, nullable=True)
    projectId: Mapped[str | None] = mapped_column(
        String, ForeignKey("bliffe_projects.id", ondelete="SET NULL"), nullable=True, index=True
    )
    projectIds: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    speciesName: Mapped[str] = mapped_column(String, nullable=False)
    scientificName: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    localName: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    speciesGroup: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    speciesGroups: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    otherSpeciesGroup: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    identificationStatus: Mapped[str | None] = mapped_column(
        String, default="Identified", nullable=True
    )
    organismStatus: Mapped[str | None] = mapped_column(String, default="Wild", nullable=True)
    locationVisibility: Mapped[str | None] = mapped_column(String, default="Open", nullable=True)
    basis_of_record: Mapped[str] = mapped_column(String, default="HumanObservation", nullable=False)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    individualCount: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    lifeStage: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    microHabitat: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    otherMicroHabitat: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    habitatType: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    reproductiveAttributes: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    sex: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    evidenceOfPresence: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    season: Mapped[str | None] = mapped_column(String, default="", nullable=True)

    hasTraditionalKnowledge: Mapped[str | None] = mapped_column(String, default="No", nullable=True)
    traditionalKnowledgeSource: Mapped[str | None] = mapped_column(
        String, default="", nullable=True
    )
    otherTraditionalKnowledgeSource: Mapped[str | None] = mapped_column(
        String, default="", nullable=True
    )

    gps_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_source: Mapped[str | None] = mapped_column(String, default="GPS", nullable=True)
    accuracyMeters: Mapped[float | None] = mapped_column(Float, nullable=True)
    gpsCapturedAt: Mapped[str | None] = mapped_column(String, nullable=True)

    observationAt: Mapped[str] = mapped_column(String, nullable=False)
    recordedAt: Mapped[str] = mapped_column(String, nullable=False)

    photo: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    photos: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    photoMetadata: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"), default=list, nullable=False
    )

    verificationStatus: Mapped[str | None] = mapped_column(
        String, default="Unreviewed", nullable=True
    )
    verifiedBy: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    verificationNotes: Mapped[str | None] = mapped_column(Text, default="", nullable=True)

    syncStatus: Mapped[str] = mapped_column(String, default="synced", nullable=False)
    userId: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    project: Mapped[BLiffeProject | None] = relationship(
        "BLiffeProject", back_populates="observations"
    )
    ward: Mapped[BLiffeWard | None] = relationship("BLiffeWard", back_populates="observations")
    survey: Mapped[BLiffeSurvey | None] = relationship(
        "BLiffeSurvey", back_populates="observations"
    )
