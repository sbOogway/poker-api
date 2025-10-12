from ..core.db.database import Base

from typing import List
from sqlalchemy import DateTime, ForeignKey, String, Float, Text, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from datetime import UTC, datetime

class Player(Base):
    __tablename__ = "player"

    id : Mapped[str] = mapped_column(primary_key=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

