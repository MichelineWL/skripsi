from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.organization_service import OrganizationService


def get_organization_service(
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationService:
    return OrganizationService(db)