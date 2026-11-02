"""Script to verify PostgreSQL connectivity and query core tables."""

import asyncio

from sqlalchemy import text

from app.db.session import async_session_factory


async def check_database() -> None:
    print("Connecting to PostgreSQL database...")
    async with async_session_factory() as session:
        version_result = await session.execute(text("SELECT version();"))
        print(f"Database version: {version_result.scalar()}")

    tables = [
        "users",
        "user_profiles",
        "sessions",
        "accounts",
        "verifications",
        "bliffe_projects",
        "bliffe_wards",
        "bliffe_surveys",
        "bliffe_observations",
    ]
    print("\nTable record counts:")
    for tbl in tables:
        async with async_session_factory() as session:
            try:
                res = await session.execute(text(f'SELECT COUNT(*) FROM "{tbl}";'))
                print(f"  - {tbl}: {res.scalar()} rows")
            except Exception as e:
                print(f"  - {tbl}: error ({e})")


if __name__ == "__main__":
    asyncio.run(check_database())
