from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator


class SessionBase(BaseModel):
    """Pydantic representation of the SQLAlchemy ``Session`` table."""

    id: str = Field(
        ..., description=" matches the ``id`` column in the DB."
    )
    # start_hour: datetime = Field(..., description="Hour we begin session, used as primary key")

    cash_in: float = Field(None, description="Money in")
    cash_out: float = Field(None, description="Money out")
    
    game: str = Field(..., description="Foreign key to ``game.name``.")
    account: str = Field(..., description="Foreign key to ``account.name``.")
    
    start_time: datetime = Field(..., description="When the session started (UTC).")
    end_time: datetime = Field(..., description="When the session ended (UTC).")

    table_name: str = Field(..., description="Table name")

    bullets: Optional[int] = Field(
        None, description="Optional number of bullets used; may be null in the DB."
    )

class SessionIdGameStartTime(BaseModel):
    id: str
    game: str
    start_time: datetime = Field(...)

    @classmethod
    def from_attributes(cls, obj):
        data = obj.__dict__.copy()
        data["start_time"] = obj.start_time.isoformat()
        print("debug from orm")

        return super().parse_obj(data)



class SessionCreate(SessionBase):
    pass


class SessionCreateInternal(SessionBase):
    pass


class SessionRead(SessionBase):
    pass


class SessionUpdate(SessionBase):
    pass


class SessionUpdateInternal(SessionBase):
    pass


class SessionDelete(SessionBase):
    pass
