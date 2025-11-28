from fastcrud import FastCRUD
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.hand import Hand
from ..schemas.hand import (
    HandCreate,
    HandCreateInternal,
    HandDelete,
    HandRead,
    HandUpdate,
    HandUpdateInternal,
)


async def select_all_hand(db: AsyncSession) -> set[str]:
    stmt = select(Hand.id)
    result = await db.execute(stmt)
    return set(result.scalars().all())

async def select_all_hand_session_id(db: AsyncSession, session_id: str) -> set[str]:
    stmt = select(Hand.id).where(Hand.session_id == session_id)
    result = await db.execute(stmt)
    return set(result.scalars().all())

async def select_all_hand_player(db: AsyncSession, player: str) -> set[Hand]:
    stmt = select(Hand).join(Hand.game).where(
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

async def select_all_hand_game():
    pass


CRUDHand = FastCRUD[
    HandCreate, HandCreateInternal, HandRead, HandUpdate, HandUpdateInternal, HandDelete
]

CRUDHand.select_all_hand = staticmethod(select_all_hand)
CRUDHand.select_all_hands_player = staticmethod(select_all_hand_player)
CRUDHand.select_all_hand_session_id = staticmethod(select_all_hand_session_id)


crud_hands = CRUDHand(Hand)
