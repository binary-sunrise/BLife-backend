from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.export import router as export_router
from app.api.v1.observations import router as observations_router
from app.api.v1.profile import router as profile_router
from app.api.v1.projects import router as projects_router
from app.api.v1.surveys import router as surveys_router
from app.api.v1.sync import router as sync_router
from app.api.v1.wards import router as wards_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth")
api_v1_router.include_router(profile_router, prefix="/profile")
api_v1_router.include_router(profile_router, prefix="/v1/profile")
api_v1_router.include_router(projects_router, prefix="/projects")
api_v1_router.include_router(wards_router, prefix="/wards")
api_v1_router.include_router(surveys_router, prefix="/surveys")
api_v1_router.include_router(observations_router, prefix="/observations")
api_v1_router.include_router(sync_router, prefix="/sync")
api_v1_router.include_router(export_router, prefix="/export")

# Hierarchical route aliases matching B-Liffe frontend navigation URLs
api_v1_router.include_router(
    surveys_router, prefix="/projects/{project_id}/wards/{ward_id}/surveys"
)
