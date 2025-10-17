from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, Query
from ...core.db.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from ...crud.crud_player import crud_player
from typing import Annotated

from ...schemas.player import PlayerBase
import json

router = APIRouter(tags=["players"])


@router.get("/players")
async def get_sessions(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    players = await crud_player.get_multi(
        db,
        schema_to_select=PlayerBase,
        return_as_model=True,
        limit=10_000,
        sort_columns="id",
        sort_orders="asc"
    )

    return [player.id for player in players["data"]]
