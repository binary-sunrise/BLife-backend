from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DarwinCoreRecordSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    occurrenceID: str = Field(alias="dwc:occurrenceID")
    basisOfRecord: str = Field(alias="dwc:basisOfRecord")
    scientificName: str | None = Field(default=None, alias="dwc:scientificName")
    vernacularName: str | None = Field(default=None, alias="dwc:vernacularName")
    decimalLatitude: float | None = Field(default=None, alias="dwc:decimalLatitude")
    decimalLongitude: float | None = Field(default=None, alias="dwc:decimalLongitude")
    coordinateUncertaintyInMeters: float | None = Field(
        default=None, alias="dwc:coordinateUncertaintyInMeters"
    )
    eventDate: str = Field(alias="dwc:eventDate")
    individualCount: int | None = Field(default=None, alias="dwc:individualCount")
    lifeStage: str | None = Field(default=None, alias="dwc:lifeStage")
    habitat: str | None = Field(default=None, alias="dwc:habitat")
    fieldNotes: str | None = Field(default=None, alias="dwc:fieldNotes")
    identificationVerificationStatus: str | None = Field(
        default=None, alias="dwc:identificationVerificationStatus"
    )
    dynamicProperties: str = Field(alias="dwc:dynamicProperties")


class DwCExportResponseSchema(BaseModel):
    exportDate: str
    recordCount: int
    records: list[dict]
