from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from app.schemas.observation import ObservationSchema


def to_darwin_core_record(obs: ObservationSchema | dict[str, Any]) -> dict[str, Any]:
    if isinstance(obs, dict):
        obs_dict = obs
    else:
        obs_dict = obs.model_dump()

    dynamic_props = {
        "tags": obs_dict.get("tags") or [],
        "organismStatus": obs_dict.get("organismStatus"),
        "locationVisibility": obs_dict.get("locationVisibility"),
        "locationSource": obs_dict.get("location_source"),
        "hasTraditionalKnowledge": obs_dict.get("hasTraditionalKnowledge"),
        "traditionalKnowledgeSource": obs_dict.get("traditionalKnowledgeSource"),
        "administrativeWard": obs_dict.get("wardName") or obs_dict.get("wardId"),
        "surveyId": obs_dict.get("surveyId"),
        "projectId": obs_dict.get("projectId"),
        "projectIds": obs_dict.get("projectIds") or [],
    }

    event_date = (
        obs_dict.get("observationAt")
        or obs_dict.get("recordedAt")
        or obs_dict.get("createdAt")
        or datetime.now(UTC).isoformat()
    )

    record: dict[str, Any] = {
        "dwc:occurrenceID": obs_dict.get("id"),
        "dwc:basisOfRecord": obs_dict.get("basis_of_record") or "HumanObservation",
        "dwc:scientificName": obs_dict.get("scientificName") or None,
        "dwc:vernacularName": obs_dict.get("localName") or obs_dict.get("speciesName") or None,
        "dwc:decimalLatitude": obs_dict.get("latitude"),
        "dwc:decimalLongitude": obs_dict.get("longitude"),
        "dwc:coordinateUncertaintyInMeters": obs_dict.get("accuracyMeters"),
        "dwc:eventDate": event_date,
        "dwc:individualCount": obs_dict.get("individualCount", 1),
        "dwc:lifeStage": obs_dict.get("lifeStage") or None,
        "dwc:habitat": obs_dict.get("microHabitat") or None,
        "dwc:fieldNotes": obs_dict.get("notes") or None,
        "dwc:identificationVerificationStatus": obs_dict.get("verificationStatus"),
        "dwc:dynamicProperties": json.dumps(dynamic_props),
    }

    return record


def export_observations_as_dwc(
    observations: Sequence[ObservationSchema | dict[str, Any]],
) -> dict[str, Any]:
    records = [to_darwin_core_record(o) for o in observations]
    return {
        "exportDate": datetime.now(UTC).isoformat(),
        "recordCount": len(records),
        "records": records,
    }
