from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.observation import BLiffeObservation
    from app.models.project import BLiffeProject
    from app.models.survey import BLiffeSurvey


class BLiffeWard(Base, TimestampMixin):
    __tablename__ = "bliffe_wards"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    projectId: Mapped[str] = mapped_column(
        String, ForeignKey("bliffe_projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    wardNumber: Mapped[str] = mapped_column(String, nullable=False)
    wardName: Mapped[str] = mapped_column(String, nullable=False)
    localBodyName: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    district: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    state: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    keyLandmarks: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    syncStatus: Mapped[str] = mapped_column(String, default="synced", nullable=False)

    project: Mapped[BLiffeProject] = relationship("BLiffeProject", back_populates="wards")
    surveys: Mapped[list[BLiffeSurvey]] = relationship(
        "BLiffeSurvey", back_populates="ward", cascade="all, delete-orphan"
    )
    observations: Mapped[list[BLiffeObservation]] = relationship(
        "BLiffeObservation", back_populates="ward"
    )
