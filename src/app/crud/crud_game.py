from fastcrud import FastCRUD

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.game import Game
from ..schemas.game import (
    GameCreate,
    GameCreateInternal,
    GameRead,
    GameUpdate,
    GameUpdateInternal,
    GameDelete,
)


async def select_all_game(db: AsyncSession) -> set[str]:
    stmt = select(Game.name)
    result = await db.execute(stmt)
    return set(result.scalars().all())

CRUDGame = FastCRUD[
    GameCreate, GameCreateInternal, GameRead, GameUpdate, GameUpdateInternal, GameDelete
]

CRUDGame.select_all_game = staticmethod(select_all_game)

crud_game = CRUDGame(Game)
