from fastcrud import FastCRUD
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.stat import Stat
from ..schemas.stat import (
    StatCreate,
    StatCreateInternal,
    StatDelete,
    StatRead,
    StatUpdate,
    StatUpdateInternal,
)


async def select_all_stat(db: AsyncSession) -> set[str]:
    stmt = select(Stat.id)
    result = await db.execute(stmt)
    return set(result.scalars().all())



CRUDStat = FastCRUD[
    StatCreate, StatCreateInternal, StatRead, StatUpdate, StatUpdateInternal, StatDelete
]

CRUDStat.select_all_stat = staticmethod(select_all_stat)

crud_stat = CRUDStat(Stat)
