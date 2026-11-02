from __future__ import annotations

from enum import StrEnum


class IdentificationStatus(StrEnum):
    IDENTIFIED = "Identified"
    UNKNOWN = "Unknown"
    NEEDS_VERIFICATION = "Needs verification"


class OrganismStatus(StrEnum):
    WILD = "Wild"
    CAPTIVE = "Captive"
    CULTIVATED = "Cultivated"
    UNKNOWN = "Unknown / Not sure"


class LocationVisibility(StrEnum):
    OPEN = "Open"
    OBSCURED = "Obscured"
    PRIVATE = "Private"


class SyncStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    SYNCED = "synced"


class LocationSource(StrEnum):
    GPS = "GPS"
    MANUAL = "Manual Pin Adjustment"


class BasisOfRecord(StrEnum):
    HUMAN_OBSERVATION = "HumanObservation"
    MACHINE_OBSERVATION = "MachineObservation"
    PRESERVED_SPECIMEN = "PreservedSpecimen"
    MATERIAL_SAMPLE = "MaterialSample"
    LIVING_SPECIMEN = "LivingSpecimen"
    FOSSIL_SPECIMEN = "FossilSpecimen"
    LITERATURE = "Literature"
    UNKNOWN = "Unknown"


class VerificationStatus(StrEnum):
    UNREVIEWED = "Unreviewed"
    VALIDATED = "Validated"
    FLAGGED = "Flagged"


class YesNo(StrEnum):
    YES = "Yes"
    NO = "No"


class AvatarPresetId(StrEnum):
    USER = "user"
    BIRD = "bird"
    FROG = "frog"
    ELEPHANT = "elephant"
    TURTLE = "turtle"
    SQUIRREL = "squirrel"
    BUTTERFLY = "butterfly"
    LEAF = "leaf"


class AvatarType(StrEnum):
    PRESET = "preset"
    UPLOAD = "upload"


class ProjectStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"
