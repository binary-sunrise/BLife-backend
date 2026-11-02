from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncEngine

_instrumented = False


def setup_telemetry(
    app: FastAPI, service_name: str = "b-liffe-backend", enabled: bool = True
) -> None:
    global _instrumented
    if not enabled or _instrumented:
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    # FastAPI instrumentation
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    _instrumented = True


def instrument_engine(engine: AsyncEngine) -> None:
    try:
        import sqlalchemy

        version_parts = [int(p) for p in sqlalchemy.__version__.split(".")[:2] if p.isdigit()]
        if len(version_parts) == 2 and tuple(version_parts) < (2, 1):
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

            SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    except Exception:
        # Gracefully pass if engine instrumentation is unavailable
        pass
