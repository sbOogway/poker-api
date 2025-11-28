import json
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.db.database import async_get_db
from ...crud.crud_session import crud_session
from ...schemas.session import SessionIdGameStartTime

router = APIRouter(tags=["sessions"])

@router.get("/sessions")
async def get_sessions(
    db: Annotated[AsyncSession, Depends(async_get_db)],

 ):
    sessions = await crud_session.get_multi(
        db,
        schema_to_select=SessionIdGameStartTime,
        return_as_model=True,
        sort_columns=["start_time"],
        sort_orders="desc"
        )

    return list(map(lambda x: json.loads(x.model_dump_json()), sessions["data"]))
