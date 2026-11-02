from __future__ import annotations

from typing import Any

from arq.connections import RedisSettings

from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.tasks.jobs import export_dwc_job, sync_cleanup_job

logger = get_logger(__name__)
settings = get_settings()


async def startup(ctx: dict[str, Any]) -> None:
    setup_logging(settings.ENVIRONMENT)
    logger.info("arq_worker_startup", redis_url=settings.REDIS_URL)


async def shutdown(ctx: dict[str, Any]) -> None:
    logger.info("arq_worker_shutdown")


class WorkerSettings:
    functions: list[Any] = [export_dwc_job, sync_cleanup_job]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
