
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas.divisions import (
    DivisionCreate,
    DivisionUpdate,
    DivisionResponse,
)
from app.core.dependencies import get_division_service
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)
from app.services.division_service import DivisionService


router = APIRouter(
    prefix="/divisions",
    tags=["Divisions"],
)


DivisionServiceDependency = Annotated[
    DivisionService,
    Depends(get_division_service),
]


@router.post(
    "/",
    response_model=DivisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_division(
    payload: DivisionCreate,
    service: DivisionServiceDependency,
):
    try:
        return service.create(
            organization_id=payload.organization_id,
            period_id=payload.period_id,
            name=payload.name,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[DivisionResponse],
)
def get_divisions(
    service: DivisionServiceDependency,
    organization_id: Annotated[int | None, Query()] = None,
    period_id: Annotated[int | None, Query()] = None,
):
    try:
        return service.get_all(
            organization_id=organization_id,
            period_id=period_id,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/{division_id}",
    response_model=DivisionResponse,
)
def get_division(
    division_id: int,
    service: DivisionServiceDependency,
):
    try:
        return service.get_by_id(division_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/{division_id}",
    response_model=DivisionResponse,
)
def update_division(
    division_id: int,
    payload: DivisionUpdate,
    service: DivisionServiceDependency,
):
    try:
        return service.update(
            division_id=division_id,
            name=payload.name,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except BusinessRuleError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{division_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_division(
    division_id: int,
    service: DivisionServiceDependency,
):
    try:
        service.delete(division_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
