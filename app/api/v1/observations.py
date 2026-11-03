from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, Request, status

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import EntityNotFoundException
from app.core.security import generate_uuid
from app.models.observation import BLiffeObservation
from app.repositories.observation_repo import ObservationRepository
from app.schemas.observation import (
    CreateObservationSchema,
    ObservationSchema,
    UpdateObservationSchema,
)
from app.services.s3_service import S3StorageService
from app.services.sync_service import SyncService

router = APIRouter(tags=["Observations"])


def map_observation(obs: BLiffeObservation) -> dict[str, Any]:
    return {
        "id": obs.id,
        "surveyId": obs.surveyId,
        "wardId": obs.wardId,
        "wardName": obs.wardName,
        "projectId": obs.projectId,
        "projectIds": obs.projectIds or [],
        "speciesName": obs.speciesName,
        "scientificName": obs.scientificName or "",
        "localName": obs.localName or "",
        "speciesGroup": obs.speciesGroup or "",
        "speciesGroups": obs.speciesGroups or "",
        "otherSpeciesGroup": obs.otherSpeciesGroup or "",
        "identificationStatus": obs.identificationStatus or "Identified",
        "organismStatus": obs.organismStatus or "Wild",
        "locationVisibility": obs.locationVisibility or "Open",
        "basis_of_record": obs.basis_of_record or "HumanObservation",
        "tags": obs.tags or [],
        "notes": obs.notes or "",
        "individualCount": obs.individualCount,
        "lifeStage": obs.lifeStage or "",
        "microHabitat": obs.microHabitat or "",
        "otherMicroHabitat": obs.otherMicroHabitat or "",
        "hasTraditionalKnowledge": obs.hasTraditionalKnowledge or "No",
        "traditionalKnowledgeSource": obs.traditionalKnowledgeSource or "",
        "otherTraditionalKnowledgeSource": obs.otherTraditionalKnowledgeSource or "",
        "gps_latitude": obs.gps_latitude,
        "gps_longitude": obs.gps_longitude,
        "latitude": obs.latitude,
        "longitude": obs.longitude,
        "location_source": obs.location_source or "GPS",
        "accuracyMeters": obs.accuracyMeters,
        "observationAt": obs.observationAt,
        "recordedAt": obs.recordedAt,
        "photos": obs.photos or [],
        "verificationStatus": obs.verificationStatus or "Unreviewed",
        "verifiedBy": obs.verifiedBy or "",
        "verificationNotes": obs.verificationNotes or "",
        "syncStatus": obs.syncStatus or "synced",
        "userId": obs.userId,
        "createdAt": obs.createdAt.isoformat() if obs.createdAt else None,
        "updatedAt": obs.updatedAt.isoformat() if obs.updatedAt else None,
    }


@router.get("", response_model=list[ObservationSchema])
@router.get("/", response_model=list[ObservationSchema], include_in_schema=False)
async def list_observations(
    session: SessionDep,
    projectId: str | None = None,
    wardId: str | None = None,
    surveyId: str | None = None,
    status: str | None = None,
    identificationStatus: str | None = None,
    organismStatus: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    q: str | None = None,
    limit: int = Query(default=100, le=200),
    offset: int = 0,
) -> list[dict[str, Any]]:
    repo = ObservationRepository(session)
    search_term = search or q
    observations = await repo.list_observations(
        project_id=projectId,
        ward_id=wardId,
        survey_id=surveyId,
        status=status,
        identification_status=identificationStatus,
        organism_status=organismStatus,
        tag=tag,
        search=search_term,
        limit=limit,
        offset=offset,
    )
    return [map_observation(o) for o in observations]


@router.post("", response_model=ObservationSchema, status_code=status.HTTP_201_CREATED)
@router.post(
    "/",
    response_model=ObservationSchema,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
async def create_observation(
    input_data: CreateObservationSchema,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> dict[str, Any]:
    sync_service = SyncService(session)
    raw_user_id = current_user.user_id or input_data.userId

    rels = await sync_service.ensure_relational_entities(
        project_id=input_data.projectId,
        ward_id=input_data.wardId,
        ward_name=input_data.wardName,
        survey_id=input_data.surveyId,
        user_id=raw_user_id,
        observation_at=input_data.observationAt,
    )

    obs_id = input_data.id or generate_uuid()
    raw_photos = input_data.photos or ([input_data.photo] if input_data.photo else [])
    s3_service = S3StorageService()
    photos = s3_service.upload_batch_base64_if_needed(raw_photos, folder="observations")
    project_ids = input_data.projectIds or ([rels["projectId"]] if rels["projectId"] else [])
    now_iso = datetime.now(UTC).isoformat()

    obs = BLiffeObservation(
        id=obs_id,
        surveyId=rels["surveyId"],
        wardId=rels["wardId"],
        wardName=input_data.wardName,
        projectId=rels["projectId"],
        projectIds=project_ids,
        speciesName=input_data.speciesName.strip(),
        scientificName=input_data.scientificName.strip() if input_data.scientificName else "",
        localName=input_data.localName.strip() if input_data.localName else "",
        speciesGroup=input_data.speciesGroup.strip() if input_data.speciesGroup else "",
        speciesGroups=input_data.speciesGroups.strip() if input_data.speciesGroups else "",
        otherSpeciesGroup=input_data.otherSpeciesGroup.strip()
        if input_data.otherSpeciesGroup
        else "",
        identificationStatus=input_data.identificationStatus or "Identified",
        organismStatus=input_data.organismStatus or "Wild",
        locationVisibility=input_data.locationVisibility or "Open",
        basis_of_record=input_data.basis_of_record or "HumanObservation",
        tags=input_data.tags or [],
        notes=input_data.notes.strip() if input_data.notes else "",
        individualCount=input_data.individualCount or 1,
        lifeStage=input_data.lifeStage.strip() if input_data.lifeStage else "",
        microHabitat=input_data.microHabitat.strip() if input_data.microHabitat else "",
        otherMicroHabitat=input_data.otherMicroHabitat.strip()
        if input_data.otherMicroHabitat
        else "",
        hasTraditionalKnowledge=input_data.hasTraditionalKnowledge or "No",
        traditionalKnowledgeSource=input_data.traditionalKnowledgeSource.strip()
        if input_data.traditionalKnowledgeSource
        else "",
        otherTraditionalKnowledgeSource=input_data.otherTraditionalKnowledgeSource.strip()
        if input_data.otherTraditionalKnowledgeSource
        else "",
        gps_latitude=input_data.gps_latitude,
        gps_longitude=input_data.gps_longitude,
        latitude=input_data.latitude,
        longitude=input_data.longitude,
        location_source=input_data.location_source or "GPS",
        accuracyMeters=input_data.accuracyMeters,
        observationAt=input_data.observationAt or now_iso,
        recordedAt=input_data.recordedAt or now_iso,
        photos=photos,
        verificationStatus=input_data.verificationStatus or "Unreviewed",
        verifiedBy=input_data.verifiedBy.strip() if input_data.verifiedBy else "",
        verificationNotes=input_data.verificationNotes.strip()
        if input_data.verificationNotes
        else "",
        syncStatus=input_data.syncStatus or "synced",
        userId=rels["userId"],
    )

    session.add(obs)
    await session.commit()
    await session.refresh(obs)
    return map_observation(obs)


@router.get("/{id}", response_model=ObservationSchema)
async def get_observation(id: str, session: SessionDep) -> dict[str, Any]:
    repo = ObservationRepository(session)
    obs = await repo.get_by_id(id)
    if not obs:
        raise EntityNotFoundException("Observation not found")
    return map_observation(obs)


@router.put("/{id}", response_model=ObservationSchema)
async def update_observation(
    id: str, input_data: UpdateObservationSchema, session: SessionDep
) -> dict[str, Any]:
    repo = ObservationRepository(session)
    obs = await repo.get_by_id(id)
    if not obs:
        raise EntityNotFoundException("Observation not found")

    if input_data.speciesName is not None:
        obs.speciesName = input_data.speciesName.strip()
    if input_data.scientificName is not None:
        obs.scientificName = input_data.scientificName.strip()
    if input_data.localName is not None:
        obs.localName = input_data.localName.strip()
    if input_data.speciesGroup is not None:
        obs.speciesGroup = input_data.speciesGroup.strip()
    if input_data.speciesGroups is not None:
        obs.speciesGroups = input_data.speciesGroups.strip()
    if input_data.otherSpeciesGroup is not None:
        obs.otherSpeciesGroup = input_data.otherSpeciesGroup.strip()
    if input_data.identificationStatus is not None:
        obs.identificationStatus = input_data.identificationStatus
    if input_data.organismStatus is not None:
        obs.organismStatus = input_data.organismStatus
    if input_data.locationVisibility is not None:
        obs.locationVisibility = input_data.locationVisibility
    if input_data.basis_of_record is not None:
        obs.basis_of_record = input_data.basis_of_record
    if input_data.tags is not None:
        obs.tags = input_data.tags
    if input_data.notes is not None:
        obs.notes = input_data.notes.strip()
    if input_data.individualCount is not None:
        obs.individualCount = input_data.individualCount
    if input_data.lifeStage is not None:
        obs.lifeStage = input_data.lifeStage.strip()
    if input_data.microHabitat is not None:
        obs.microHabitat = input_data.microHabitat.strip()
    if input_data.otherMicroHabitat is not None:
        obs.otherMicroHabitat = input_data.otherMicroHabitat.strip()
    if input_data.hasTraditionalKnowledge is not None:
        obs.hasTraditionalKnowledge = input_data.hasTraditionalKnowledge
    if input_data.traditionalKnowledgeSource is not None:
        obs.traditionalKnowledgeSource = input_data.traditionalKnowledgeSource.strip()
    if input_data.otherTraditionalKnowledgeSource is not None:
        obs.otherTraditionalKnowledgeSource = input_data.otherTraditionalKnowledgeSource.strip()
    if input_data.gps_latitude is not None:
        obs.gps_latitude = input_data.gps_latitude
    if input_data.gps_longitude is not None:
        obs.gps_longitude = input_data.gps_longitude
    if input_data.latitude is not None:
        obs.latitude = input_data.latitude
    if input_data.longitude is not None:
        obs.longitude = input_data.longitude
    if input_data.location_source is not None:
        obs.location_source = input_data.location_source
    if input_data.accuracyMeters is not None:
        obs.accuracyMeters = input_data.accuracyMeters
    if input_data.photos is not None:
        s3_service = S3StorageService()
        obs.photos = s3_service.upload_batch_base64_if_needed(
            input_data.photos, folder="observations"
        )
    elif input_data.photo is not None:
        s3_service = S3StorageService()
        obs.photos = s3_service.upload_batch_base64_if_needed(
            [input_data.photo], folder="observations"
        )
    if input_data.verificationStatus is not None:
        obs.verificationStatus = input_data.verificationStatus
    if input_data.verifiedBy is not None:
        obs.verifiedBy = input_data.verifiedBy.strip()
    if input_data.verificationNotes is not None:
        obs.verificationNotes = input_data.verificationNotes.strip()
    if input_data.syncStatus is not None:
        obs.syncStatus = input_data.syncStatus
    if input_data.projectId is not None:
        obs.projectId = input_data.projectId
    if input_data.projectIds is not None:
        obs.projectIds = input_data.projectIds
    if input_data.wardId is not None:
        obs.wardId = input_data.wardId
    if input_data.wardName is not None:
        obs.wardName = input_data.wardName
    if input_data.surveyId is not None:
        obs.surveyId = input_data.surveyId

    await session.commit()
    await session.refresh(obs)
    return map_observation(obs)


@router.delete("/{id}")
async def delete_observation(id: str, session: SessionDep) -> dict[str, Any]:
    repo = ObservationRepository(session)
    obs = await repo.get_by_id(id)
    if not obs:
        raise EntityNotFoundException("Observation not found")
    await repo.delete(obs)
    await session.commit()
    return {"success": True, "message": "Observation deleted successfully"}


@router.post("/batch")
async def batch_upsert_observations(request: Request, session: SessionDep) -> dict[str, Any]:
    raw_body = await request.json()
    items = raw_body if isinstance(raw_body, list) else raw_body.get("observations", [])
    sync_service = SyncService(session)
    count = 0

    for raw in items:
        parsed = CreateObservationSchema.model_validate(raw)
        oid = parsed.id or generate_uuid()
        rels = await sync_service.ensure_relational_entities(
            project_id=parsed.projectId,
            ward_id=parsed.wardId,
            ward_name=parsed.wardName,
            survey_id=parsed.surveyId,
            user_id=parsed.userId,
            observation_at=parsed.observationAt,
        )

        s3_service = S3StorageService()
        raw_photos = parsed.photos or ([parsed.photo] if parsed.photo else [])
        clean_photos = s3_service.upload_batch_base64_if_needed(raw_photos, folder="observations")

        existing = await session.get(BLiffeObservation, oid)
        if existing:
            existing.speciesName = parsed.speciesName.strip()
            existing.scientificName = parsed.scientificName.strip() if parsed.scientificName else ""
            existing.localName = parsed.localName.strip() if parsed.localName else ""
            existing.speciesGroup = parsed.speciesGroup.strip() if parsed.speciesGroup else ""
            existing.notes = parsed.notes.strip() if parsed.notes else ""
            existing.tags = parsed.tags or []
            existing.latitude = parsed.latitude
            existing.longitude = parsed.longitude
            if clean_photos:
                existing.photos = clean_photos
            existing.syncStatus = "synced"
        else:
            now_iso = datetime.now(UTC).isoformat()
            new_obs = BLiffeObservation(
                id=oid,
                surveyId=rels["surveyId"],
                wardId=rels["wardId"],
                wardName=parsed.wardName,
                projectId=rels["projectId"],
                projectIds=parsed.projectIds or ([rels["projectId"]] if rels["projectId"] else []),
                speciesName=parsed.speciesName.strip(),
                scientificName=parsed.scientificName.strip() if parsed.scientificName else "",
                localName=parsed.localName.strip() if parsed.localName else "",
                speciesGroup=parsed.speciesGroup.strip() if parsed.speciesGroup else "",
                speciesGroups=parsed.speciesGroups.strip() if parsed.speciesGroups else "",
                otherSpeciesGroup=parsed.otherSpeciesGroup.strip()
                if parsed.otherSpeciesGroup
                else "",
                identificationStatus=parsed.identificationStatus or "Identified",
                organismStatus=parsed.organismStatus or "Wild",
                locationVisibility=parsed.locationVisibility or "Open",
                basis_of_record=parsed.basis_of_record or "HumanObservation",
                tags=parsed.tags or [],
                notes=parsed.notes.strip() if parsed.notes else "",
                individualCount=parsed.individualCount or 1,
                lifeStage=parsed.lifeStage.strip() if parsed.lifeStage else "",
                microHabitat=parsed.microHabitat.strip() if parsed.microHabitat else "",
                otherMicroHabitat=parsed.otherMicroHabitat.strip()
                if parsed.otherMicroHabitat
                else "",
                hasTraditionalKnowledge=parsed.hasTraditionalKnowledge or "No",
                traditionalKnowledgeSource=parsed.traditionalKnowledgeSource.strip()
                if parsed.traditionalKnowledgeSource
                else "",
                otherTraditionalKnowledgeSource=parsed.otherTraditionalKnowledgeSource.strip()
                if parsed.otherTraditionalKnowledgeSource
                else "",
                gps_latitude=parsed.gps_latitude,
                gps_longitude=parsed.gps_longitude,
                latitude=parsed.latitude,
                longitude=parsed.longitude,
                location_source=parsed.location_source or "GPS",
                accuracyMeters=parsed.accuracyMeters,
                observationAt=parsed.observationAt or now_iso,
                recordedAt=parsed.recordedAt or now_iso,
                photos=clean_photos,
                verificationStatus=parsed.verificationStatus or "Unreviewed",
                verifiedBy=parsed.verifiedBy.strip() if parsed.verifiedBy else "",
                verificationNotes=parsed.verificationNotes.strip()
                if parsed.verificationNotes
                else "",
                syncStatus="synced",
            )
            session.add(new_obs)
        count += 1

    await session.commit()
    return {"success": True, "count": count}
