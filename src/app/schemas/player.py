from pydantic import BaseModel, Field
from typing import Annotated, List
from datetime import datetime

class PlayerBase(BaseModel):
    id: str = Field(..., description="player id")

class PlayerCreate(PlayerBase):
    pass

class PlayerCreateInternal(PlayerBase):
    pass

class PlayerRead(PlayerBase):
    pass

class PlayerUpdate(PlayerBase):
    pass

class PlayerUpdateInternal(PlayerBase):
    pass

class PlayerDelete(PlayerBase):
    pass