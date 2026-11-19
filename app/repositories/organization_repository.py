from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str) -> Organization:
        organization = Organization(name=name)

        self.db.add(organization)
        self.db.commit()
        self.db.refresh(organization)

        return organization

    def get_by_id(self, organization_id: int) -> Organization | None:
        statement = select(Organization).where(
            Organization.id == organization_id
        )

        return self.db.scalar(statement)

    def get_all(self) -> list[Organization]:
        statement = select(Organization).order_by(Organization.id)

        return list(self.db.scalars(statement).all())

    def update(
        self,
        organization_id: int,
        name: str,
    ) -> Organization | None:
        organization = self.get_by_id(organization_id)

        if organization is None:
            return None

        organization.name = name

        self.db.commit()
        self.db.refresh(organization)

        return organization

    def delete(self, organization_id: int) -> bool:
        organization = self.get_by_id(organization_id)

        if organization is None:
            return False

        self.db.delete(organization)
        self.db.commit()

        return True