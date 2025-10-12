from uuid6 import uuid7
from datetime import UTC, datetime
import uuid as uuid_pkg

from sqlalchemy import DateTime, ForeignKey, String, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Account(Base):
    __tablename__ = "account"

    name: Mapped[str] = mapped_column(primary_key=True)

    initial_balance: Mapped[Float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String) 

    online: Mapped[bool] = mapped_column(default=False)
    live: Mapped[bool] = mapped_column(default=False)


    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default_factory=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
