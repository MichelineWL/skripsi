
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.schemas.periods import (
    PeriodCreate,
    PeriodUpdate,
    PeriodResponse,
)
from app.core.dependencies import get_period_service
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)
from app.services.period_service import PeriodService


router = APIRouter(
    prefix="/periods",
    tags=["Periods"],
)


PeriodServiceDependency = Annotated[
    PeriodService,
    Depends(get_period_service),
]


@router.post(
    "/",
    response_model=PeriodResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_period(
    payload: PeriodCreate,
    service: PeriodServiceDependency,
):
    try:
        return service.create(
            organization_id=payload.organization_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
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
    response_model=list[PeriodResponse],
)
def get_periods(
    service: PeriodServiceDependency,
    organization_id: Annotated[
        int | None,
        Query(),
    ] = None,
):
    try:
        return service.get_all(organization_id=organization_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/{period_id}",
    response_model=PeriodResponse,
)
def get_period(
    period_id: int,
    service: PeriodServiceDependency,
):
    try:
        return service.get_by_id(period_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/{period_id}",
    response_model=PeriodResponse,
)
def update_period(
    period_id: int,
    payload: PeriodUpdate,
    service: PeriodServiceDependency,
):
    try:
        return service.update(
            period_id=period_id,
            name=payload.name,
            start_date=payload.start_date,
            end_date=payload.end_date,
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
    "/{period_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_period(
    period_id: int,
    service: PeriodServiceDependency,
):
    try:
        service.delete(period_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
