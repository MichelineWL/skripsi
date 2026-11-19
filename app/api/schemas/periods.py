from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PeriodCreate(BaseModel):
    organization_id: int
    name: str = Field(min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None


class PeriodUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None


class PeriodResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    start_date: date | None
    end_date: date | None

    model_config = ConfigDict(from_attributes=True)