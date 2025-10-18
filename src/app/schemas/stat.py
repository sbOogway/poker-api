from pydantic import BaseModel, Field


class StatBase(BaseModel):
    id: str = Field(..., description="stat id")

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