from __future__ import annotations

import re
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_uuid
from app.models.observation import BLiffeObservation
from app.models.project import BLiffeProject
from app.models.survey import BLiffeSurvey
from app.models.user import User
from app.models.ward import BLiffeWard
from app.schemas.sync import (
    SyncPayloadSchema,
    SyncResponseSchema,
    SyncStatusResponseSchema,
    SyncSyncedCounts,
)
from app.services.s3_service import S3StorageService
from app.services.ward_service import TVM_WARDS


class SyncService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def ensure_relational_entities(
        self,
        project_id: str | None,
        ward_id: str | None,
        ward_name: str | None,
        survey_id: str | None,
        user_id: str | None,
        observation_at: str | None,
    ) -> dict[str, str | None]:
        effective_project_id = project_id or None
        if effective_project_id:
            proj = await self.session.get(BLiffeProject, effective_project_id)
            if not proj:
                proj = BLiffeProject(
                    id=effective_project_id,
                    name="Biodiversity Field Project",
                    targetRegion="Thiruvananthapuram",
                    status="active",
                    syncStatus="synced",
                )
                self.session.add(proj)
                await self.session.flush()

        effective_ward_id = ward_id or None
        if effective_ward_id:
            ward = await self.session.get(BLiffeWard, effective_ward_id)
            if not ward:
                project_for_ward = effective_project_id
                if not project_for_ward:
                    res = await self.session.execute(select(BLiffeProject).limit(1))
                    default_proj = res.scalars().first()
                    if not default_proj:
                        default_proj = BLiffeProject(
                            id="proj-tvm-biodiversity-2026",
                            name="Thiruvananthapuram City Biodiversity Register",
                            organization="Kerala State Biodiversity Board",
                            targetRegion="Thiruvananthapuram Municipal Corporation",
                            status="active",
                            syncStatus="synced",
                        )
                        self.session.add(default_proj)
                        await self.session.flush()
                    project_for_ward = default_proj.id
                    effective_project_id = default_proj.id

                matched_ref = next((w for w in TVM_WARDS if w.ward_id == effective_ward_id), None)
                ward_num_match = re.search(r"\d+", ward_name or "")
                ward_num = (
                    matched_ref.ward_number
                    if matched_ref
                    else (ward_num_match.group(0) if ward_num_match else "14")
                )
                w_name = matched_ref.ward_name if matched_ref else (ward_name or "Palayam")
                local_body = (
                    matched_ref.local_body_name
                    if matched_ref
                    else "Thiruvananthapuram Municipal Corporation"
                )

                ward = BLiffeWard(
                    id=effective_ward_id,
                    projectId=project_for_ward,
                    wardNumber=ward_num,
                    wardName=w_name,
                    localBodyName=local_body,
                    district="Thiruvananthapuram",
                    state="Kerala",
                    syncStatus="synced",
                )
                self.session.add(ward)
                await self.session.flush()

        effective_survey_id = survey_id or None
        if effective_survey_id:
            survey = await self.session.get(BLiffeSurvey, effective_survey_id)
            if not survey:
                if effective_project_id and effective_ward_id:
                    survey = BLiffeSurvey(
                        id=effective_survey_id,
                        projectId=effective_project_id,
                        wardId=effective_ward_id,
                        leadObserver="Field Researcher",
                        startTime=observation_at or datetime.now(UTC).isoformat(),
                        syncStatus="synced",
                    )
                    self.session.add(survey)
                    await self.session.flush()
                else:
                    effective_survey_id = None

        effective_user_id = user_id or None
        if effective_user_id:
            user = await self.session.get(User, effective_user_id)
            if not user:
                effective_user_id = None

        return {
            "projectId": effective_project_id,
            "wardId": effective_ward_id,
            "surveyId": effective_survey_id,
            "userId": effective_user_id,
        }

    async def sync_all(self, payload: SyncPayloadSchema) -> SyncResponseSchema:
        synced_projects = 0
        synced_wards = 0
        synced_surveys = 0
        synced_observations = 0

        # 1. Sync Projects
        for p in payload.projects:
            pid = p.id or generate_uuid()
            existing_p = await self.session.get(BLiffeProject, pid)
            if existing_p:
                existing_p.name = p.name.strip()
                existing_p.description = p.description.strip() if p.description else ""
                existing_p.status = p.status.value if p.status else "active"
                existing_p.organization = p.organization.strip() if p.organization else ""
                existing_p.targetRegion = p.targetRegion.strip() if p.targetRegion else ""
                existing_p.syncStatus = "synced"
            else:
                new_p = BLiffeProject(
                    id=pid,
                    name=p.name.strip(),
                    description=p.description.strip() if p.description else "",
                    startDate=p.startDate,
                    status=p.status.value if p.status else "active",
                    organization=p.organization.strip() if p.organization else "",
                    targetRegion=p.targetRegion.strip() if p.targetRegion else "",
                    syncStatus="synced",
                )
                self.session.add(new_p)
            synced_projects += 1
        await self.session.flush()

        # 2. Sync Wards
        for w in payload.wards:
            wid = w.id or generate_uuid()
            # Ensure project exists
            proj = await self.session.get(BLiffeProject, w.projectId)
            if not proj:
                proj = BLiffeProject(
                    id=w.projectId,
                    name="Synced Field Project",
                    status="active",
                    syncStatus="synced",
                )
                self.session.add(proj)
                await self.session.flush()

            existing_w = await self.session.get(BLiffeWard, wid)
            if existing_w:
                existing_w.wardNumber = w.wardNumber.strip()
                existing_w.wardName = w.wardName.strip()
                existing_w.localBodyName = w.localBodyName.strip() if w.localBodyName else ""
                existing_w.district = w.district.strip() if w.district else ""
                existing_w.state = w.state.strip() if w.state else ""
                existing_w.keyLandmarks = w.keyLandmarks.strip() if w.keyLandmarks else ""
                existing_w.syncStatus = "synced"
            else:
                new_w = BLiffeWard(
                    id=wid,
                    projectId=w.projectId,
                    wardNumber=w.wardNumber.strip(),
                    wardName=w.wardName.strip(),
                    localBodyName=w.localBodyName.strip() if w.localBodyName else "",
                    district=w.district.strip() if w.district else "",
                    state=w.state.strip() if w.state else "",
                    keyLandmarks=w.keyLandmarks.strip() if w.keyLandmarks else "",
                    syncStatus="synced",
                )
                self.session.add(new_w)
            synced_wards += 1
        await self.session.flush()

        # 3. Sync Surveys
        for s in payload.surveys:
            sid = s.id or generate_uuid()
            # Ensure project and ward exist
            proj = await self.session.get(BLiffeProject, s.projectId)
            if not proj:
                proj = BLiffeProject(id=s.projectId, name="Synced Project", syncStatus="synced")
                self.session.add(proj)
                await self.session.flush()

            ward = await self.session.get(BLiffeWard, s.wardId)
            if not ward:
                ward = BLiffeWard(
                    id=s.wardId,
                    projectId=s.projectId,
                    wardNumber="14",
                    wardName="Palayam",
                    syncStatus="synced",
                )
                self.session.add(ward)
                await self.session.flush()

            existing_s = await self.session.get(BLiffeSurvey, sid)
            if existing_s:
                existing_s.leadObserver = s.leadObserver.strip()
                existing_s.teamMembers = s.teamMembers
                existing_s.surveyMethod = s.surveyMethod
                existing_s.habitatType = s.habitatType
                existing_s.targetGroup = s.targetGroup
                existing_s.startTime = s.startTime
                existing_s.endTime = s.endTime
                existing_s.weatherNotes = s.weatherNotes or ""
                existing_s.syncStatus = "synced"
            else:
                new_s = BLiffeSurvey(
                    id=sid,
                    projectId=s.projectId,
                    wardId=s.wardId,
                    leadObserver=s.leadObserver.strip(),
                    teamMembers=s.teamMembers,
                    surveyMethod=s.surveyMethod or "Opportunistic Encounter",
                    habitatType=s.habitatType or "Urban Park / Garden",
                    targetGroup=s.targetGroup or "All Biodiversity",
                    startTime=s.startTime,
                    endTime=s.endTime,
                    weatherNotes=s.weatherNotes.strip() if s.weatherNotes else "",
                    syncStatus="synced",
                )
                self.session.add(new_s)
            synced_surveys += 1
        await self.session.flush()

        # 4. Sync Observations
        for o in payload.observations:
            oid = o.id or generate_uuid()
            rels = await self.ensure_relational_entities(
                project_id=o.projectId,
                ward_id=o.wardId,
                ward_name=o.wardName,
                survey_id=o.surveyId,
                user_id=o.userId,
                observation_at=o.observationAt,
            )

            s3_service = S3StorageService()
            raw_photos = o.photos or ([o.photo] if o.photo else [])
            clean_photos = s3_service.upload_batch_base64_if_needed(raw_photos, folder="observations")

            existing_o = await self.session.get(BLiffeObservation, oid)
            if existing_o:
                existing_o.speciesName = o.speciesName.strip()
                existing_o.scientificName = o.scientificName.strip() if o.scientificName else ""
                existing_o.localName = o.localName.strip() if o.localName else ""
                existing_o.speciesGroup = o.speciesGroup.strip() if o.speciesGroup else ""
                existing_o.notes = o.notes.strip() if o.notes else ""
                existing_o.tags = o.tags
                existing_o.latitude = o.latitude
                existing_o.longitude = o.longitude
                if clean_photos:
                    existing_o.photos = clean_photos
                existing_o.syncStatus = "synced"
            else:
                now_iso = datetime.now(UTC).isoformat()
                new_o = BLiffeObservation(
                    id=oid,
                    surveyId=rels["surveyId"],
                    wardId=rels["wardId"],
                    wardName=o.wardName,
                    projectId=rels["projectId"],
                    projectIds=o.projectIds or ([rels["projectId"]] if rels["projectId"] else []),
                    speciesName=o.speciesName.strip(),
                    scientificName=o.scientificName.strip() if o.scientificName else "",
                    localName=o.localName.strip() if o.localName else "",
                    speciesGroup=o.speciesGroup.strip() if o.speciesGroup else "",
                    speciesGroups=o.speciesGroups.strip() if o.speciesGroups else "",
                    otherSpeciesGroup=o.otherSpeciesGroup.strip() if o.otherSpeciesGroup else "",
                    identificationStatus=o.identificationStatus or "Identified",
                    organismStatus=o.organismStatus or "Wild",
                    locationVisibility=o.locationVisibility or "Open",
                    basis_of_record=o.basis_of_record or "HumanObservation",
                    tags=o.tags or [],
                    notes=o.notes.strip() if o.notes else "",
                    individualCount=o.individualCount or 1,
                    lifeStage=o.lifeStage.strip() if o.lifeStage else "",
                    microHabitat=o.microHabitat.strip() if o.microHabitat else "",
                    otherMicroHabitat=o.otherMicroHabitat.strip() if o.otherMicroHabitat else "",
                    hasTraditionalKnowledge=o.hasTraditionalKnowledge or "No",
                    traditionalKnowledgeSource=o.traditionalKnowledgeSource.strip()
                    if o.traditionalKnowledgeSource
                    else "",
                    otherTraditionalKnowledgeSource=o.otherTraditionalKnowledgeSource.strip()
                    if o.otherTraditionalKnowledgeSource
                    else "",
                    gps_latitude=o.gps_latitude,
                    gps_longitude=o.gps_longitude,
                    latitude=o.latitude,
                    longitude=o.longitude,
                    location_source=o.location_source or "GPS",
                    accuracyMeters=o.accuracyMeters,
                    observationAt=o.observationAt or now_iso,
                    recordedAt=o.recordedAt or now_iso,
                    photos=clean_photos,
                    verificationStatus=o.verificationStatus or "Unreviewed",
                    verifiedBy=o.verifiedBy.strip() if o.verifiedBy else "",
                    verificationNotes=o.verificationNotes.strip() if o.verificationNotes else "",
                    syncStatus="synced",
                    userId=rels["userId"],
                )
                self.session.add(new_o)
            synced_observations += 1

        await self.session.commit()

        return SyncResponseSchema(
            success=True,
            timestamp=datetime.now(UTC).isoformat(),
            synced=SyncSyncedCounts(
                projects=synced_projects,
                wards=synced_wards,
                surveys=synced_surveys,
                observations=synced_observations,
            ),
        )

    async def get_status(self) -> SyncStatusResponseSchema:
        p_count = await self.session.scalar(select(func.count(BLiffeProject.id))) or 0
        w_count = await self.session.scalar(select(func.count(BLiffeWard.id))) or 0
        s_count = await self.session.scalar(select(func.count(BLiffeSurvey.id))) or 0
        o_count = await self.session.scalar(select(func.count(BLiffeObservation.id))) or 0

        return SyncStatusResponseSchema(
            status="online",
            timestamp=datetime.now(UTC).isoformat(),
            counts=SyncSyncedCounts(
                projects=p_count,
                wards=w_count,
                surveys=s_count,
                observations=o_count,
            ),
        )
