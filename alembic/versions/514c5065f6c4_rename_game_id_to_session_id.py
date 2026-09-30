"""Rename game id to session id

Revision ID: 514c5065f6c4
Revises: c2352860ec02
Create Date: 2026-09-11 01:21:46.240603

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '514c5065f6c4'
down_revision: Union[str, Sequence[str], None] = 'c2352860ec02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "games",
        "game_id",
        new_column_name="session_id",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "games",
        "session_id",
        new_column_name="game_id",
    )
