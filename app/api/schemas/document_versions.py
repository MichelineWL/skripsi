from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentVersionCreate(BaseModel):
    file_path: str = Field(min_length=1, max_length=500)
    file_hash: str = Field(min_length=1, max_length=64)


class DocumentVersionStatusUpdate(BaseModel):
    processing_status: str = Field(min_length=1, max_length=50)


class DocumentVersionResponse(BaseModel):
    id: int
    document_id: int
    version_number: int
    file_path: str
    file_hash: str
    uploaded_at: datetime
    processing_status: str

    model_config = ConfigDict(from_attributes=True)