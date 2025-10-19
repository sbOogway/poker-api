from pydantic import BaseModel, Field


class StatBase(BaseModel):
    player_id: str = Field(..., description="player id")
    report_id: str = Field(..., description="report id")

    n_hands: int = Field(...)

    net_profit: float = Field(...)
    rake_paid: float = Field(...)
    vpip: int = Field(...)
    pfr: int = Field(...)
    pfc: int = Field(...)


class StatCreate(StatBase):
    pass


class StatCreateInternal(StatBase):
    pass


class StatRead(StatBase):
    pass


class StatUpdate(StatBase):
    pass


class StatUpdateInternal(StatBase):
    pass


class StatDelete(StatBase):
    pass
