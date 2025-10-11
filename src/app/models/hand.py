from ..core.db.database import Base

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from datetime import UTC, datetime

class Hand(Base):
    __tablename__ = "hand"

    id: Mapped[str] = mapped_column(primary_key=True)

    text: Mapped[str] = mapped_column(String(8192))

    time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    currency: Mapped[str] = mapped_column(String(4))

    player_1: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_2: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_3: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_4: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_5: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_6: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_7: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_8: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)
    player_9: Mapped[str] = mapped_column(ForeignKey("player.id"), default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))