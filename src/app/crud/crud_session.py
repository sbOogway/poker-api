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

async def select_all_session_start_time(db: AsyncSession):
    stmt = select(Session.id, Session.start_time, Session.game)
    result = await db.execute(stmt)
    return result.fetchall()

CRUDSession = FastCRUD[
    SessionCreate, SessionCreateInternal, SessionRead, SessionUpdate, SessionUpdateInternal, SessionDelete
]

CRUDSession.select_all_session = staticmethod(select_all_session)
CRUDSession.select_all_session_start_time = staticmethod(select_all_session_start_time)
crud_session = CRUDSession(Session)
