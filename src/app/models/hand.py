from ..core.db.database import Base

from sqlalchemy import DateTime, ForeignKey, String, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from typing import List
from datetime import UTC, datetime


class Hand(Base):
    __tablename__ = "hand"

    id: Mapped[str] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(String(8192))

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    game: Mapped[str] = mapped_column(ForeignKey("game.name"))
    session_id: Mapped[str] = mapped_column(ForeignKey("session.id"))

    went_to_showdown: Mapped[bool] = mapped_column(Boolean, default=False)

    flop_cards: Mapped[List[str]] | None = mapped_column(JSON, default=list)
    turn_card: Mapped[str] | None = mapped_column(String, default="")
    river_card: Mapped[str] | None = mapped_column(String, default="")

    player_1: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=False
    )
    player_2: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=False
    )
    player_3: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )
    player_4: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )
    player_5: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )
    player_6: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )
    player_7: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )
    player_8: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )
    player_9: Mapped[str] = mapped_column(
        ForeignKey("player.id"), default=None, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default_factory=lambda: datetime.now(UTC)
    )

    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)