from ..core.db.database import Base

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from datetime import UTC, datetime

"""
Hand seen by the perspective of each user in a hand
"""
class HandUser(Base):
    __tablename__ = "hand_user"

    hand_id: Mapped[int] = mapped_column(ForeignKey("hand.id"), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.username"), primary_key=True, index=True)

    # need to add all hero data fields

