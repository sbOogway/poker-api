from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, Query

from ...core.db.database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.report import Report
from ...schemas.report import ReportBase
from ...crud.crud_report import crud_report

from typing import Annotated

router = APIRouter(tags=["report"])

@router.get("/")
async def get_report(
    db: Annotated[AsyncSession, Depends(async_get_db)],
):
    return await crud_report.get_multi(db, schema_to_select=ReportBase)