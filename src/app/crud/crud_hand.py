from fastcrud import FastCRUD

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.hand import Hand
from ..schemas.hand import (
    HandCreate,
    HandCreateInternal,
    HandRead,
    HandUpdate,
    HandUpdateInternal,
    HandDelete,
)


async def select_all_hand(db: AsyncSession) -> set[str]:
    stmt = select(Hand.id)
    result = await db.execute(stmt)
    return set(result.scalars().all())


async def select_all_hand_player(db: AsyncSession, player: str) -> set[Hand]:
    stmt = select(Hand).where(
        or_(
            Hand.player_1 == player,
            Hand.player_2 == player,
            Hand.player_3 == player,
            Hand.player_4 == player,
            Hand.player_5 == player,
            Hand.player_6 == player,
            Hand.player_7 == player,
            Hand.player_8 == player,
            Hand.player_9 == player,
        )
    )
    result = await db.execute(stmt)
    # print(result.scalars().all())
    return result.scalars().all()


CRUDHand = FastCRUD[
    HandCreate, HandCreateInternal, HandRead, HandUpdate, HandUpdateInternal, HandDelete
]

CRUDHand.select_all_hand = staticmethod(select_all_hand)
CRUDHand.select_all_hand_player = staticmethod(select_all_hand_player)

crud_hands = CRUDHand(Hand)
