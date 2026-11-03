from __future__ import annotations

import base64
import binascii
import mimetypes
import re
import uuid
from typing import Any

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import Settings, get_settings
from app.core.exceptions import AppException
from app.core.logging import get_logger

logger = get_logger(__name__)

# Allowed MIME types for biodiversity field images
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/heic",
    "image/heif",
}

EXTENSION_BY_MIME: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/heic": ".heic",
    "image/heif": ".heif",
}


class S3StorageException(AppException):
    def __init__(self, message: str, status_code: int = 502) -> None:
        super().__init__(status_code=status_code, message=message, code="S3_STORAGE_ERROR")


class S3StorageService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._client: Any = None

    @property
    def is_configured(self) -> bool:
        """Checks if AWS S3 credentials are configured in environment variables."""
        return bool(
            self.settings.AWS_ACCESS_KEY_ID
            and self.settings.AWS_SECRET_ACCESS_KEY
            and self.settings.AWS_S3_BUCKET
        )

    @property
    def client(self) -> Any:
        if self._client is None:
            if not self.is_configured:
                raise S3StorageException(
                    "AWS S3 is not configured. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, "
                    "and AWS_S3_BUCKET in your environment variables.",
                    status_code=503,
                )

            client_kwargs: dict[str, Any] = {
                "service_name": "s3",
                "aws_access_key_id": self.settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": self.settings.AWS_SECRET_ACCESS_KEY,
                "region_name": self.settings.AWS_REGION,
                "config": Config(signature_version="s3v4"),
            }
            if self.settings.AWS_S3_ENDPOINT_URL:
                client_kwargs["endpoint_url"] = self.settings.AWS_S3_ENDPOINT_URL

            self._client = boto3.client(**client_kwargs)
        return self._client

    def _sanitize_filename(self, filename: str) -> str:
        clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename).strip("_")
        return clean or "image.jpg"

    def _build_public_url(self, key: str) -> str:
        return f"{self.settings.s3_base_url}/{key.lstrip('/')}"

    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str | None = None,
        folder: str = "observations",
    ) -> dict[str, str]:
        """Uploads a file to Amazon S3 bucket (bliffe-media) and returns the public URL and key."""
        clean_name = self._sanitize_filename(filename)
        resolved_content_type = content_type or mimetypes.guess_type(clean_name)[0] or "image/jpeg"

        if resolved_content_type.lower() not in ALLOWED_IMAGE_MIME_TYPES:
            raise S3StorageException(
                f"Unsupported image type '{resolved_content_type}'. Supported formats: JPEG, PNG, WebP, GIF, HEIC.",
                status_code=400,
            )

        # Generate a unique key partitioned by folder
        file_uid = uuid.uuid4().hex[:12]
        key = f"{folder.strip('/')}/{file_uid}_{clean_name}"

        try:
            self.client.put_object(
                Bucket=self.settings.AWS_S3_BUCKET,
                Key=key,
                Body=file_bytes,
                ContentType=resolved_content_type,
            )
            public_url = self._build_public_url(key)
            logger.info(
                "s3_upload_success",
                bucket=self.settings.AWS_S3_BUCKET,
                key=key,
                size_bytes=len(file_bytes),
            )
            return {
                "url": public_url,
                "key": key,
                "bucket": self.settings.AWS_S3_BUCKET,
            }
        except (BotoCoreError, ClientError) as err:
            logger.error("s3_upload_failed", error=str(err), bucket=self.settings.AWS_S3_BUCKET, key=key)
            raise S3StorageException(f"Failed to upload image to S3: {err}") from err

    def generate_presigned_upload_url(
        self,
        filename: str,
        content_type: str = "image/jpeg",
        folder: str = "observations",
        expires_in: int = 900,
    ) -> dict[str, Any]:
        """Generates a secure presigned PUT URL allowing clients to upload directly to S3."""
        clean_name = self._sanitize_filename(filename)
        resolved_content_type = content_type or mimetypes.guess_type(clean_name)[0] or "image/jpeg"

        if resolved_content_type.lower() not in ALLOWED_IMAGE_MIME_TYPES:
            raise S3StorageException(
                f"Unsupported image type '{resolved_content_type}'.",
                status_code=400,
            )

        file_uid = uuid.uuid4().hex[:12]
        key = f"{folder.strip('/')}/{file_uid}_{clean_name}"

        try:
            presigned_url = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.settings.AWS_S3_BUCKET,
                    "Key": key,
                    "ContentType": resolved_content_type,
                },
                ExpiresIn=expires_in,
            )
            public_url = self._build_public_url(key)
            return {
                "uploadUrl": presigned_url,
                "publicUrl": public_url,
                "key": key,
                "folder": folder,
                "expiresIn": expires_in,
            }
        except (BotoCoreError, ClientError) as err:
            logger.error("s3_presigned_url_failed", error=str(err), key=key)
            raise S3StorageException(f"Failed to generate presigned upload URL: {err}") from err

    def upload_base64_if_needed(self, data_or_url: str | None, folder: str = "observations") -> str | None:
        """If data_or_url is a base64 data URI, decodes and uploads it to S3, returning the S3 URL.
        If already an HTTP/HTTPS URL, returns it as-is.
        If S3 is not configured, logs a warning and returns the string safely."""
        if not data_or_url or not isinstance(data_or_url, str):
            return None

        trimmed = data_or_url.strip()
        if not trimmed:
            return ""

        # Already a public web or S3 URL
        if trimmed.startswith("http://") or trimmed.startswith("https://"):
            return trimmed

        # Check for Base64 Data URI pattern (e.g. data:image/jpeg;base64,....)
        data_uri_match = re.match(r"^data:(image\/[a-zA-Z0-9.+_-]+);base64,(.+)$", trimmed, re.DOTALL)
        if not data_uri_match:
            # Check if raw base64 string without data: prefix
            if len(trimmed) > 100 and not trimmed.startswith(("/", "blob:", "file:")):
                mime_type = "image/jpeg"
                raw_b64 = trimmed
            else:
                return trimmed
        else:
            mime_type = data_uri_match.group(1).lower()
            raw_b64 = data_uri_match.group(2)

        if not self.is_configured:
            logger.warning(
                "s3_not_configured_skipping_upload",
                detail="AWS credentials not set; retaining original data string.",
            )
            return trimmed

        try:
            file_bytes = base64.b64decode(raw_b64)
        except binascii.Error:
            logger.warning("invalid_base64_data_cannot_upload_to_s3")
            return trimmed

        ext = EXTENSION_BY_MIME.get(mime_type, ".jpg")
        filename = f"upload_{uuid.uuid4().hex[:8]}{ext}"

        try:
            result = self.upload_file(
                file_bytes=file_bytes,
                filename=filename,
                content_type=mime_type,
                folder=folder,
            )
            return result["url"]
        except Exception as err:
            logger.error("s3_base64_upload_failed", error=str(err))
            return trimmed

    def upload_batch_base64_if_needed(
        self, photos: list[str] | None, folder: str = "observations"
    ) -> list[str]:
        """Processes a list of photo strings/URLs, converting any base64 images into S3 URLs."""
        if not photos:
            return []
        processed: list[str] = []
        for photo in photos:
            if not photo:
                continue
            uploaded_url = self.upload_base64_if_needed(photo, folder=folder)
            if uploaded_url:
                processed.append(uploaded_url)
        return processed

