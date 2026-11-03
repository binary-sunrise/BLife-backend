from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PresignedUrlRequestSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    filename: str = Field(min_length=1, description="Original image filename (e.g. observation_1.jpg)")
    contentType: str = Field(default="image/jpeg", description="MIME type of the image")
    folder: str = Field(default="observations", description="S3 folder partition (observations or avatars)")


class PresignedUrlResponseSchema(BaseModel):
    uploadUrl: str
    publicUrl: str
    key: str
    folder: str
    expiresIn: int


class MediaUploadResponseSchema(BaseModel):
    url: str
    key: str
    bucket: str
    size: int | None = None

