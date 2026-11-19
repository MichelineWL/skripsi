from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    organization_id: int
    title: str = Field(min_length=1, max_length=255)
    document_type: str = Field(min_length=1, max_length=100)
    period_id: int | None = None
    program_id: int | None = None
    division_id: int | None = None


class DocumentUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    document_type: str = Field(min_length=1, max_length=100)
    period_id: int | None = None
    program_id: int | None = None
    division_id: int | None = None


class DocumentResponse(BaseModel):
    id: int
    organization_id: int
    period_id: int | None
    program_id: int | None
    division_id: int | None
    title: str
    document_type: str

    model_config = ConfigDict(from_attributes=True)