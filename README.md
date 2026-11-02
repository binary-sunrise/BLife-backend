# B-Liffe Backend Service (FastAPI)

Production-ready, high-performance async backend service and data layer for the **B-Liffe Biodiversity Field Data Collection Application**.

Built with **FastAPI**, **SQLAlchemy 2.0 Async**, **PostgreSQL** (`asyncpg`), **Alembic**, and **ARQ** background workers. Completely replaces the legacy Node.js/Express service while preserving 100% of existing API contracts, database schemas, Dexie IndexedDB sync behavior, Darwin Core (DwC) standards, and Thiruvananthapuram Corporation GIS boundary point matching.

---

## Production Stack

* **API Framework:** FastAPI + Uvicorn + Gunicorn (Worker model)
* **ORM & Migrations:** SQLAlchemy 2.x Async + Alembic
* **Database Driver:** PostgreSQL 16 + asyncpg (AWS RDS SSL enabled)
* **Background Jobs:** ARQ (Redis-backed async job queue)
* **Logging & Observability:** structlog + OpenTelemetry
* **Data Validation & Settings:** Pydantic v2 + pydantic-settings
* **Package Management:** `uv`
* **Code Quality:** Ruff (linting & formatting) + mypy (strict static type checking)

---

## Directory Architecture

```
B-Liffe_Backend/
├── alembic/                       # Database migrations
│   ├── versions/                  # Versioned async migration scripts
│   ├── env.py                     # Async Alembic runner
│   └── script.py.mako
├── app/
│   ├── api/
│   │   ├── deps.py                # FastApi dependency injection (Session, CurrentUser)
│   │   └── v1/                    # API route handlers
│   │       ├── router.py          # Unified router & compatibility aliases
│   │       ├── auth.py            # Better Auth & session authentication
│   │       ├── profile.py         # User profile management & presets
│   │       ├── projects.py        # Project CRUD & ward sub-resources
│   │       ├── wards.py           # Ward management & GIS spatial identification
│   │       ├── surveys.py         # Biodiversity field survey sessions
│   │       ├── observations.py    # Occurrence observations & batch upsert
│   │       ├── sync.py            # Dexie offline synchronization engine
│   │       └── export.py          # Darwin Core (DwC) occurrence exports
│   ├── core/
│   │   ├── config.py              # Pydantic Settings configuration (.env)
│   │   ├── exceptions.py          # Centralized error handling & Zod contract mapping
│   │   ├── logging.py             # Structured logging with structlog
│   │   ├── security.py            # Password hashing & token generation
│   │   └── telemetry.py           # OpenTelemetry tracing setup
│   ├── db/
│   │   ├── base.py                # DeclarativeBase & TimestampMixin
│   │   ├── session.py             # Async engine & connection pooling
│   │   └── seed.py                # Database seeding pipeline
│   ├── models/                    # SQLAlchemy 2.0 ORM models
│   │   ├── user.py                # User, UserProfile, Session, Account, Verification
│   │   ├── project.py             # BLiffeProject
│   │   ├── ward.py                # BLiffeWard
│   │   ├── survey.py              # BLiffeSurvey
│   │   └── observation.py         # BLiffeObservation
│   ├── repositories/              # Clean async database query abstraction
│   ├── schemas/                   # Pydantic v2 request/response contracts
│   ├── services/                  # Business logic (GIS matching, DwC, Dexie sync)
│   ├── tasks/                     # ARQ worker & background task definitions
│   └── main.py                    # FastAPI application factory & lifespan
├── certs/                         # AWS RDS SSL root CA bundle
├── scripts/                       # Database verification utilities
├── tests/                         # Pytest asynchronous integration suite
├── Dockerfile                     # Multi-stage production container
├── docker-compose.yml             # API, ARQ worker, and Redis services
├── Makefile                       # Developer automation commands
├── pyproject.toml                 # uv package definition & tool configuration
└── README.md
```

---

## Quickstart & Local Development

### 1. Prerequisites
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) installed:
  ```bash
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  # Linux/macOS
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- PostgreSQL 16+ or AWS RDS instance
- Redis 7+ (for ARQ background tasks)

### 2. Environment Configuration
Copy `.env.example` to `.env` and configure your database and secrets:
```bash
cp .env.example .env
```

Ensure `DATABASE_URL` is set:
```env
DATABASE_URL=postgresql://user:pass@host:5432/bliffe_db
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
PORT=3000
HOST=0.0.0.0
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Apply Database Migrations
```bash
uv run alembic upgrade head
```

### 5. Seed Initial Data (Optional)
```bash
uv run python -m app.db.seed
```

### 6. Start Development Server
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

The interactive API documentation is available at:
- **Swagger UI**: [http://localhost:3000/docs](http://localhost:3000/docs)
- **ReDoc**: [http://localhost:3000/redoc](http://localhost:3000/redoc)
- **Health Check**: [http://localhost:3000/health](http://localhost:3000/health)

---

## Running in Production

### Gunicorn with Uvicorn Workers
```bash
uv run gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:3000 app.main:app
```

### ARQ Background Worker
```bash
uv run arq app.tasks.worker.WorkerSettings
```

### Full Stack with Docker Compose
Run the API, ARQ background worker, and Redis in isolated containers:
```bash
docker compose up -d
```

---

## Testing & Code Quality

### Run Test Suite
Run the full 23-test contract verification suite:
```bash
uv run pytest
```

### Linting & Formatting
```bash
# Check code with Ruff
uv run ruff check .

# Automatically format code
uv run ruff format .
```

### Type Checking
Run strict type checking with mypy across all application modules:
```bash
uv run mypy app
```

### Verify Database Connection
```bash
uv run python scripts/check_db.py
```

---

## API Contract Specification

All endpoints maintain 100% backward compatibility with the B-Liffe frontend and Dexie synchronization engine.

### 1. Authentication & Profile
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `POST` | `/api/auth/sign-up/email` | Register account with email & password | `200 OK` |
| `POST` | `/api/auth/register` | Register alias | `201 Created` |
| `POST` | `/api/auth/sign-in/email` | Login with credentials | `200 OK` |
| `POST` | `/api/auth/login` | Login alias | `200 OK` |
| `POST` | `/api/auth/sign-out` | Sign out & invalidate session | `200 OK` |
| `POST` | `/api/auth/logout` | Logout alias | `200 OK` |
| `GET` | `/api/auth/get-session` | Get active session & user | `200 OK` |
| `GET` | `/api/auth/me` | Current user profile | `200 OK` |
| `GET` | `/api/profile` | Get researcher profile | `200 OK` |
| `GET` | `/api/v1/profile` | Profile v1 alias | `200 OK` |
| `PUT` | `/api/profile` | Update profile information | `200 OK` |
| `PUT` | `/api/v1/profile` | Update profile alias | `200 OK` |
| `POST` | `/api/profile/avatar/preset` | Set profile avatar preset | `200 OK` |

### 2. Projects (`/api/projects`)
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `GET` | `/api/projects` | List projects with survey/observation counts | `200 OK` |
| `POST` | `/api/projects` | Create a new project | `201 Created` |
| `GET` | `/api/projects/{id}` | Get full project details with wards | `200 OK` |
| `PUT` | `/api/projects/{id}` | Update project metadata | `200 OK` |
| `DELETE` | `/api/projects/{id}` | Delete project | `200 OK` |
| `GET` | `/api/projects/{id}/summary` | Get project summary statistics | `200 OK` |
| `GET` | `/api/projects/{id}/wards` | List wards belonging to project | `200 OK` |
| `POST` | `/api/projects/{id}/wards` | Add a ward to a project | `201 Created` |

### 3. Wards & GIS Boundary Matching (`/api/wards`)
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `GET` | `/api/wards` | List all wards with optional filtering | `200 OK` |
| `POST` | `/api/wards` | Create administrative ward | `201 Created` |
| `GET` | `/api/wards/{id}` | Get ward by ID | `200 OK` |
| `PUT` | `/api/wards/{id}` | Update ward details | `200 OK` |
| `DELETE` | `/api/wards/{id}` | Delete ward | `200 OK` |
| `POST` | `/api/wards/identify` | Match GPS coordinates to Thiruvananthapuram ward boundaries | `200 OK` |
| `GET` | `/api/wards/identify` | GET alias for GPS coordinate matching | `200 OK` |

### 4. Surveys (`/api/surveys`)
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `GET` | `/api/surveys` | List surveys with filters | `200 OK` |
| `POST` | `/api/surveys` | Record new field survey session | `201 Created` |
| `GET` | `/api/surveys/{id}` | Get survey details & observation count | `200 OK` |
| `PUT` | `/api/surveys/{id}` | Update survey parameters | `200 OK` |
| `DELETE` | `/api/surveys/{id}` | Delete survey | `200 OK` |
| `GET` | `/api/projects/{pId}/wards/{wId}/surveys` | List surveys nested under project and ward | `200 OK` |
| `POST` | `/api/projects/{pId}/wards/{wId}/surveys` | Create survey nested under project and ward | `201 Created` |

### 5. Observations (`/api/observations`)
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `GET` | `/api/observations` | Filter observations by status, tag, species, ward | `200 OK` |
| `POST` | `/api/observations` | Create individual observation record | `201 Created` |
| `GET` | `/api/observations/{id}` | Get observation details | `200 OK` |
| `PUT` | `/api/observations/{id}` | Update observation notes/identification | `200 OK` |
| `DELETE` | `/api/observations/{id}` | Delete observation | `200 OK` |
| `POST` | `/api/observations/batch` | Bulk insert/upsert observation records | `200 OK` |

### 6. Dexie Offline Synchronization (`/api/sync`)
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `POST` | `/api/sync` | Batch upsert Dexie tables (projects, wards, surveys, observations) | `200 OK` |
| `GET` | `/api/sync/counts` | Get table row counts for synchronization verification | `200 OK` |
| `GET` | `/api/sync/status` | Alias for database synchronization status | `200 OK` |

### 7. Darwin Core Standard Export (`/api/export`)
| Method | Endpoint | Description | Status Code |
|--------|----------|-------------|-------------|
| `GET` | `/api/export/dwc` | Export observations formatted as Darwin Core (DwC) occurrences | `200 OK` |
| `GET` | `/api/export/dwc/direct` | Direct stream export of DwC records | `200 OK` |
