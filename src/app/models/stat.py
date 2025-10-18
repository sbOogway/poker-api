from uuid6 import uuid7
from datetime import UTC, datetime
import uuid as uuid_pkg

from sqlalchemy import DateTime, ForeignKey, String, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base

class Stat(Base):
    __tablename__ = "stat"

    player_id: Mapped[str] = mapped_column(ForeignKey("player.id"), primary_key=True)
    report_id: Mapped[str] = mapped_column(ForeignKey("report.id"), primary_key=True)

    n_hands: Mapped[int] = mapped_column(Integer, default=0)

    net_profit: Mapped[float] = mapped_column(Float, default=0.0) 
    rake_paid: Mapped[float] = mapped_column(Float, default=0.0) 
    vpip: Mapped[float] = mapped_column(Float, default=0.0) 
    pfr: Mapped[float] = mapped_column(Float, default=0.0) 
    pfc: Mapped[float] = mapped_column(Float, default=0.0) 