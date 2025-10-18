from pydantic import BaseModel, Field


class ReportBase(BaseModel):
    id: str = Field(..., description="report id")

class ReportCreate(ReportBase):
    pass

class ReportCreateInternal(ReportBase):
    pass

class ReportRead(ReportBase):
    pass

class ReportUpdate(ReportBase):
    pass

class ReportUpdateInternal(ReportBase):
    pass

class ReportDelete(ReportBase):
    pass