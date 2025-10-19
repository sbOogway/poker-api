from pydantic import BaseModel, Field
from typing import Annotated, List
from datetime import datetime



class HandPlayerBase(BaseModel):
    hand_id: str = Field(..., description="Unique identifier for the hand")
    player_id: str = Field(..., description="user we take perspective from")
    session_id: str | None  = Field(..., description="session id of the user perspective")

    position: str = Field(..., description="Hero's seat position")
    hole_cards: List[str] | None = Field(..., description="Hero's two hole cards")

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
    
    net_profit_before_rake: float = Field(
        0.0, description="Profit before rake deduction"
    )
    net_profit_after_rake: float = Field(
        0.0, description="Profit after rake deduction"
    )
    

    # Hand progression (action counts per street)
    preflop_actions: int = Field(0, description="Number of actions pre‑flop")
    flop_actions: int = Field(0, description="Number of actions on the flop")
    turn_actions: int = Field(0, description="Number of actions on the turn")
    river_actions: int = Field(0, description="Number of actions on the river")

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
 

class HandPlayerReport(BaseModel):
    net_profit: float
    net_profit_before_rake: float

    vpip: bool
    preflop_raised: bool
    preflop_called: bool
    preflop_folded: bool

class HandPlayerCreate(HandPlayerBase):
    pass

class HandPlayerCreateInternal(HandPlayerBase):
    pass

class HandPlayerRead(HandPlayerBase):
    pass

class HandPlayerUpdate(HandPlayerBase):
    pass

class HandPlayerUpdateInternal(HandPlayerBase):
    pass

class HandPlayerDelete(HandPlayerBase):
    pass