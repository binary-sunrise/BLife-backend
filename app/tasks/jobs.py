from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


async def export_dwc_job(ctx: dict[str, Any], project_id: str | None = None) -> dict[str, Any]:
    logger.info("executing_background_dwc_export", project_id=project_id)
    # Background export task implementation
    return {
        "status": "completed",
        "projectId": project_id,
        "completedAt": datetime.now(UTC).isoformat(),
    }


async def sync_cleanup_job(ctx: dict[str, Any]) -> dict[str, Any]:
    logger.info("executing_sync_cleanup_job")
    return {
        "status": "completed",
        "timestamp": datetime.now(UTC).isoformat(),
    }
