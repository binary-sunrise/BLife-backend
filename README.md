# 🌿 B-Liffe Backend (FastAPI API Service)

High-performance asynchronous REST API powering the B-Liffe (Vasudha) biodiversity survey and ecological monitoring application. Built with **FastAPI**, **SQLAlchemy 2.0 (Asyncpg)**, and **AWS Elastic Beanstalk (Docker)**.

[![AWS Elastic Beanstalk](https://img.shields.io/badge/AWS-Elastic_Beanstalk-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](#-live-api-endpoints)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-AWS_RDS-336791?style=flat-square&logo=postgresql&logoColor=white)](https://aws.amazon.com/rds/postgresql/)
[![Docker](https://img.shields.io/badge/Docker-Amazon_Linux_2023-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)

---

## 🌐 Live API Endpoints

* 🚀 **API Base URL:** `http://bliffe-api.ap-southeast-2.elasticbeanstalk.com`
* 📖 **Interactive Swagger UI (OpenAPI Docs):** `http://bliffe-api.ap-southeast-2.elasticbeanstalk.com/docs`
* 🩺 **Health Check:** `http://bliffe-api.ap-southeast-2.elasticbeanstalk.com/health`

---

## 🏗️ Architecture & Features

* **Framework**: FastAPI (Python 3.12) running under Gunicorn with Uvicorn worker pool.
* **Database**: AWS RDS PostgreSQL with asyncpg connection pooling & SSL certificate verification.
* **Storage**: Amazon S3 (`bliffe-media`) for observation photos and survey attachments.
* **Reverse Proxy**: Built-in Nginx via `.platform/nginx/conf.d/custom.conf` routing port 80 to container port 3000.
* **Continuous Deployment**: Automated GitHub Actions workflow using AWS CLI deploying to AWS Elastic Beanstalk on push.

---

## 🚀 Local Development

### Prerequisites
* [Python 3.12+](https://www.python.org/)
* [uv](https://docs.astral.sh/uv/) package manager
* Running PostgreSQL instance

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/binary-sunrise/lookaround_backend.git
cd lookaround_backend

# 2. Sync dependencies
uv sync

# 3. Configure local environment
cp .env.example .env
# Update DATABASE_URL and secrets in .env

# 4. Run database migrations
uv run alembic upgrade head

# 5. Start dev server
uv run uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

---

## ☁️ Deployment (CI/CD)

Deployments are automated through GitHub Actions (`.github/workflows/deploy.yml`):
1. Runs on push to `main` and `refactor_BE` branches.
2. Authenticates using GitHub repository secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`.
3. Creates a clean deployment package excluding caches, tests, and `.venv`.
4. Uploads package to Elastic Beanstalk S3 storage and updates environment `bliffe-backend-prod`.
