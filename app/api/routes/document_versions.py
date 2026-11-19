from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.document_versions import (
    DocumentVersionCreate,
    DocumentVersionStatusUpdate,
    DocumentVersionResponse,
)
from app.core.dependencies import get_document_version_service
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)
from app.services.document_version_service import DocumentVersionService


router = APIRouter(
    prefix="/documents",
    tags=["Document Versions"],
)


DocumentVersionServiceDep = Annotated[
    DocumentVersionService,
    Depends(get_document_version_service),
]


@router.post(
    "/{document_id}/versions",
    response_model=DocumentVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_version(
    document_id: int,
    payload: DocumentVersionCreate,
    service: DocumentVersionServiceDep,
):
    try:
        return service.create(
            document_id=document_id,
            file_path=payload.file_path,
            file_hash=payload.file_hash,
        )
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
    "/{document_id}/versions",
    response_model=list[DocumentVersionResponse],
)
def get_document_versions(
    document_id: int,
    service: DocumentVersionServiceDep,
):
    try:
        return service.get_all(document_id=document_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{document_id}/versions/latest",
    response_model=DocumentVersionResponse,
)
def get_latest_document_version(
    document_id: int,
    service: DocumentVersionServiceDep,
):
    try:
        version = service.get_latest(document_id)

        if version is None:
            raise HTTPException(
                status_code=404,
                detail="Document version not found.",
            )

        return version
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.get(
    "/{document_id}/versions/{version_id}",
    response_model=DocumentVersionResponse,
)
def get_document_version(
    document_id: int,
    version_id: int,
    service: DocumentVersionServiceDep,
):
    try:
        version = service.get_by_id(version_id)

        if version.document_id != document_id:
            raise HTTPException(
                status_code=404,
                detail="Document version not found.",
            )

        return version
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.put(
    "/{document_id}/versions/{version_id}/status",
    response_model=DocumentVersionResponse,
)
def update_document_version_status(
    document_id: int,
    version_id: int,
    payload: DocumentVersionStatusUpdate,
    service: DocumentVersionServiceDep,
):
    try:
        version = service.get_by_id(version_id)

        if version.document_id != document_id:
            raise HTTPException(
                status_code=404,
                detail="Document version not found.",
            )

        return service.update_processing_status(
            document_version_id=version_id,
            processing_status=payload.processing_status,
        )
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


@router.delete(
    "/{document_id}/versions/{version_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_version(
    document_id: int,
    version_id: int,
    service: DocumentVersionServiceDep,
):
    try:
        version = service.get_by_id(version_id)

        if version.document_id != document_id:
            raise HTTPException(
                status_code=404,
                detail="Document version not found.",
            )

        service.delete(version_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc