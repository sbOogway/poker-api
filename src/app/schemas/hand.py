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