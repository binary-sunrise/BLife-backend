"""add_observation_ecological_fields

Revision ID: 20261103_0002
Revises: 20261102_0001
Create Date: 2026-11-03 20:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261103_0002"
down_revision: str | None = "20261102_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = {c["name"] for c in inspector.get_columns("bliffe_observations")}

    if "photo" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column("photo", sa.String(), nullable=True, server_default=""),
        )
    if "habitatType" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column("habitatType", sa.String(), nullable=True, server_default=""),
        )
    if "reproductiveAttributes" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column(
                "reproductiveAttributes",
                sa.ARRAY(sa.String()),
                nullable=False,
                server_default="{}",
            ),
        )
    if "sex" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column("sex", sa.String(), nullable=True, server_default=""),
        )
    if "evidenceOfPresence" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column(
                "evidenceOfPresence",
                sa.ARRAY(sa.String()),
                nullable=False,
                server_default="{}",
            ),
        )
    if "season" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column("season", sa.String(), nullable=True, server_default=""),
        )
    if "gpsCapturedAt" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column("gpsCapturedAt", sa.String(), nullable=True),
        )
    if "photoMetadata" not in existing_columns:
        op.add_column(
            "bliffe_observations",
            sa.Column(
                "photoMetadata",
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=False,
                server_default="[]",
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = {c["name"] for c in inspector.get_columns("bliffe_observations")}

    for col in [
        "photoMetadata",
        "gpsCapturedAt",
        "season",
        "evidenceOfPresence",
        "sex",
        "reproductiveAttributes",
        "habitatType",
        "photo",
    ]:
        if col in existing_columns:
            op.drop_column("bliffe_observations", col)

