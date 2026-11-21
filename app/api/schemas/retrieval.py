from pydantic import BaseModel, Field, field_validator


class RetrievalRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=1000,
    )

    organization_id: int = Field(
        gt=0,
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=10,
    )

    @field_validator("query")
    @classmethod
    def validate_query(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Query cannot be empty.")

        return value


class RetrievalResult(BaseModel):
    score: float
    content: str
    extracted_content_id: int | None = None
    document_version_id: int | None = None
    chunk_index: int | None = None
    locator: str | None = None
    page_number: int | None = None


class RetrievalResponse(BaseModel):
    query: str
    result_count: int
    results: list[RetrievalResult]