from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime



class HandBase(BaseModel):
    id: Annotated[
        str, 
        Field(examples=["257906845279"])
    ]

    text: Annotated[str, Field()]

    time: datetime
    currency: str

    player_1: str
    player_2: str
    player_3: str
    player_4: str
    player_5: str
    player_6: str
    player_7: str
    player_8: str
    player_9: str

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