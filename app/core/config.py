from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "B-Liffe Biodiversity Field Data API"
    SERVICE_NAME: str = "b-liffe-backend"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = Field(default="development", validation_alias="NODE_ENV")
    PORT: int = 3000
    HOST: str = "0.0.0.0"
    BODY_LIMIT: str = "50mb"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )
    CORS_ALLOW_ALL: bool = False

    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/bliffe_db")
    DIRECT_URL: str | None = None
    DB_HOST: str | None = None
    DB_PORT: int = 5432
    DB_USER: str | None = None
    DB_PASSWORD: str | None = None
    DB_NAME: str = "bliffe_db"
    DATABASE_SSL: bool = True
    DATABASE_SSL_REJECT_UNAUTHORIZED: bool = False
    RDS_CA_BUNDLE_PATH: str = "certs/global-bundle.pem"
    DB_POOL_MAX: int = 10
    DB_POOL_MIN: int = 2
    DB_IDLE_TIMEOUT: int = 30000
    DB_CONN_TIMEOUT: int = 10

    # Authentication & Session
    BETTER_AUTH_SECRET: str = "lookaround_prod_auth_secret_kfri_2026_secure_key_32chars!"
    BETTER_AUTH_URL: str = "http://localhost:3000"
    AUTH_SESSION_EXPIRES_IN_SECONDS: int = 604800  # 7 days
    AUTH_MIN_PASSWORD_LENGTH: int = 6

    # Redis & ARQ Background Worker
    REDIS_URL: str = "redis://localhost:6379/0"

    # Amazon S3 / Object Storage (Free Tier)
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str = "bliffe-media"
    AWS_S3_ENDPOINT_URL: str | None = None
    AWS_S3_PUBLIC_URL_PREFIX: str | None = None

    # Observability & OpenTelemetry
    OTEL_ENABLED: bool = True
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "b-liffe-backend"

    @property
    def s3_base_url(self) -> str:
        """Returns the public base URL for objects in the S3 bucket."""
        if self.AWS_S3_PUBLIC_URL_PREFIX:
            return self.AWS_S3_PUBLIC_URL_PREFIX.rstrip("/")
        if self.AWS_REGION == "us-east-1":
            return f"https://{self.AWS_S3_BUCKET}.s3.amazonaws.com"
        return f"https://{self.AWS_S3_BUCKET}.s3.{self.AWS_REGION}.amazonaws.com"

    @property
    def cors_origins(self) -> list[str]:
        origins = [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        if self.FRONTEND_URL:
            origins.append(self.FRONTEND_URL.strip())
        if self.ALLOWED_ORIGINS:
            for item in self.ALLOWED_ORIGINS.split(","):
                cleaned = item.strip()
                if cleaned and cleaned not in origins:
                    origins.append(cleaned)
        return list(dict.fromkeys(origins))

    @property
    def asyncpg_url(self) -> str:
        """Translates standard postgresql:// into asyncpg-compatible postgresql+asyncpg:// url."""
        raw = self.DATABASE_URL
        # Remove any ?sslmode=... because asyncpg requires ssl context in connect_args
        base = raw.split("?")[0]
        if base.startswith("postgres://"):
            return "postgresql+asyncpg://" + base[len("postgres://") :]
        if base.startswith("postgresql://"):
            return "postgresql+asyncpg://" + base[len("postgresql://") :]
        return base


@lru_cache
def get_settings() -> Settings:
    return Settings()
