from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.observation import BLiffeObservation
    from app.models.project import BLiffeProject
    from app.models.ward import BLiffeWard


class BLiffeSurvey(Base, TimestampMixin):
    __tablename__ = "bliffe_surveys"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    projectId: Mapped[str] = mapped_column(
        String, ForeignKey("bliffe_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    wardId: Mapped[str] = mapped_column(
        String, ForeignKey("bliffe_wards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    leadObserver: Mapped[str] = mapped_column(String, nullable=False)
    teamMembers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    surveyMethod: Mapped[str | None] = mapped_column(
        String, default="Opportunistic Encounter", nullable=True
    )
    habitatType: Mapped[str | None] = mapped_column(
        String, default="Urban Park / Garden", nullable=True
    )
    targetGroup: Mapped[str | None] = mapped_column(
        String, default="All Biodiversity", nullable=True
    )
    startTime: Mapped[str] = mapped_column(String, nullable=False)
    endTime: Mapped[str | None] = mapped_column(String, nullable=True)
    weatherNotes: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    syncStatus: Mapped[str] = mapped_column(String, default="synced", nullable=False)

    project: Mapped[BLiffeProject] = relationship("BLiffeProject", back_populates="surveys")
    ward: Mapped[BLiffeWard] = relationship("BLiffeWard", back_populates="surveys")
    observations: Mapped[list[BLiffeObservation]] = relationship(
        "BLiffeObservation", back_populates="survey"
    )
