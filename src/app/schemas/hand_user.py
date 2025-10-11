from pydantic import BaseModel, Field
from typing import Annotated, List
from datetime import datetime



class HandUserBase(BaseModel):
    hand_id: str = Field(..., description="Unique identifier for the hand")
    user_id: str = Field(..., description="user we take perspective from")

    # timestamp: datetime = Field(..., description="When the hand was played")
    site: str = Field(..., description="Poker site (e.g., PokerStars)")
    stakes: str = Field(..., description="Stakes/limits (e.g., $0.25/$0.50)")
    table_name: str = Field(..., description="Name or ID of the table")
    position: str = Field(..., description="Hero's seat position")
    hole_cards: List[str] | None = Field(..., description="Hero's two hole cards")
    # hand_text: str = Field(..., description="Raw hand history text")

    # Key analysis metrics
    went_to_showdown: bool = Field(False, description="Did the hand reach showdown")
    won_at_showdown: bool = Field(
        False, description="Won at showdown (W$SD)"
    )
    won_when_saw_flop: bool = Field(
        False, description="Won the hand after seeing the flop"
    )
    saw_flop: bool = Field(False, description="Saw the flop")

    # Financial data
    total_contributed: float = Field(0.0, description="Total amount hero put in")
    total_collected: float = Field(0.0, description="Total amount hero collected")
    net_profit: float = Field(0.0, description="Net profit (collected‑contributed)")

    # Rake analysis
    rake_amount: float = Field(0.0, description="Rake taken from the pot")
    net_profit_before_rake: float = Field(
        0.0, description="Profit before rake deduction"
    )
    net_profit_after_rake: float = Field(
        0.0, description="Profit after rake deduction"
    )
    total_pot_size: float = Field(0.0, description="Total size of the pot")

    # Hand progression (action counts per street)
    preflop_actions: int = Field(0, description="Number of actions pre‑flop")
    flop_actions: int = Field(0, description="Number of actions on the flop")
    turn_actions: int = Field(0, description="Number of actions on the turn")
    river_actions: int = Field(0, description="Number of actions on the river")

    # Board cards
    flop_cards: List[str] = Field(
        default_factory=list, description="Flop cards"
    )
    turn_card: str = Field("", description="Turn card")
    river_card: str = Field("", description="River card")

    # Hand‑strength indicators
    preflop_raised: bool = Field(False, description="Raised pre‑flop")
    preflop_called: bool = Field(False, description="Called pre‑flop")
    preflop_folded: bool = Field(False, description="Folded pre‑flop")
    vpip: bool = Field(False, description="Voluntarily Put Money In Pot")
    cbet_flop: bool = Field(False, description="Continuation bet on flop")
    cbet_turn: bool = Field(False, description="Continuation bet on turn")
    cbet_river: bool = Field(False, description="Continuation bet on river")
    cbet_flop_opportunity: bool = Field(
        False, description="Had opportunity to c‑bet on flop"
    )
    cbet_turn_opportunity: bool = Field(
        False, description="Had opportunity to c‑bet on turn"
    )
    cbet_river_opportunity: bool = Field(
        False, description="Had opportunity to c‑bet on river"
    )

    limped: bool = Field(False, description="Limped pre‑flop")
    called: bool = Field(False, description="Called a bet")
    serial_caller: bool = Field(False, description="Called repeatedly")

    single_raised_pot: bool = Field(False, description="Only one raise in pot")
    three_bet: bool = Field(False, description="Three‑bet occurred")
    four_bet: bool = Field(False, description="Four‑bet occurred")
    five_bet: bool = Field(False, description="Five‑bet occurred")
 

class HandUserCreate(HandUserBase):
    pass

class HandUserCreateInternal(HandUserBase):
    pass

class HandUserRead(HandUserBase):
    pass

class HandUserUpdate(HandUserBase):
    pass

class HandUserUpdateInternal(HandUserBase):
    pass

class HandUserDelete(HandUserBase):
    pass