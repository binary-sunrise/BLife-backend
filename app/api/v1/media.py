from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.deps import CurrentUserDep
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.schemas.media import (
    MediaUploadResponseSchema,
    PresignedUrlRequestSchema,
    PresignedUrlResponseSchema,
)
from app.services.s3_service import S3StorageService

router = APIRouter(tags=["Media & S3 Storage"])
settings = get_settings()
s3_service = S3StorageService(settings)

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max per image file


@router.post(
    "/upload",
    response_model=MediaUploadResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Upload image directly to Amazon S3",
)
async def upload_image(
    current_user: CurrentUserDep,
    file: UploadFile = File(...),
    folder: str = Form("observations"),
) -> dict[str, Any]:
    """Uploads an image file to the Amazon S3 bucket (bliffe-media).
    Returns the public S3 URL and object key to store in the database model."""
    if not file.filename:
        raise AppException(status_code=400, message="Filename must not be empty", code="INVALID_FILENAME")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise AppException(status_code=400, message="Uploaded file is empty", code="EMPTY_FILE")

    if len(file_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise AppException(
            status_code=413,
            message=f"File exceeds maximum size limit of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB",
            code="FILE_TOO_LARGE",
        )

    clean_folder = "avatars" if folder == "avatars" else "observations"
    result = s3_service.upload_file(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type,
        folder=clean_folder,
    )
    result["size"] = len(file_bytes)
    return result


@router.post(
    "/presigned-url",
    response_model=PresignedUrlResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Generate presigned S3 PUT URL for direct client upload",
)
async def get_presigned_upload_url(
    payload: PresignedUrlRequestSchema,
    current_user: CurrentUserDep,
) -> dict[str, Any]:
    """Generates a short-lived presigned PUT URL allowing the client to upload an image directly
    to S3 without streaming data through the backend server."""
    clean_folder = "avatars" if payload.folder == "avatars" else "observations"
    return s3_service.generate_presigned_upload_url(
        filename=payload.filename,
        content_type=payload.contentType,
        folder=clean_folder,
    )


@router.get("/status", summary="Check Amazon S3 configuration status")
async def get_s3_status() -> dict[str, Any]:
    """Returns the current status of Amazon S3 object storage configuration."""
    return {
        "configured": s3_service.is_configured,
        "bucket": settings.AWS_S3_BUCKET,
        "region": settings.AWS_REGION,
        "baseUrl": settings.s3_base_url,
    }

