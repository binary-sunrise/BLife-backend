from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.logging import get_logger, setup_logging
from app.core.security import hash_password
from app.db.session import async_session_factory, engine
from app.models.observation import BLiffeObservation
from app.models.project import BLiffeProject
from app.models.survey import BLiffeSurvey
from app.models.user import Account, User, UserProfile
from app.models.ward import BLiffeWard

logger = get_logger(__name__)


async def seed() -> None:
    setup_logging()
    logger.info("seed_pipeline_start")

    async with async_session_factory() as session:
        default_pwd = hash_password("Password123!")

        # 1. Seed Users
        users_data = [
            {
                "id": "user-veena",
                "sub": "mock-user-veena-001",
                "name": "Veena V",
                "givenName": "Veena",
                "familyName": "V",
                "email": "veena@field.b-liffe.org",
                "role": "Lead Researcher",
                "roles": ["ROLE_USER", "ROLE_ADMIN"],
                "customUserId": "mock-user-veena-001",
                "organisation": "Kerala Forest Research Institute",
                "avatar": "VV",
            },
            {
                "id": "user-jane",
                "sub": "mock-user-jane-002",
                "name": "Dr. Jane Goodall",
                "givenName": "Jane",
                "familyName": "Goodall",
                "email": "jane@field.b-liffe.org",
                "role": "Senior Ecologist",
                "roles": ["ROLE_USER"],
                "customUserId": "mock-user-jane-002",
                "organisation": "B-Liffe Research Network",
                "avatar": "JG",
            },
        ]

        for u in users_data:
            existing = await session.get(User, u["id"])
            if not existing:
                user = User(
                    id=u["id"],
                    sub=u["sub"],
                    name=u["name"],
                    givenName=u["givenName"],
                    familyName=u["familyName"],
                    email=u["email"],
                    emailVerified=True,
                    role=u["role"],
                    roles=u["roles"],
                    customUserId=u["customUserId"],
                    organisation=u["organisation"],
                    avatar=u["avatar"],
                )
                session.add(user)
                await session.flush()

                acc = Account(
                    id=f"account-{u['id']}",
                    accountId=u["email"],
                    providerId="credential",
                    password=default_pwd,
                    userId=user.id,
                )
                session.add(acc)

        # 2. Seed User Profile
        prof_res = await session.execute(
            select(UserProfile).where(UserProfile.email == "veena@field.b-liffe.org")
        )
        if not prof_res.scalars().first():
            profile = UserProfile(
                id="profile-demo-veena",
                userId="user-veena",
                fullName="Veena V",
                displayName="Veena",
                email="veena@field.b-liffe.org",
                bio="Biodiversity enthusiast & field observer documenting flora, fauna, and local ecosystems.",
                avatarType="preset",
                avatarPresetId="user",
                avatarCustomUrl=None,
            )
            session.add(profile)

        # 3. Seed Project
        proj = await session.get(BLiffeProject, "proj-tvm-biodiversity-2026")
        if not proj:
            proj = BLiffeProject(
                id="proj-tvm-biodiversity-2026",
                name="Thiruvananthapuram City Biodiversity Register",
                description="Comprehensive municipal ward-level documentation of urban flora, fauna, and local ecosystems.",
                organization="Kerala State Biodiversity Board",
                targetRegion="Thiruvananthapuram Municipal Corporation",
                status="active",
                syncStatus="synced",
            )
            session.add(proj)
            await session.flush()

        # 4. Seed Ward
        ward = await session.get(BLiffeWard, "TVM-WARD-014")
        if not ward:
            ward = BLiffeWard(
                id="TVM-WARD-014",
                projectId=proj.id,
                wardNumber="14",
                wardName="Palayam",
                localBodyName="Thiruvananthapuram Municipal Corporation",
                district="Thiruvananthapuram",
                state="Kerala",
                keyLandmarks="University Stadium, Public Library, Secretariat",
                syncStatus="synced",
            )
            session.add(ward)
            await session.flush()

        # 5. Seed Survey
        survey = await session.get(BLiffeSurvey, "survey-tvm-urban-001")
        if not survey:
            survey = BLiffeSurvey(
                id="survey-tvm-urban-001",
                projectId=proj.id,
                wardId=ward.id,
                leadObserver="Veena V",
                teamMembers=["Veena V", "Anand M"],
                surveyMethod="Opportunistic Encounter",
                habitatType="Urban Park / Garden",
                targetGroup="All Biodiversity",
                startTime="2026-10-30T07:30:00.000Z",
                weatherNotes="Clear sky, pleasant morning breeze, 27°C",
                syncStatus="synced",
            )
            session.add(survey)
            await session.flush()

        # 6. Seed Observation
        obs = await session.get(BLiffeObservation, "obs-birdwing-001")
        if not obs:
            obs = BLiffeObservation(
                id="obs-birdwing-001",
                projectId=proj.id,
                projectIds=[proj.id],
                wardId=ward.id,
                wardName="Ward 14 – Palayam",
                surveyId=survey.id,
                speciesName="Southern Birdwing",
                scientificName="Troides minos",
                localName="ഗരുഡശലഭം",
                speciesGroup="Insects / Butterflies",
                identificationStatus="Identified",
                organismStatus="Wild",
                locationVisibility="Open",
                basis_of_record="HumanObservation",
                tags=["state-butterfly", "canopy-dwelling", "pollinator"],
                notes="State butterfly of Kerala observed nectaring on Pagoda flowers near the Museum garden.",
                individualCount=1,
                lifeStage="Adult",
                microHabitat="Tree Canopy",
                hasTraditionalKnowledge="No",
                latitude=8.4982,
                longitude=76.9534,
                accuracyMeters=4.0,
                location_source="GPS",
                observationAt="2026-10-30T08:15:00.000Z",
                recordedAt="2026-10-30T08:15:00.000Z",
                photos=["https://images.unsplash.com/photo-1544979590-37e9b47eb705"],
                verificationStatus="Validated",
                verifiedBy="KFRI Entomologist",
                syncStatus="synced",
            )
            session.add(obs)

        await session.commit()
        logger.info("seed_pipeline_complete")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
