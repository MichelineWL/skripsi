from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas.documents import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
)
from app.core.dependencies import get_document_service
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


DocumentServiceDep = Annotated[
    DocumentService,
    Depends(get_document_service),
]


@router.post(
    "/",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    payload: DocumentCreate,
    service: DocumentServiceDep,
):
    try:
        return service.create(
            organization_id=payload.organization_id,
            title=payload.title,
            document_type=payload.document_type,
            period_id=payload.period_id,
            program_id=payload.program_id,
            division_id=payload.division_id,
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
    "/",
    response_model=list[DocumentResponse],
)
def get_documents(
    service: DocumentServiceDep,
    organization_id: int | None = Query(default=None),
    period_id: int | None = Query(default=None),
    program_id: int | None = Query(default=None),
    division_id: int | None = Query(default=None),
):
    try:
        return service.get_all(
            organization_id=organization_id,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
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
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    service: DocumentServiceDep,
):
    try:
        return service.get_by_id(document_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.put(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    service: DocumentServiceDep,
):
    try:
        return service.update(
            document_id=document_id,
            title=payload.title,
            document_type=payload.document_type,
            period_id=payload.period_id,
            program_id=payload.program_id,
            division_id=payload.division_id,
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
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    service: DocumentServiceDep,
):
    try:
        service.delete(document_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc