from ..core.db.database import Base

from typing import List
from sqlalchemy import DateTime, ForeignKey, String, Float, Text, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from datetime import UTC, datetime

class Player(Base):
    __tablename__ = "player"

    id : Mapped[str] = mapped_column(primary_key=True, index=True)

    
    # vpip: Mapped[int] = mapped_column(Integer, default=0.0)


