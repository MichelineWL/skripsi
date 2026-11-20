from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.extracted_contents import (
    ExtractedContentResponse,
)
from app.core.database import get_db
from app.core.dependencies import get_extraction_service
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)
from app.repositories.document_version_repository import (
    DocumentVersionRepository,
)
from app.repositories.extracted_content_repository import (
    ExtractedContentRepository,
)
from app.services.extraction_service import ExtractionService


router = APIRouter(
    prefix="/documents",
    tags=["Document Extraction"],
)


ExtractionServiceDep = Annotated[
    ExtractionService,
    Depends(get_extraction_service),
]

DbSessionDep = Annotated[
    Session,
    Depends(get_db),
]


@router.post(
    "/{document_id}/versions/{version_id}/extract",
    response_model=ExtractedContentResponse,
)
def extract_document_version(
    document_id: int,
    version_id: int,
    service: ExtractionServiceDep,
):
    try:
        version = service.document_version_repository.get_by_id(
            version_id
        )

        if version is None or version.document_id != document_id:
            raise HTTPException(
                status_code=404,
                detail="Document version not found.",
            )

        return service.extract(version_id)

    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get(
    "/{document_id}/versions/{version_id}/extracted-contents",
    response_model=list[ExtractedContentResponse],
)
def get_extracted_contents(
    document_id: int,
    version_id: int,
    db: DbSessionDep,
):
    version_repository = DocumentVersionRepository(db)
    extracted_repository = ExtractedContentRepository(db)

    version = version_repository.get_by_id(version_id)

    if version is None or version.document_id != document_id:
        raise HTTPException(
            status_code=404,
            detail="Document version not found.",
        )

    return extracted_repository.get_by_document_version(
        version_id
    )


@router.get(
    "/{document_id}/versions/{version_id}/extracted-contents/{extracted_content_id}",
    response_model=ExtractedContentResponse,
)
def get_extracted_content(
    document_id: int,
    version_id: int,
    extracted_content_id: int,
    db: DbSessionDep,
):
    version_repository = DocumentVersionRepository(db)
    extracted_repository = ExtractedContentRepository(db)

    version = version_repository.get_by_id(version_id)

    if version is None or version.document_id != document_id:
        raise HTTPException(
            status_code=404,
            detail="Document version not found.",
        )

    extracted_content = extracted_repository.get_by_id(
        extracted_content_id
    )

    if (
        extracted_content is None
        or extracted_content.document_version_id != version_id
    ):
        raise HTTPException(
            status_code=404,
            detail="Extracted content not found.",
        )

    return extracted_content