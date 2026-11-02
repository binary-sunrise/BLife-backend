from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.api.v1.observations import map_observation
from app.repositories.observation_repo import ObservationRepository
from app.schemas.export import DwCExportResponseSchema
from app.services.dwc_service import export_observations_as_dwc

router = APIRouter(tags=["Export"])


@router.get("/dwc", response_model=DwCExportResponseSchema)
async def export_dwc(
    session: SessionDep,
    projectId: str | None = None,
    wardId: str | None = None,
    surveyId: str | None = None,
) -> dict[str, Any]:
    repo = ObservationRepository(session)
    observations = await repo.list_observations(
        project_id=projectId,
        ward_id=wardId,
        survey_id=surveyId,
        limit=1000,
    )
    mapped = [map_observation(o) for o in observations]
    return export_observations_as_dwc(mapped)
