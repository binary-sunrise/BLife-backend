from __future__ import annotations

import ssl
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def get_ssl_context() -> ssl.SSLContext | bool:
    is_localhost = "localhost" in settings.DATABASE_URL or "127.0.0.1" in settings.DATABASE_URL
    if is_localhost or not settings.DATABASE_SSL:
        return False

    ctx = ssl.create_default_context()
    if not settings.DATABASE_SSL_REJECT_UNAUTHORIZED:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx.check_hostname = True
        ctx.verify_mode = ssl.CERT_REQUIRED

    # Look for RDS CA Bundle file
    candidate_paths = [
        settings.RDS_CA_BUNDLE_PATH,
        Path.cwd() / "certs" / "global-bundle.pem",
        Path(__file__).resolve().parent.parent.parent / "certs" / "global-bundle.pem",
    ]
    for path_candidate in candidate_paths:
        p = Path(str(path_candidate))
        if p.exists() and p.is_file():
            try:
                ctx.load_verify_locations(cafile=str(p))
                logger.info("loaded_rds_ca_bundle", path=str(p))
                break
            except Exception as e:
                logger.warning("failed_loading_ca_bundle", path=str(p), error=str(e))

    return ctx


connect_args: dict[str, Any] = {}
ssl_ctx = get_ssl_context()
if ssl_ctx is not False:
    connect_args["ssl"] = ssl_ctx

# Tune connection pool for AWS RDS PostgreSQL
engine: AsyncEngine = create_async_engine(
    settings.asyncpg_url,
    connect_args=connect_args,
    pool_size=settings.DB_POOL_MAX,
    max_overflow=settings.DB_POOL_MAX // 2,
    pool_timeout=settings.DB_CONN_TIMEOUT,
    pool_recycle=1800,
    pool_pre_ping=True,
    echo=False,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
