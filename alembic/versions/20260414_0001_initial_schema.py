"""initial schema

Revision ID: 20260414_0001
Revises:
Create Date: 2026-04-14 13:00:00
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260414_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "device_references",
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("site_id", sa.Text(), nullable=False),
        sa.Column("reference_id", sa.Text(), nullable=False),
        sa.Column("device_id", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint(
            "organization_id",
            "site_id",
            "reference_id",
            name="pk_device_references",
        ),
    )

    op.create_table(
        "mappings",
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("site_id", sa.Text(), nullable=False),
        sa.Column("reference_id", sa.Text(), nullable=False),
        sa.Column("mapping_id", sa.Text(), nullable=False),
        sa.Column("source_key", sa.Text(), nullable=False),
        sa.Column("target_point_id", sa.Text(), nullable=False),
        sa.Column("transform", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id", "site_id", "reference_id"],
            [
                "device_references.organization_id",
                "device_references.site_id",
                "device_references.reference_id",
            ],
            ondelete="CASCADE",
            name="fk_mappings_reference",
        ),
        sa.PrimaryKeyConstraint(
            "organization_id", "site_id", "reference_id", "mapping_id", name="pk_mappings"
        ),
    )

    op.create_table(
        "links",
        sa.Column("organization_id", sa.Text(), nullable=False),
        sa.Column("site_id", sa.Text(), nullable=False),
        sa.Column("reference_id", sa.Text(), nullable=False),
        sa.Column("link_id", sa.Text(), nullable=False),
        sa.Column("point_id", sa.Text(), nullable=False),
        sa.Column("relation", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id", "site_id", "reference_id"],
            [
                "device_references.organization_id",
                "device_references.site_id",
                "device_references.reference_id",
            ],
            ondelete="CASCADE",
            name="fk_links_reference",
        ),
        sa.PrimaryKeyConstraint(
            "organization_id",
            "site_id",
            "reference_id",
            "link_id",
            name="pk_links",
        ),
    )


def downgrade() -> None:
    op.drop_table("links")
    op.drop_table("mappings")
    op.drop_table("device_references")
