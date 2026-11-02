from __future__ import annotations

import math

from app.schemas.ward import IdentifiedWardSchema, WardIdentificationResultSchema


class WardBoundary:
    def __init__(
        self,
        ward_id: str,
        ward_number: str,
        ward_name: str,
        local_body_name: str,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ):
        self.ward_id = ward_id
        self.ward_number = ward_number
        self.ward_name = ward_name
        self.local_body_name = local_body_name
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.radius_km = radius_km


TVM_WARDS: list[WardBoundary] = [
    WardBoundary(
        ward_id="TVM-WARD-001",
        ward_number="1",
        ward_name="Kazhakoottam",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.5686,
        center_lon=76.8713,
        radius_km=2.5,
    ),
    WardBoundary(
        ward_id="TVM-WARD-014",
        ward_number="14",
        ward_name="Palayam",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.4982,
        center_lon=76.9534,
        radius_km=1.5,
    ),
    WardBoundary(
        ward_id="TVM-WARD-026",
        ward_number="26",
        ward_name="Pattom",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.5241,
        center_lon=76.9452,
        radius_km=1.8,
    ),
    WardBoundary(
        ward_id="TVM-WARD-033",
        ward_number="33",
        ward_name="Kowdiar",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.5284,
        center_lon=76.9611,
        radius_km=1.6,
    ),
    WardBoundary(
        ward_id="TVM-WARD-041",
        ward_number="41",
        ward_name="Sasthamangalam",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.5132,
        center_lon=76.9741,
        radius_km=1.7,
    ),
    WardBoundary(
        ward_id="TVM-WARD-079",
        ward_number="79",
        ward_name="Fort",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.4821,
        center_lon=76.9463,
        radius_km=1.4,
    ),
    WardBoundary(
        ward_id="TVM-WARD-082",
        ward_number="82",
        ward_name="Chalai",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.4812,
        center_lon=76.9546,
        radius_km=1.3,
    ),
    WardBoundary(
        ward_id="TVM-WARD-093",
        ward_number="93",
        ward_name="Thiruvallam",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.4552,
        center_lon=76.9624,
        radius_km=2.2,
    ),
    WardBoundary(
        ward_id="TVM-WARD-100",
        ward_number="100",
        ward_name="Vizhinjam",
        local_body_name="Thiruvananthapuram Municipal Corporation",
        center_lat=8.3812,
        center_lon=77.0125,
        radius_km=2.8,
    ),
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0  # Earth's radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2.0) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def identify_ward_from_coordinates(
    latitude: float, longitude: float
) -> WardIdentificationResultSchema:
    if (
        not isinstance(latitude, (int, float))
        or not isinstance(longitude, (int, float))
        or math.isnan(latitude)
        or math.isnan(longitude)
        or latitude < -90.0
        or latitude > 90.0
        or longitude < -180.0
        or longitude > 180.0
    ):
        return WardIdentificationResultSchema(
            status="ward_unidentified",
            message="Invalid GPS coordinates provided.",
        )

    # Thiruvananthapuram regional bounding box: 8.2 to 8.9 lat, 76.6 to 77.3 lon
    is_within_district = 8.2 <= latitude <= 8.9 and 76.6 <= longitude <= 77.3

    if not is_within_district:
        return WardIdentificationResultSchema(
            status="ward_unidentified",
            message="Coordinates fall outside the Thiruvananthapuram Municipal Corporation boundary.",
        )

    closest_ward: WardBoundary | None = None
    min_dist = float("inf")

    for ward in TVM_WARDS:
        dist = haversine_distance_km(latitude, longitude, ward.center_lat, ward.center_lon)
        if dist < min_dist:
            min_dist = dist
            closest_ward = ward

    if closest_ward and min_dist <= closest_ward.radius_km * 1.5:
        return WardIdentificationResultSchema(
            status="ward_identified",
            ward=IdentifiedWardSchema(
                wardId=closest_ward.ward_id,
                wardNumber=closest_ward.ward_number,
                wardName=closest_ward.ward_name,
                localBodyName=closest_ward.local_body_name,
            ),
            message=f"Identified as Ward {closest_ward.ward_number} – {closest_ward.ward_name} ({closest_ward.local_body_name}).",
        )

    return WardIdentificationResultSchema(
        status="ward_unidentified",
        message="Coordinates are in Thiruvananthapuram region, but official GIS sub-polygon boundary matching is pending.",
    )
