from ..core.db.database import Base

from typing import List
from sqlalchemy import DateTime, ForeignKey, String, Float, Text, JSON, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from datetime import UTC, datetime

"""
Hand seen by the perspective of each user in a hand
"""
class HandUser(Base):
    __tablename__ = "hand_user"

    hand_id: Mapped[str] = mapped_column(ForeignKey("hand.id"), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("player.id"), primary_key=True, index=True)

    # need to add all hero data fields
    # timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    site: Mapped[str] = mapped_column(String, nullable=False)
    stakes: Mapped[str] = mapped_column(String, nullable=False)
    table_name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[str] = mapped_column(String, nullable=False)
    hole_cards: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    # hand_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Key analysis metrics
    went_to_showdown: Mapped[bool] = mapped_column(Boolean, default=False)
    won_at_showdown: Mapped[bool] = mapped_column(Boolean, default=False)  # W$SD
    won_when_saw_flop: Mapped[bool] = mapped_column(Boolean, default=False)
    saw_flop: Mapped[bool] = mapped_column(Boolean, default=False)

    # Financial data
    total_contributed: Mapped[float] = mapped_column(Float, default=0.0)
    total_collected: Mapped[float] = mapped_column(Float, default=0.0)
    net_profit: Mapped[float] = mapped_column(Float, default=0.0)

    # Rake analysis
    rake_amount: Mapped[float] = mapped_column(Float, default=0.0)
    net_profit_before_rake: Mapped[float] = mapped_column(Float, default=0.0)
    net_profit_after_rake: Mapped[float] = mapped_column(Float, default=0.0)
    total_pot_size: Mapped[float] = mapped_column(Float, default=0.0)

    # Hand progression (action counts per street)
    preflop_actions: Mapped[int] = mapped_column(Integer, default=0)
    flop_actions: Mapped[int] = mapped_column(Integer, default=0)
    turn_actions: Mapped[int] = mapped_column(Integer, default=0)
    river_actions: Mapped[int] = mapped_column(Integer, default=0)

    # Board cards
    flop_cards: Mapped[List[str]] = mapped_column(JSON, default=list)
    turn_card: Mapped[str] = mapped_column(String, default="")
    river_card: Mapped[str] = mapped_column(String, default="")

    # Hand‑strength indicators
    preflop_raised: Mapped[bool] = mapped_column(Boolean, default=False)
    preflop_called: Mapped[bool] = mapped_column(Boolean, default=False)
    preflop_folded: Mapped[bool] = mapped_column(Boolean, default=False)
    vpip: Mapped[bool] = mapped_column(Boolean, default=False)  # Voluntarily Put money In Pot
    cbet_flop: Mapped[bool] = mapped_column(Boolean, default=False)
    cbet_turn: Mapped[bool] = mapped_column(Boolean, default=False)
    cbet_river: Mapped[bool] = mapped_column(Boolean, default=False)
    cbet_flop_opportunity: Mapped[bool] = mapped_column(Boolean, default=False)
    cbet_turn_opportunity: Mapped[bool] = mapped_column(Boolean, default=False)
    cbet_river_opportunity: Mapped[bool] = mapped_column(Boolean, default=False)

    limped: Mapped[bool] = mapped_column(Boolean, default=False)
    called: Mapped[bool] = mapped_column(Boolean, default=False)
    serial_caller: Mapped[bool] = mapped_column(Boolean, default=False)

    single_raised_pot: Mapped[bool] = mapped_column(Boolean, default=False)
    three_bet: Mapped[bool] = mapped_column(Boolean, default=False)
    four_bet: Mapped[bool] = mapped_column(Boolean, default=False)
    five_bet: Mapped[bool] = mapped_column(Boolean, default=False)

