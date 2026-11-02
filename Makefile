.PHONY: help install dev start test lint format typecheck migrate upgrade seed worker docker-up docker-down

help:
	@echo "B-Liffe FastAPI Backend Management:"
	@echo "  make install     - Install all project dependencies with uv"
	@echo "  make dev         - Run development server with auto-reload (port 3000)"
	@echo "  make start       - Run production Gunicorn with Uvicorn workers"
	@echo "  make test        - Run test suite with pytest"
	@echo "  make lint        - Run Ruff linter"
	@echo "  make format      - Format code with Ruff"
	@echo "  make typecheck   - Run mypy type checking"
	@echo "  make upgrade     - Apply database migrations with Alembic"
	@echo "  make seed        - Populate database with initial seed data"
	@echo "  make worker      - Start ARQ background worker"
	@echo "  make docker-up   - Run full stack (api, worker, redis) via Docker Compose"
	@echo "  make docker-down - Stop Docker Compose stack"

install:
	uv sync

dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

start:
	uv run gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:3000 app.main:app

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

typecheck:
	uv run mypy app

upgrade:
	uv run alembic upgrade head

seed:
	uv run python -m app.db.seed

worker:
	uv run arq app.tasks.worker.WorkerSettings

docker-up:
	docker compose up -d

docker-down:
	docker compose down
