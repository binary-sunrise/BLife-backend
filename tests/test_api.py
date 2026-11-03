from __future__ import annotations

import json
import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient) -> None:
    res = await client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "b-liffe-backend"
    assert "uptime" in data


@pytest.mark.asyncio
async def test_root_discovery(client: AsyncClient) -> None:
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "endpoints" in data


@pytest.mark.asyncio
class TestBLiffeContractSuite:
    test_run_id = uuid.uuid4().hex[:8]
    test_user_email = f"researcher_{test_run_id}@field.b-liffe.org"
    auth_token: str = ""
    test_project_id: str = ""
    test_ward_id: str = ""
    test_survey_id: str = ""
    test_observation_id: str = ""

    # ==========================================
    # 1. Authentication & Profile Contracts
    # ==========================================
    async def test_register(self, client: AsyncClient) -> None:
        res = await client.post(
            "/api/auth/register",
            json={
                "fullName": "Dr. Jane Goodall",
                "email": TestBLiffeContractSuite.test_user_email,
                "password": "secureFieldPassword2026!",
            },
        )
        assert res.status_code == 201
        data = res.json()
        assert "token" in data
        TestBLiffeContractSuite.auth_token = data["token"]
        assert data["user"]["fullName"] == "Dr. Jane Goodall"
        assert data["user"]["displayName"] == "Dr."
        assert data["user"]["email"] == TestBLiffeContractSuite.test_user_email
        assert data["user"]["avatarPresetId"] == "user"

    async def test_login(self, client: AsyncClient) -> None:
        res = await client.post(
            "/api/auth/login",
            json={
                "email": TestBLiffeContractSuite.test_user_email,
                "password": "secureFieldPassword2026!",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert "token" in data
        assert data["user"]["email"] == TestBLiffeContractSuite.test_user_email

    async def test_me(self, client: AsyncClient) -> None:
        res = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {TestBLiffeContractSuite.auth_token}"},
        )
        assert res.status_code == 200
        profile = res.json()
        assert profile["fullName"] == "Dr. Jane Goodall"

    async def test_profile_get(self, client: AsyncClient) -> None:
        res = await client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {TestBLiffeContractSuite.auth_token}"},
        )
        assert res.status_code == 200
        profile = res.json()
        assert "id" in profile
        assert profile["fullName"]
        assert profile["avatarPresetId"]

    async def test_profile_update(self, client: AsyncClient) -> None:
        res = await client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {TestBLiffeContractSuite.auth_token}"},
            json={
                "fullName": "Dr. Jane Goodall DBE",
                "displayName": "Jane",
                "bio": "Primatologist and anthropologist.",
                "avatarType": "preset",
                "avatarPresetId": "butterfly",
            },
        )
        assert res.status_code == 200
        updated = res.json()
        assert updated["fullName"] == "Dr. Jane Goodall DBE"
        assert updated["displayName"] == "Jane"
        assert updated["avatarPresetId"] == "butterfly"

    # ==========================================
    # 2. Projects Endpoints
    # ==========================================
    async def test_create_project(self, client: AsyncClient) -> None:
        new_project = {
            "name": f"Thiruvananthapuram Urban Ecology Campaign {TestBLiffeContractSuite.test_run_id}",
            "description": "Comprehensive municipal ward-level documentation of urban flora and fauna.",
            "organization": "Kerala State Biodiversity Board",
            "targetRegion": "Thiruvananthapuram District",
            "status": "active",
        }
        res = await client.post("/api/projects", json=new_project)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        TestBLiffeContractSuite.test_project_id = data["id"]
        assert data["name"] == new_project["name"]
        assert data["status"] == "active"
        assert data["organization"] == new_project["organization"]
        assert data["syncStatus"] == "synced"

    async def test_list_projects(self, client: AsyncClient) -> None:
        res = await client.get(f"/api/projects?search={TestBLiffeContractSuite.test_run_id}")
        assert res.status_code == 200
        projects = res.json()
        assert isinstance(projects, list)
        assert len(projects) >= 1
        assert projects[0]["id"] == TestBLiffeContractSuite.test_project_id
        assert isinstance(projects[0]["wardCount"], int)
        assert isinstance(projects[0]["surveyCount"], int)
        assert isinstance(projects[0]["observationCount"], int)

    async def test_get_project_detail(self, client: AsyncClient) -> None:
        res = await client.get(f"/api/projects/{TestBLiffeContractSuite.test_project_id}")
        assert res.status_code == 200
        project = res.json()
        assert project["id"] == TestBLiffeContractSuite.test_project_id
        assert isinstance(project["wards"], list)
        assert isinstance(project["surveys"], list)

    async def test_update_project(self, client: AsyncClient) -> None:
        res = await client.put(
            f"/api/projects/{TestBLiffeContractSuite.test_project_id}",
            json={
                "description": "Updated field initiative notes.",
                "status": "completed",
            },
        )
        assert res.status_code == 200
        updated = res.json()
        assert updated["status"] == "completed"
        assert updated["description"] == "Updated field initiative notes."

    # ==========================================
    # 3. Wards & GIS Boundary Matching
    # ==========================================
    async def test_ward_identify_success(self, client: AsyncClient) -> None:
        # Palayam coordinates in Thiruvananthapuram
        res = await client.post(
            "/api/wards/identify",
            json={"latitude": 8.4982, "longitude": 76.9534},
        )
        assert res.status_code == 200
        result = res.json()
        assert result["status"] == "ward_identified"
        assert result["ward"]["wardNumber"] == "14"
        assert result["ward"]["wardName"] == "Palayam"

    async def test_ward_identify_out_of_bounds(self, client: AsyncClient) -> None:
        # London coordinates
        res = await client.post(
            "/api/wards/identify",
            json={"latitude": 51.5074, "longitude": -0.1278},
        )
        assert res.status_code == 200
        result = res.json()
        assert result["status"] == "ward_unidentified"

    async def test_create_ward(self, client: AsyncClient) -> None:
        new_ward = {
            "projectId": TestBLiffeContractSuite.test_project_id,
            "wardNumber": "14",
            "wardName": "Palayam",
            "localBodyName": "Thiruvananthapuram Municipal Corporation",
            "district": "Thiruvananthapuram",
            "state": "Kerala",
            "keyLandmarks": "University Stadium, Public Library",
        }
        res = await client.post("/api/wards", json=new_ward)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        TestBLiffeContractSuite.test_ward_id = data["id"]
        assert data["wardNumber"] == "14"
        assert data["wardName"] == "Palayam"

    async def test_list_project_wards(self, client: AsyncClient) -> None:
        res = await client.get(f"/api/projects/{TestBLiffeContractSuite.test_project_id}/wards")
        assert res.status_code == 200
        wards = res.json()
        assert isinstance(wards, list)
        assert any(w["id"] == TestBLiffeContractSuite.test_ward_id for w in wards)

    # ==========================================
    # 4. Surveys Endpoints
    # ==========================================
    async def test_create_survey(self, client: AsyncClient) -> None:
        new_survey = {
            "projectId": TestBLiffeContractSuite.test_project_id,
            "wardId": TestBLiffeContractSuite.test_ward_id,
            "leadObserver": "Dr. Jane Goodall",
            "teamMembers": ["Veena V", "Field Assistant A"],
            "surveyMethod": "Line Transect",
            "habitatType": "Urban Park / Garden",
            "targetGroup": "All Biodiversity",
            "startTime": "2026-11-02T10:00:00.000Z",
            "weatherNotes": "Clear sky, 28°C, slight breeze",
        }
        res = await client.post("/api/surveys", json=new_survey)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        TestBLiffeContractSuite.test_survey_id = data["id"]
        assert data["leadObserver"] == "Dr. Jane Goodall"
        assert data["surveyMethod"] == "Line Transect"

    async def test_list_surveys_filter(self, client: AsyncClient) -> None:
        res = await client.get(
            f"/api/surveys?projectId={TestBLiffeContractSuite.test_project_id}&wardId={TestBLiffeContractSuite.test_ward_id}"
        )
        assert res.status_code == 200
        surveys = res.json()
        assert isinstance(surveys, list)
        assert any(s["id"] == TestBLiffeContractSuite.test_survey_id for s in surveys)

    # ==========================================
    # 5. Observations Endpoints
    # ==========================================
    async def test_create_observation(self, client: AsyncClient) -> None:
        new_obs = {
            "projectId": TestBLiffeContractSuite.test_project_id,
            "wardId": TestBLiffeContractSuite.test_ward_id,
            "surveyId": TestBLiffeContractSuite.test_survey_id,
            "speciesName": "Southern Birdwing",
            "scientificName": "Troides minos",
            "localName": "ഗരുഡശലഭം",
            "speciesGroup": "Insects",
            "identificationStatus": "Identified",
            "organismStatus": "Wild",
            "locationVisibility": "Open",
            "basis_of_record": "HumanObservation",
            "tags": ["pollinator", "canopy-dwelling", "state-butterfly"],
            "notes": "Observed nectaring on Pagoda flower in the afternoon.",
            "individualCount": 2,
            "lifeStage": "Adult",
            "microHabitat": "Tree Canopy",
            "habitatType": "Forest",
            "reproductiveAttributes": ["Flower", "Breeding activity"],
            "sex": "Female",
            "evidenceOfPresence": ["Organism"],
            "season": "Post monsoon",
            "hasTraditionalKnowledge": "Yes",
            "traditionalKnowledgeSource": "Elder / knowledgeable local resident",
            "latitude": 8.4982,
            "longitude": 76.9534,
            "accuracyMeters": 4.5,
            "location_source": "GPS",
            "gpsCapturedAt": "2026-11-02T10:14:55.000Z",
            "observationAt": "2026-11-02T10:15:00.000Z",
            "recordedAt": "2026-11-02T10:15:00.000Z",
            "photos": ["https://example.com/photos/birdwing.jpg"],
            "photoMetadata": [
                {
                    "id": "meta-01",
                    "latitude": 8.4982,
                    "longitude": 76.9534,
                    "accuracy": 4.5,
                    "locationSource": "GPS",
                }
            ],
        }
        res = await client.post("/api/observations", json=new_obs)
        assert res.status_code == 201
        obs = res.json()
        assert "id" in obs
        TestBLiffeContractSuite.test_observation_id = obs["id"]
        assert obs["speciesName"] == "Southern Birdwing"
        assert obs["scientificName"] == "Troides minos"
        assert obs["localName"] == "ഗരുഡശലഭം"
        assert obs["basis_of_record"] == "HumanObservation"
        assert obs["individualCount"] == 2
        assert obs["tags"] == ["pollinator", "canopy-dwelling", "state-butterfly"]
        assert obs["habitatType"] == "Forest"
        assert obs["reproductiveAttributes"] == ["Flower", "Breeding activity"]
        assert obs["sex"] == "Female"
        assert obs["evidenceOfPresence"] == ["Organism"]
        assert obs["season"] == "Post monsoon"
        assert obs["gpsCapturedAt"] == "2026-11-02T10:14:55.000Z"
        assert obs["photo"] == "https://example.com/photos/birdwing.jpg"
        assert len(obs["photoMetadata"]) == 1

    async def test_list_observations_filter(self, client: AsyncClient) -> None:
        res = await client.get("/api/observations?tag=pollinator&search=Birdwing")
        assert res.status_code == 200
        observations = res.json()
        assert isinstance(observations, list)
        assert any(o["id"] == TestBLiffeContractSuite.test_observation_id for o in observations)

    async def test_update_observation(self, client: AsyncClient) -> None:
        res = await client.put(
            f"/api/observations/{TestBLiffeContractSuite.test_observation_id}",
            json={
                "verificationStatus": "Validated",
                "verifiedBy": "Expert Entomologist Dr. Jane",
                "verificationNotes": "Identification confirmed via distinctive wing pattern.",
            },
        )
        assert res.status_code == 200
        updated = res.json()
        assert updated["verificationStatus"] == "Validated"
        assert updated["verifiedBy"] == "Expert Entomologist Dr. Jane"

    # ==========================================
    # 6. Offline Sync Endpoints
    # ==========================================
    async def test_sync_batch_upsert(self, client: AsyncClient) -> None:
        sync_batch_id = uuid.uuid4().hex[:8]
        payload = {
            "projects": [
                {
                    "id": f"proj-offline-{sync_batch_id}",
                    "name": f"Offline Synced Forest Project {sync_batch_id}",
                    "status": "active",
                }
            ],
            "wards": [
                {
                    "id": f"ward-offline-{sync_batch_id}",
                    "projectId": f"proj-offline-{sync_batch_id}",
                    "wardNumber": "99",
                    "wardName": "Forest Boundary Ward",
                }
            ],
            "surveys": [
                {
                    "id": f"survey-offline-{sync_batch_id}",
                    "projectId": f"proj-offline-{sync_batch_id}",
                    "wardId": f"ward-offline-{sync_batch_id}",
                    "leadObserver": "Offline Field Worker",
                    "startTime": "2026-11-02T11:00:00.000Z",
                }
            ],
            "observations": [
                {
                    "id": f"obs-offline-{sync_batch_id}",
                    "projectId": f"proj-offline-{sync_batch_id}",
                    "wardId": f"ward-offline-{sync_batch_id}",
                    "surveyId": f"survey-offline-{sync_batch_id}",
                    "speciesName": "Malabar Gliding Frog",
                    "scientificName": "Rhacophorus malabaricus",
                    "basis_of_record": "HumanObservation",
                    "notes": "Found perched on an Arum leaf after monsoon drizzle.",
                    "observationAt": "2026-11-02T11:05:00.000Z",
                    "recordedAt": "2026-11-02T11:05:00.000Z",
                }
            ],
        }
        res = await client.post("/api/sync", json=payload)
        assert res.status_code == 200
        sync_result = res.json()
        assert sync_result["success"] is True
        assert sync_result["synced"]["projects"] == 1
        assert sync_result["synced"]["wards"] == 1
        assert sync_result["synced"]["surveys"] == 1
        assert sync_result["synced"]["observations"] == 1

    async def test_sync_status(self, client: AsyncClient) -> None:
        res = await client.get("/api/sync/status")
        assert res.status_code == 200
        status_data = res.json()
        assert status_data["status"] == "online"
        assert status_data["counts"]["projects"] > 0
        assert status_data["counts"]["wards"] > 0
        assert status_data["counts"]["surveys"] > 0
        assert status_data["counts"]["observations"] > 0

    # ==========================================
    # 7. Darwin Core Standard Export
    # ==========================================
    async def test_export_dwc(self, client: AsyncClient) -> None:
        res = await client.get(
            f"/api/export/dwc?projectId={TestBLiffeContractSuite.test_project_id}"
        )
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data["exportDate"], str)
        assert isinstance(data["records"], list)
        assert len(data["records"]) >= 1

        record = next(
            (
                r
                for r in data["records"]
                if r["dwc:occurrenceID"] == TestBLiffeContractSuite.test_observation_id
            ),
            None,
        )
        assert record is not None
        assert record["dwc:scientificName"] == "Troides minos"
        assert record["dwc:basisOfRecord"] == "HumanObservation"
        assert record["dwc:decimalLatitude"] == 8.4982
        assert record["dwc:decimalLongitude"] == 76.9534

        dynamic_props = json.loads(record["dwc:dynamicProperties"])
        assert isinstance(dynamic_props["tags"], list)
        assert dynamic_props["organismStatus"] == "Wild"
        assert dynamic_props["habitatType"] == "Forest"
        assert dynamic_props["reproductiveAttributes"] == ["Flower", "Breeding activity"]
        assert dynamic_props["sex"] == "Female"
        assert dynamic_props["evidenceOfPresence"] == ["Organism"]
        assert dynamic_props["season"] == "Post monsoon"
        assert record["dwc:habitat"] == "Forest"
