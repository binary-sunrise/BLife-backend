from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.observation import BLiffeObservation
    from app.models.survey import BLiffeSurvey
    from app.models.ward import BLiffeWard


class BLiffeProject(Base, TimestampMixin):
    __tablename__ = "bliffe_projects"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    startDate: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)
    organization: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    targetRegion: Mapped[str | None] = mapped_column(String, default="", nullable=True)
    syncStatus: Mapped[str] = mapped_column(String, default="synced", nullable=False)

    wards: Mapped[list[BLiffeWard]] = relationship(
        "BLiffeWard", back_populates="project", cascade="all, delete-orphan"
    )
    surveys: Mapped[list[BLiffeSurvey]] = relationship(
        "BLiffeSurvey", back_populates="project", cascade="all, delete-orphan"
    )
    observations: Mapped[list[BLiffeObservation]] = relationship(
        "BLiffeObservation", back_populates="project"
    )
