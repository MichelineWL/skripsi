from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.organization_service import OrganizationService
from app.services.period_service import PeriodService
from app.services.division_service import DivisionService

def get_organization_service(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationService:
    return OrganizationService(db)

def get_period_service(
    db: Annotated[Session, Depends(get_db)],
) -> PeriodService:
    return PeriodService(db)

def get_division_service(
    db: Annotated[Session, Depends(get_db)],
) -> DivisionService:
    return DivisionService(db)