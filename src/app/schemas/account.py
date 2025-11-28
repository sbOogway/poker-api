
from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    """Pydantic schema for the ``account`` table."""

    name: str = Field(..., description="Primary key – unique account identifier")
    initial_balance: float = Field(..., description="Starting balance of the account")
    currency: str = Field(..., description="Currency code, e.g. 'USD', 'EUR'")
    online: bool = Field(default=False, description="Whether the account is currently online")
    live: bool = Field(default=False, description="Whether the account is marked as live")

class AccountCreate(AccountBase):
    pass

class AccountCreateInternal(AccountBase):
    pass

class AccountRead(AccountBase):
    pass

class AccountUpdate(AccountBase):
    pass

class AccountUpdateInternal(AccountBase):
    pass

class AccountDelete(AccountBase):
    pass
