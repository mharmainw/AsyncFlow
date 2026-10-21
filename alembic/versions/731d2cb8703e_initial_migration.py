"""Initial migration

Revision ID: 731d2cb8703e
Revises:
Create Date: 2026-10-21 13:41:34.138816

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "731d2cb8703e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial jobs table."""
    op.create_table(
        "jobs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("input_path", sa.String(), nullable=False),
        sa.Column("original_filename", sa.String(), nullable=False),
        sa.Column(
            "operation",
            sa.Enum("CLEAN", "STATISTICS", name="operation"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "QUEUED",
                "PROCESSING",
                "COMPLETED",
                "FAILED",
                name="status",
            ),
            nullable=False,
        ),
        sa.Column(
            "missing_policy",
            sa.Enum(
                "PRESERVE",
                "DROP_ROWS",
                "DROP_REQUIRED",
                name="missingpolicy",
            ),
            nullable=True,
        ),
        sa.Column("required_columns", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("output_path", sa.String(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove the initial jobs table and its enum types."""
    op.drop_table("jobs")
    bind = op.get_bind()
    postgresql.ENUM(name="missingpolicy").drop(bind, checkfirst=True)
    postgresql.ENUM(name="status").drop(bind, checkfirst=True)
    postgresql.ENUM(name="operation").drop(bind, checkfirst=True)
