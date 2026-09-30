"""add hits to games

Revision ID: 7242ea7fb968
Revises: 514c5065f6c4
Create Date: 2026-09-15 00:22:43.822496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7242ea7fb968'
down_revision: Union[str, Sequence[str], None] = '514c5065f6c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "games",
        sa.Column(
            "hits",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )

    op.alter_column(
        "games",
        "hits",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("games", "hits")