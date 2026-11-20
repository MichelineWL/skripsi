from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExtractedContentResponse(BaseModel):
    id: int
    document_version_id: int
    extraction_method: str
    content: str
    extraction_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)