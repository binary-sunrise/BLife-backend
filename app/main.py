from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.telemetry import instrument_engine, setup_telemetry
from app.db.session import engine

settings = get_settings()
logger = get_logger(__name__)
_startup_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging(settings.ENVIRONMENT)
    logger.info(
        "server_startup",
        application=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        port=settings.PORT,
    )
    setup_telemetry(app, service_name=settings.OTEL_SERVICE_NAME, enabled=settings.OTEL_ENABLED)
    instrument_engine(engine)
    yield
    logger.info("server_shutdown")
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Middleware
    origins = settings.cors_origins
    allow_all = settings.CORS_ALLOW_ALL or settings.ENVIRONMENT != "production"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if allow_all else origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # Register centralized exception handlers
    register_exception_handlers(app)

    # Health check endpoint for monitoring probes
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, Any]:
        return {
            "status": "ok",
            "service": settings.SERVICE_NAME,
            "application": settings.APP_NAME,
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime": round(time.time() - _startup_time, 2),
        }

    # Root discovery endpoint matching B-Liffe contracts
    @app.get("/", tags=["Health"])
    async def root_discovery() -> dict[str, Any]:
        return {
            "name": settings.APP_NAME,
            "status": "online",
            "version": settings.APP_VERSION,
            "health": "/health",
            "endpoints": {
                "auth": {
                    "register": "POST /api/auth/register",
                    "login": "POST /api/auth/login",
                    "logout": "POST /api/auth/logout",
                    "me": "GET /api/auth/me",
                },
                "profile": {
                    "get": "GET /api/profile (or /api/v1/profile)",
                    "update": "PUT /api/profile (or /api/v1/profile)",
                },
                "projects": {
                    "list": "GET /api/projects",
                    "create": "POST /api/projects",
                    "get": "GET /api/projects/:id",
                    "update": "PUT /api/projects/:id",
                    "delete": "DELETE /api/projects/:id",
                    "wards": "GET /api/projects/:projectId/wards",
                },
                "wards": {
                    "identify": "POST /api/wards/identify (GPS spatial point-matching)",
                    "list": "GET /api/wards",
                    "create": "POST /api/wards",
                    "get": "GET /api/wards/:id",
                    "update": "PUT /api/wards/:id",
                    "delete": "DELETE /api/wards/:id",
                },
                "surveys": {
                    "list": "GET /api/surveys",
                    "create": "POST /api/surveys",
                    "get": "GET /api/surveys/:id",
                    "update": "PUT /api/surveys/:id",
                    "delete": "DELETE /api/surveys/:id",
                },
                "observations": {
                    "list": "GET /api/observations",
                    "create": "POST /api/observations",
                    "get": "GET /api/observations/:id",
                    "update": "PUT /api/observations/:id",
                    "delete": "DELETE /api/observations/:id",
                    "batch": "POST /api/observations/batch",
                },
                "sync": {
                    "batch": "POST /api/sync",
                    "status": "GET /api/sync/status",
                },
                "export": {
                    "darwinCore": "GET /api/export/dwc",
                },
                "media": {
                    "upload": "POST /api/media/upload",
                    "presignedUrl": "POST /api/media/presigned-url",
                    "status": "GET /api/media/status",
                },
            },
        }

    # Mount B-Liffe Domain API Routes on /api
    app.include_router(api_v1_router, prefix="/api")

    # Root aliases supported by legacy backend
    app.include_router(auth_router, prefix="/auth", include_in_schema=False)
    app.include_router(profile_router, prefix="/profile", include_in_schema=False)
    app.include_router(profile_router, prefix="/v1/profile", include_in_schema=False)

    return app


app = create_app()
