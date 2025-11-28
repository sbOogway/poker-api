from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Player(Base):
    __tablename__ = "player"

    id : Mapped[str] = mapped_column(primary_key=True, index=True)
    site : Mapped[str] = mapped_column(primary_key=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

