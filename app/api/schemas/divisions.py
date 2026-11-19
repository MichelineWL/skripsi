from pydantic import BaseModel, ConfigDict, Field


class DivisionCreate(BaseModel):
    organization_id: int
    period_id: int
    name: str = Field(min_length=1, max_length=255)


class DivisionUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class DivisionResponse(BaseModel):
    id: int
    organization_id: int
    period_id: int
    name: str

    model_config = ConfigDict(from_attributes=True)