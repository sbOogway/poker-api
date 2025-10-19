from fastcrud import FastCRUD

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.report import Report
from ..schemas.report import (
    ReportCreate,
    ReportCreateInternal,
    ReportRead,
    ReportUpdate,
    ReportUpdateInternal,
    ReportDelete,
)


async def select_all_report(db: AsyncSession) -> set[str]:
    stmt = select(Report.id)
    result = await db.execute(stmt)
    return set(result.scalars().all())



CRUDReport = FastCRUD[
    ReportCreate, ReportCreateInternal, ReportRead, ReportUpdate, ReportUpdateInternal, ReportDelete
]

CRUDReport.select_all_report = staticmethod(select_all_report)

crud_report = CRUDReport(Report)