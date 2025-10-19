from pydantic import BaseModel, Field
from typing import Annotated, List
from datetime import datetime


class HandBase(BaseModel):
    id: Annotated[str, Field(examples=["257906845279"])]

    text: Annotated[str, Field()]

    time: datetime

    game: str
    session_id: str

    went_to_showdown: bool

    flop_cards: List[str]
    turn_card: str
    river_card: str


    total_pot_size: float = Field(0.0, description="Total size of the pot")

    rake_amount: float = Field(0.0, description="Rake taken from the pot")

    player_1: str = Field(..., description="player at 1 table")
    player_2: str = Field(..., description="player at 2 table")
    player_3: str | None = Field(..., description="player at 3 table")
    player_4: str | None = Field(..., description="player at 4 table")
    player_5: str | None = Field(..., description="player at 5 table")
    player_6: str | None = Field(..., description="player at 6 table")
    player_7: str | None = Field(..., description="player at 7 table")
    player_8: str | None = Field(..., description="player at 8 table")
    player_9: str | None = Field(..., description="player at 9 table")

class HandReadText(BaseModel):
    text: str
    id: str
    session_id: str
    went_to_showdown: bool

class HandRakePot(BaseModel):
    total_pot_size: float
    rake_amount: float

class HandSessionId(BaseModel):
    session_id: str

class HandCreate(HandBase):
    pass


class HandCreateInternal(HandBase):
    pass


class HandRead(HandBase):
    pass


class HandUpdate(HandBase):
    pass


class HandUpdateInternal(HandBase):
    pass


class HandDelete(HandBase):
    pass
