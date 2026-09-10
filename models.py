from uuid import UUID

from sqlalchemy import JSON, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Game(Base):
    __tablename__ = "games"

    session_id: Mapped[UUID] = mapped_column(
        Uuid,
        primary_key=True,
    )

    ships: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )