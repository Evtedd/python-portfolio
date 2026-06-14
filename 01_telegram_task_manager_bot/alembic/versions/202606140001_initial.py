from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "202606140001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.BigInteger(), nullable=False, index=True),
        sa.Column("text", sa.String(length=500), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=True, index=True),
        sa.Column("status", sa.String(length=32), nullable=False, index=True),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("reminded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("done_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("tasks")
