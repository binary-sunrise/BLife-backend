# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /app

# Enable bytecode compilation and unbuffered stdout
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Install runtime dependencies for healthchecks & SSL certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Copy application source, migrations, configuration, and certs
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY certs ./certs
COPY README.md ./

# Sync the root project in non-editable production mode
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Ensure virtualenv binaries are in PATH
ENV PATH="/app/.venv/bin:$PATH"

# Default environment configuration
ENV HOST=0.0.0.0 \
    PORT=3000

EXPOSE 3000

# Container healthcheck against /health endpoint
HEALTHCHECK --interval=15s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Start production server with Gunicorn running Uvicorn workers
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:3000", "app.main:app"]
