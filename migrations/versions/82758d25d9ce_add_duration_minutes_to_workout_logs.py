"""Add duration_minutes to workout_logs

Revision ID: 82758d25d9ce
Revises: d8062b0aeb6c
Create Date: 2025-08-31 18:12:37.192777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82758d25d9ce'
down_revision: Union[str, Sequence[str], None] = 'd8062b0aeb6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "workout_logs",
        sa.Column("duration_minutes", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("workout_logs", "duration_minutes")
