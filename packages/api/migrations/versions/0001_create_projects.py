"""Create projects table

Revision ID: 0001
Revises:
Create Date: 2026-06-03
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("clerk_user_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("state", sa.String(50), nullable=False, server_default="phase1"),
        sa.Column("phase1_data", JSONB(), nullable=True),
        sa.Column("phase2_data", JSONB(), nullable=True),
        sa.Column("spec_data", JSONB(), nullable=True),
        sa.Column("error", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("idx_projects_user", "projects", ["clerk_user_id"])
    op.create_index("idx_projects_user_state", "projects", ["clerk_user_id", "state"])


def downgrade() -> None:
    op.drop_index("idx_projects_user_state", table_name="projects")
    op.drop_index("idx_projects_user", table_name="projects")
    op.drop_table("projects")
