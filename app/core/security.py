from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta


def hash_password(password: str) -> str:
    """Computes SHA-256 hash matching existing Node.js backend credential format."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, stored_hash_or_plain: str | None) -> bool:
    if not stored_hash_or_plain:
        return False
    computed_hash = hash_password(plain_password)
    # Match against sha256 or plain password for compatibility
    return computed_hash == stored_hash_or_plain or plain_password == stored_hash_or_plain


def generate_uuid() -> str:
    return str(uuid.uuid4())


def generate_session_token() -> str:
    return str(uuid.uuid4())


def calculate_session_expiration(duration_seconds: int = 604800) -> datetime:
    # Use timezone-naive datetime matching PostgreSQL timestamp without time zone
    return datetime.now(UTC).replace(tzinfo=None) + timedelta(seconds=duration_seconds)
