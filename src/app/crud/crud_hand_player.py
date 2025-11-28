from fastcrud import FastCRUD
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.hand_player import HandPlayer
from ..schemas.hand_player import (
    HandPlayerCreate,
    HandPlayerCreateInternal,
    HandPlayerDelete,
    HandPlayerRead,
    HandPlayerUpdate,
    HandPlayerUpdateInternal,
)


async def select_all_hand_player(db: AsyncSession, player_id) -> set[str]:
    stmt = select(HandPlayer.hand_id).where(HandPlayer.player_id == player_id)
    result = await db.execute(stmt)
    return set(result.scalars().all())


CRUDHandPlayer = FastCRUD[
    HandPlayerCreate,
    HandPlayerCreateInternal,
    HandPlayerRead,
    HandPlayerUpdate,
    HandPlayerUpdateInternal,
    HandPlayerDelete,
]

CRUDHandPlayer.select_all_hand_player = staticmethod(select_all_hand_player)

crud_hands_player = CRUDHandPlayer(HandPlayer)
