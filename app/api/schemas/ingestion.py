from pydantic import BaseModel


class IngestionResponse(BaseModel):
    extracted_content_id: int
    chunk_count: int
    vector_count: int
    status: str
    cleanup_warning: str | None = None