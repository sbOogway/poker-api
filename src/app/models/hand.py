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

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))