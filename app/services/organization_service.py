from app.repositories.organization_repository import OrganizationRepository
from app.core.exceptions import ResourceNotFoundError


class OrganizationService:
    def __init__(self, db):
        self.repository = OrganizationRepository(db)

    def create(self, name: str):
        name = name.strip()

        if not name:
            raise ValueError("Organization name cannot be empty.")

        return self.repository.create(name)

    def get_by_id(self, organization_id: int):
        organization = self.repository.get_by_id(organization_id)

        if organization is None:
            raise ResourceNotFoundError("Organization not found.")

        return organization

    def get_all(self):
        return self.repository.get_all()

    def update(self, organization_id: int, name: str):
        name = name.strip()

        if not name:
            raise ValueError("Organization name cannot be empty.")

        organization = self.repository.update(organization_id, name)

        if organization is None:
            raise ResourceNotFoundError("Organization not found.")

        return organization

    def delete(self, organization_id: int):
        deleted = self.repository.delete(organization_id)

        if not deleted:
            raise ResourceNotFoundError("Organization not found.")

        return True