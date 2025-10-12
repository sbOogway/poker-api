from fastcrud import FastCRUD

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.base import Base
from ..schemas.base import (
    BaseCreate,
    BaseCreateInternal,
    BaseRead,
    BaseUpdate,
    BaseUpdateInternal,
    BaseDelete,
)


async def select_all_base(db: AsyncSession) -> set[str]:
    stmt = select(Base.id)
    result = await db.execute(stmt)
    return set(result.scalars().all())



CRUDBase = FastCRUD[
    BaseCreate, BaseCreateInternal, BaseRead, BaseUpdate, BaseUpdateInternal, BaseDelete
]

CRUDBase.select_all_base = staticmethod(select_all_base)

crud_bases = CRUDBase(Base)
