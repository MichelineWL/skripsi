from pydantic import BaseModel, ConfigDict, Field


class ProgramCreate(BaseModel):
    organization_id: int
    period_id: int
    division_id: int
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: str = "planned"


class ProgramUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    status: str = "planned"


class ProgramResponse(BaseModel):
    id: int
    organization_id: int
    period_id: int
    division_id: int
    name: str
    description: str | None
    status: str

    model_config = ConfigDict(from_attributes=True)