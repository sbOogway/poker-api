from fastcrud import FastCRUD

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.hand import Hand
from ..schemas.hand import HandCreate, HandCreateInternal, HandRead, HandUpdate, HandUpdateInternal, HandDelete

async def select_all_hand(db: AsyncSession) -> set[str]:
    stmt = select(Hand.id)
    print("debug hand", stmt.description)
    result = await db.execute(stmt)
    print("debug hand", result)
    return set(result.scalars().all())

CRUDHand = FastCRUD[HandCreate, HandCreateInternal, HandRead, HandUpdate, HandUpdateInternal, HandDelete]

CRUDHand.select_all_hand = staticmethod(select_all_hand)

crud_hands = CRUDHand(Hand)