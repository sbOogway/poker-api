from fastcrud import FastCRUD
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.player import Player
from ..schemas.player import (
    PlayerCreate,
    PlayerCreateInternal,
    PlayerDelete,
    PlayerRead,
    PlayerUpdate,
    PlayerUpdateInternal,
)


async def select_all_player(db: AsyncSession) -> set[str]:
    stmt = select(Player.id)
    result = await db.execute(stmt)
    return set(result.scalars().all())

CRUDPlayer = FastCRUD[PlayerCreate, PlayerCreateInternal, PlayerRead, PlayerUpdate, PlayerUpdateInternal, PlayerDelete]

CRUDPlayer.select_all_player = staticmethod(select_all_player)

crud_player = CRUDPlayer(Player)
