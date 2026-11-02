"""initial_schema

Revision ID: 20261102_0001
Revises:
Create Date: 2026-11-02 21:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20261102_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Use IF NOT EXISTS to guarantee idempotent migration on both fresh and pre-existing RDS databases
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("sub", sa.String(), unique=True, nullable=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("givenName", sa.String(), nullable=True),
            sa.Column("familyName", sa.String(), nullable=True),
            sa.Column("email", sa.String(), unique=True, nullable=False),
            sa.Column("emailVerified", sa.Boolean(), default=True, nullable=False),
            sa.Column("image", sa.String(), nullable=True),
            sa.Column("role", sa.String(), nullable=True),
            sa.Column("roles", sa.ARRAY(sa.String()), nullable=False),
            sa.Column("customUserId", sa.String(), nullable=True),
            sa.Column("avatar", sa.String(), nullable=True),
            sa.Column("organisation", sa.String(), nullable=True),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "user_profiles" not in existing_tables:
        op.create_table(
            "user_profiles",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column(
                "userId",
                sa.String(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                unique=True,
                nullable=True,
            ),
            sa.Column("fullName", sa.String(), nullable=False),
            sa.Column("displayName", sa.String(), nullable=False),
            sa.Column("email", sa.String(), unique=True, nullable=False),
            sa.Column("bio", sa.Text(), default="", nullable=False),
            sa.Column("avatarType", sa.String(), default="preset", nullable=False),
            sa.Column("avatarPresetId", sa.String(), default="user", nullable=False),
            sa.Column("avatarCustomUrl", sa.String(), nullable=True),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "sessions" not in existing_tables:
        op.create_table(
            "sessions",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("expiresAt", sa.DateTime(), nullable=False),
            sa.Column("token", sa.String(), unique=True, nullable=False),
            sa.Column("ipAddress", sa.String(), nullable=True),
            sa.Column("userAgent", sa.String(), nullable=True),
            sa.Column(
                "userId", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
            ),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "accounts" not in existing_tables:
        op.create_table(
            "accounts",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("accountId", sa.String(), nullable=False),
            sa.Column("providerId", sa.String(), nullable=False),
            sa.Column(
                "userId", sa.String(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
            ),
            sa.Column("accessToken", sa.Text(), nullable=True),
            sa.Column("refreshToken", sa.Text(), nullable=True),
            sa.Column("idToken", sa.Text(), nullable=True),
            sa.Column("accessTokenExpiresAt", sa.DateTime(), nullable=True),
            sa.Column("refreshTokenExpiresAt", sa.DateTime(), nullable=True),
            sa.Column("scope", sa.String(), nullable=True),
            sa.Column("password", sa.String(), nullable=True),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "verifications" not in existing_tables:
        op.create_table(
            "verifications",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("identifier", sa.String(), nullable=False),
            sa.Column("value", sa.String(), nullable=False),
            sa.Column("expiresAt", sa.DateTime(), nullable=False),
            sa.Column("createdAt", sa.DateTime(), nullable=True),
            sa.Column("updatedAt", sa.DateTime(), nullable=True),
        )

    if "bliffe_projects" not in existing_tables:
        op.create_table(
            "bliffe_projects",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("name", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), default="", nullable=True),
            sa.Column("startDate", sa.String(), nullable=True),
            sa.Column("status", sa.String(), default="active", nullable=False),
            sa.Column("organization", sa.String(), default="", nullable=True),
            sa.Column("targetRegion", sa.String(), default="", nullable=True),
            sa.Column("syncStatus", sa.String(), default="synced", nullable=False),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "bliffe_wards" not in existing_tables:
        op.create_table(
            "bliffe_wards",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column(
                "projectId",
                sa.String(),
                sa.ForeignKey("bliffe_projects.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("wardNumber", sa.String(), nullable=False),
            sa.Column("wardName", sa.String(), nullable=False),
            sa.Column("localBodyName", sa.String(), default="", nullable=True),
            sa.Column("district", sa.String(), default="", nullable=True),
            sa.Column("state", sa.String(), default="", nullable=True),
            sa.Column("keyLandmarks", sa.Text(), default="", nullable=True),
            sa.Column("syncStatus", sa.String(), default="synced", nullable=False),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "bliffe_surveys" not in existing_tables:
        op.create_table(
            "bliffe_surveys",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column(
                "projectId",
                sa.String(),
                sa.ForeignKey("bliffe_projects.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "wardId",
                sa.String(),
                sa.ForeignKey("bliffe_wards.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("leadObserver", sa.String(), nullable=False),
            sa.Column("teamMembers", sa.ARRAY(sa.String()), nullable=False),
            sa.Column(
                "surveyMethod", sa.String(), default="Opportunistic Encounter", nullable=True
            ),
            sa.Column("habitatType", sa.String(), default="Urban Park / Garden", nullable=True),
            sa.Column("targetGroup", sa.String(), default="All Biodiversity", nullable=True),
            sa.Column("startTime", sa.String(), nullable=False),
            sa.Column("endTime", sa.String(), nullable=True),
            sa.Column("weatherNotes", sa.Text(), default="", nullable=True),
            sa.Column("syncStatus", sa.String(), default="synced", nullable=False),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )

    if "bliffe_observations" not in existing_tables:
        op.create_table(
            "bliffe_observations",
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column(
                "surveyId",
                sa.String(),
                sa.ForeignKey("bliffe_surveys.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "wardId",
                sa.String(),
                sa.ForeignKey("bliffe_wards.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("wardName", sa.String(), nullable=True),
            sa.Column(
                "projectId",
                sa.String(),
                sa.ForeignKey("bliffe_projects.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("projectIds", sa.ARRAY(sa.String()), nullable=False),
            sa.Column("speciesName", sa.String(), nullable=False),
            sa.Column("scientificName", sa.String(), default="", nullable=True),
            sa.Column("localName", sa.String(), default="", nullable=True),
            sa.Column("speciesGroup", sa.String(), default="", nullable=True),
            sa.Column("speciesGroups", sa.String(), default="", nullable=True),
            sa.Column("otherSpeciesGroup", sa.String(), default="", nullable=True),
            sa.Column("identificationStatus", sa.String(), default="Identified", nullable=True),
            sa.Column("organismStatus", sa.String(), default="Wild", nullable=True),
            sa.Column("locationVisibility", sa.String(), default="Open", nullable=True),
            sa.Column("basis_of_record", sa.String(), default="HumanObservation", nullable=False),
            sa.Column("tags", sa.ARRAY(sa.String()), nullable=False),
            sa.Column("notes", sa.Text(), default="", nullable=False),
            sa.Column("individualCount", sa.Integer(), default=1, nullable=False),
            sa.Column("lifeStage", sa.String(), default="", nullable=True),
            sa.Column("microHabitat", sa.String(), default="", nullable=True),
            sa.Column("otherMicroHabitat", sa.String(), default="", nullable=True),
            sa.Column("hasTraditionalKnowledge", sa.String(), default="No", nullable=True),
            sa.Column("traditionalKnowledgeSource", sa.String(), default="", nullable=True),
            sa.Column("otherTraditionalKnowledgeSource", sa.String(), default="", nullable=True),
            sa.Column("gps_latitude", sa.Float(), nullable=True),
            sa.Column("gps_longitude", sa.Float(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("location_source", sa.String(), default="GPS", nullable=True),
            sa.Column("accuracyMeters", sa.Float(), nullable=True),
            sa.Column("observationAt", sa.String(), nullable=False),
            sa.Column("recordedAt", sa.String(), nullable=False),
            sa.Column("photos", sa.ARRAY(sa.String()), nullable=False),
            sa.Column("verificationStatus", sa.String(), default="Unreviewed", nullable=True),
            sa.Column("verifiedBy", sa.String(), default="", nullable=True),
            sa.Column("verificationNotes", sa.Text(), default="", nullable=True),
            sa.Column("syncStatus", sa.String(), default="synced", nullable=False),
            sa.Column("userId", sa.String(), nullable=True),
            sa.Column("createdAt", sa.DateTime(), nullable=False),
            sa.Column("updatedAt", sa.DateTime(), nullable=False),
        )


def downgrade() -> None:
    op.drop_table("bliffe_observations")
    op.drop_table("bliffe_surveys")
    op.drop_table("bliffe_wards")
    op.drop_table("bliffe_projects")
    op.drop_table("verifications")
    op.drop_table("accounts")
    op.drop_table("sessions")
    op.drop_table("user_profiles")
    op.drop_table("users")
