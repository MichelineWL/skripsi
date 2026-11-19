from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_organization_service
from app.core.exceptions import ResourceNotFoundError
from app.services.organization_service import OrganizationService
from app.api.schemas.organizations import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)


router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


OrganizationServiceDependency = Annotated[
    OrganizationService,
    Depends(get_organization_service),
]


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    payload: OrganizationCreate,
    service: OrganizationServiceDependency,
):
    try:
        return service.create(payload.name)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[OrganizationResponse],
)
def get_organizations(
    service: OrganizationServiceDependency,
):
    return service.get_all()


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_id: int,
    service: OrganizationServiceDependency,
):
    try:
        return service.get_by_id(organization_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_id: int,
    payload: OrganizationUpdate,
    service: OrganizationServiceDependency,
):
    try:
        return service.update(
            organization_id=organization_id,
            name=payload.name,
        )
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organization(
    organization_id: int,
    service: OrganizationServiceDependency,
):
    try:
        service.delete(organization_id)
    except ResourceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )