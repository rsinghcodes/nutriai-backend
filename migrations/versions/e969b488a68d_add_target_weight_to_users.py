"""add target_weight to users

Revision ID: e969b488a68d
Revises: 82758d25d9ce
Create Date: 2025-09-02 10:15:47.039342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e969b488a68d'
down_revision: Union[str, Sequence[str], None] = '82758d25d9ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("target_weight", sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "target_weight")
