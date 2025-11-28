from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Game(Base):
    __tablename__ = "game"

    name: Mapped[str] = mapped_column(primary_key=True)

    stakes: Mapped[str] | None = mapped_column(String)
    currency: str = mapped_column(String)

    site: str = mapped_column(String)

    # cash game, mtt, zoom
    mode: Mapped[str] | None = mapped_column(String)

    # plo, 6max, nlhe
    variant: Mapped[str] | None = mapped_column(String)


    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


