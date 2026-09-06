"""Update games table

Revision ID: c2352860ec02
Revises: e216826606ee
Create Date: 2026-09-07 01:00:12.243880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2352860ec02"
down_revision: Union[str, Sequence[str], None] = "e216826606ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("games_pkey", "games", type_="primary")

    op.add_column(
        "games",
        sa.Column("game_id", sa.Uuid(), nullable=False),
    )
    op.add_column(
        "games",
        sa.Column("ships", sa.JSON(), nullable=False),
    )

    op.create_primary_key(
        "games_pkey",
        "games",
        ["game_id"],
    )

    op.drop_column("games", "session_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "games",
        sa.Column("session_id", sa.UUID(), nullable=False),
    )

    op.drop_constraint("games_pkey", "games", type_="primary")

    op.create_primary_key(
        "games_pkey",
        "games",
        ["session_id"],
    )

    op.drop_column("games", "ships")
    op.drop_column("games", "game_id")