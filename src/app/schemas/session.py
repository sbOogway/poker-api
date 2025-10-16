from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


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
