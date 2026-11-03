from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from httpx import AsyncClient

from app.core.config import Settings
from app.services.s3_service import S3StorageService


@pytest.mark.asyncio
async def test_media_status_endpoint(client: AsyncClient) -> None:
    res = await client.get("/api/media/status")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert data["bucket"] == "bliffe-media"
    assert "region" in data
    assert "baseUrl" in data


def test_s3_service_without_credentials() -> None:
    settings = Settings(
        AWS_ACCESS_KEY_ID="",
        AWS_SECRET_ACCESS_KEY="",
        AWS_S3_BUCKET="bliffe-media",
        AWS_REGION="ap-south-1",
    )
    service = S3StorageService(settings)
    assert not service.is_configured

    # Should retain base64 safely without throwing
    dummy_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
    res = service.upload_base64_if_needed(dummy_b64)
    assert res == dummy_b64

    # Should retain existing HTTP URLs unchanged
    http_url = "https://example.com/photo.jpg"
    assert service.upload_base64_if_needed(http_url) == http_url


def test_s3_service_upload_with_mock_client() -> None:
    settings = Settings(
        AWS_ACCESS_KEY_ID="test_key",
        AWS_SECRET_ACCESS_KEY="test_secret",
        AWS_S3_BUCKET="bliffe-media",
        AWS_REGION="ap-south-1",
    )
    service = S3StorageService(settings)
    assert service.is_configured

    mock_client = MagicMock()
    service._client = mock_client

    result = service.upload_file(
        file_bytes=b"dummy-image-bytes",
        filename="test observation.jpg",
        content_type="image/jpeg",
        folder="observations",
    )
    assert "bliffe-media" in result["url"]
    assert "observations/" in result["key"]
    assert result["bucket"] == "bliffe-media"
    mock_client.put_object.assert_called_once()

    # Presigned URL test
    mock_client.generate_presigned_url.return_value = "https://bliffe-media.s3.amazonaws.com/test-presigned"
    presigned = service.generate_presigned_upload_url(
        filename="flower.png",
        content_type="image/png",
        folder="observations",
    )
    assert presigned["uploadUrl"] == "https://bliffe-media.s3.amazonaws.com/test-presigned"
    assert "flower.png" in presigned["key"]
