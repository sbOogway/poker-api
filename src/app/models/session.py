from ..core.db.database import Base

from sqlalchemy import DateTime, ForeignKey, String, Boolean, JSON, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from typing import List
from datetime import UTC, datetime


class Session(Base):
    __tablename__ = "session"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    # start_hour: Mapped[str] = mapped_column(DateTime(timezone=True))

    cash_in: Mapped[Float] | None = mapped_column(Float)
    cash_out: Mapped[Float] | None = mapped_column(Float)

    game: Mapped[str] = mapped_column(ForeignKey("game.name"))
    account: Mapped[str] = mapped_column(ForeignKey("account.name"))

    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    bullets: Mapped[int] | None = mapped_column(Integer)

    table_name: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


