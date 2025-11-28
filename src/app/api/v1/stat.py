from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_stat import crud_stat

router = APIRouter(tags=["stat"])

@router.get("/")
async def get_stat(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    return await crud_stat.get_multi(db)
