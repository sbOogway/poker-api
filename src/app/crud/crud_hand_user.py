from fastcrud import FastCRUD

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.hand_user import HandUser
from ..schemas.hand_user import (
    HandUserCreate,
    HandUserCreateInternal,
    HandUserRead,
    HandUserUpdate,
    HandUserUpdateInternal,
    HandUserDelete,
)


async def select_all_hand_user(db: AsyncSession, user_id) -> set[str]:
    stmt = select(HandUser.hand_id).where(HandUser.user_id == user_id)
    result = await db.execute(stmt)
    return set(result.scalars().all())


CRUDHandUser = FastCRUD[
    HandUserCreate,
    HandUserCreateInternal,
    HandUserRead,
    HandUserUpdate,
    HandUserUpdateInternal,
    HandUserDelete,
]

CRUDHandUser.select_all_hand_user = staticmethod(select_all_hand_user)

crud_hands_user = CRUDHandUser(HandUser)
