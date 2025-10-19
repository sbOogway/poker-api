from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, Query

from ...core.db.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.stat import Stat
from ...schemas.stat import StatBase
from ...crud.crud_stat import crud_stat

from typing import Annotated

router = APIRouter(tags=["stat"])

@router.get("/")
async def get_stat(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    return await crud_stat.get_multi(db)