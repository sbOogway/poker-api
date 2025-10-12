from fastcrud import FastCRUD

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.session import Session
from ..schemas.session import (
    SessionCreate,
    SessionCreateInternal,
    SessionRead,
    SessionUpdate,
    SessionUpdateInternal,
    SessionDelete,
)


async def select_all_session(db: AsyncSession, game: str) -> set[str]:
    stmt = select(Session.id).where(Session.game == game)
    result = await db.execute(stmt)
    return set(result.scalars().all())



CRUDSession = FastCRUD[
    SessionCreate, SessionCreateInternal, SessionRead, SessionUpdate, SessionUpdateInternal, SessionDelete
]

CRUDSession.select_all_session = staticmethod(select_all_session)

crud_session = CRUDSession(Session)
