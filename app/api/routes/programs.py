from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas.programs import (
    ProgramCreate,
    ProgramUpdate,
    ProgramResponse,
)
from app.core.dependencies import get_program_service
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)
from app.services.program_service import ProgramService


router = APIRouter(
    prefix="/programs",
    tags=["Programs"],
)


ProgramServiceDep = Annotated[
    ProgramService,
    Depends(get_program_service),
]


@router.post(
    "/",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_program(
    payload: ProgramCreate,
    service: ProgramServiceDep,
):
    try:
        return service.create(
            organization_id=payload.organization_id,
            period_id=payload.period_id,
            division_id=payload.division_id,
            name=payload.name,
            description=payload.description,
            status=payload.status,
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
    response_model=list[ProgramResponse],
)
def get_programs(
    service: ProgramServiceDep,
    organization_id: int | None = Query(default=None),
    period_id: int | None = Query(default=None),
    division_id: int | None = Query(default=None),
):
    try:
        return service.get_all(
            organization_id=organization_id,
            period_id=period_id,
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
    "/{program_id}",
    response_model=ProgramResponse,
)
def get_program(
    program_id: int,
    service: ProgramServiceDep,
):
    try:
        return service.get_by_id(program_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc


@router.put(
    "/{program_id}",
    response_model=ProgramResponse,
)
def update_program(
    program_id: int,
    payload: ProgramUpdate,
    service: ProgramServiceDep,
):
    try:
        return service.update(
            program_id=program_id,
            name=payload.name,
            description=payload.description,
            status=payload.status,
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
    "/{program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_program(
    program_id: int,
    service: ProgramServiceDep,
):
    try:
        service.delete(program_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc