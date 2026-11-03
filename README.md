# B-Liffe Backend Service (FastAPI)

Production-ready, high-performance async backend service for the **B-Liffe Biodiversity Field Data Collection Application**.

Built with **FastAPI**, **SQLAlchemy 2.0 Async**, **PostgreSQL** (`asyncpg`), **Alembic**, and **Redis** background workers.

---

## 🚀 Quick EC2 Deployment & Container Startup

Your live EC2 server is at **`54.252.66.130`** (using key `certs/bliffe-key.pem`).

### 1. Connect to EC2 from Windows PowerShell
```powershell
ssh -i "certs\bliffe-key.pem" ubuntu@54.252.66.130
```

### 2. One-Line Container Startup (inside EC2)
Inside your EC2 terminal, run:
```bash
cd ~/B-Liffe_Backend && git checkout refactor_BE && git pull origin refactor_BE && docker compose up -d --build
```

### 3. Check Status & Logs
```bash
# Verify containers are running
docker compose ps

# View live API logs
docker compose logs -f api
```

### 4. Restart or Stop Containers
```bash
# Restart backend
docker compose restart api

# Stop all containers
docker compose down
```

---

## ⚡ Local Docker Setup

### 1. Configure `.env`
Copy the example configuration:
```bash
cp .env.example .env
```

Ensure your `.env` contains:
```env
ENVIRONMENT=production
PORT=3000
HOST=0.0.0.0

# Allowed frontend domains for CORS
ALLOWED_ORIGINS=https://veenaav.github.io,http://localhost:5173

# Database (AWS RDS PostgreSQL)
DATABASE_URL="postgresql+asyncpg://postgres:BliffeP0stgres2026Secure!@bliffe-db.cxags06gwym1.ap-southeast-2.rds.amazonaws.com:5432/bliffe_db"
DATABASE_SSL=true
DATABASE_SSL_REJECT_UNAUTHORIZED=false
RDS_CA_BUNDLE_PATH=certs/global-bundle.pem

# Auth secret (minimum 32 characters)
BETTER_AUTH_SECRET="lookaround_auth_secret_development_min_32_chars_ok!"
```

### 2. Download AWS RDS Certificate Bundle
```bash
mkdir -p certs
curl -o certs/global-bundle.pem https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

### 3. Start Containers
```bash
docker compose up -d --build
```

---

## 🐍 Local Python Setup (Without Docker)

For local development and testing with hot-reload.

### 1. Install Dependencies
Ensure [`uv`](https://docs.astral.sh/uv/) is installed, then run:
```bash
uv sync
```

### 2. Run Database Migrations
```bash
uv run alembic upgrade head
```

### 3. Start Development Server
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

---

## 🌐 Verifying the Backend

- **Health Check**: [https://bliffe-api.duckdns.org/health](https://bliffe-api.duckdns.org/health) (EC2) or [http://localhost:3000/health](http://localhost:3000/health) (Local)
- **Interactive Swagger Docs**: [https://bliffe-api.duckdns.org/docs](https://bliffe-api.duckdns.org/docs) or [http://localhost:3000/docs](http://localhost:3000/docs)
- **ReDoc**: [http://localhost:3000/redoc](http://localhost:3000/redoc)

```powershell
# Windows PowerShell quick test
curl.exe -i https://bliffe-api.duckdns.org/health
```

---

## 🧪 Testing & Code Quality

```bash
# Run full pytest test suite
uv run pytest

# Check DB connection
uv run python scripts/check_db.py

# Format and lint code
uv run ruff format .
uv run ruff check .

# Static type check
uv run mypy app
```

---

## 🔒 Free HTTPS / Caddy Reference (EC2)

Caddy automatically provisions free Let's Encrypt SSL certificates.

`/etc/caddy/Caddyfile`:
```caddyfile
bliffe-api.duckdns.org {
    reverse_proxy localhost:3000
}
```

Reload Caddy config:
```bash
sudo systemctl reload caddy
```
