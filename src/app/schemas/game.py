from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class GameBase(BaseModel):
    """Pydantic representation of the ``Game`` SQLAlchemy model."""

    # Primary‑key fields – all are required because they are part of the PK
    name: str = Field(..., description="Unique identifier for the game")
    stakes: Optional[str] = Field(
        None,
        description="Stakes level (e.g., \"$1/$2\"). Part of the composite primary key.",
    )
    site: str = Field(..., description="Site or platform where the game is hosted")
    mode: Optional[str] = Field(
        None,
        description="Game mode (e.g., \"cash\", \"mtt\", \"zoom\"). Part of the PK.",
    )
    variant: Optional[str] = Field(
        None,
        description="Game variant (e.g., \"plo\", \"6max\", \"nlhe\"). Part of the PK.",
    )

    # Regular columns
    currency: str = Field(..., description="Currency used for the stakes")

class GameReadCurrency(BaseModel):
    currency: str


class GameCreate(GameBase):
    pass

class GameCreateInternal(GameBase):
    pass

class GameRead(GameBase):
    pass

class GameUpdate(GameBase):
    pass

class GameUpdateInternal(GameBase):
    pass

class GameDelete(GameBase):
    pass
