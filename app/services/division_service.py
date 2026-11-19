from app.repositories.division_repository import DivisionRepository
from app.repositories.period_repository import PeriodRepository
from app.repositories.organization_repository import OrganizationRepository

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class DivisionService:
    def __init__(self, db):
        self.repository = DivisionRepository(db)
        self.period_repository = PeriodRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def create(
        self,
        organization_id: int,
        period_id: int,
        name: str,
    ):
        name = name.strip()

        if not name:
            raise BusinessRuleError("Division name cannot be empty.")

        self._validate_organization(organization_id)
        self._validate_period_context(organization_id, period_id)

        return self.repository.create(
            organization_id=organization_id,
            period_id=period_id,
            name=name,
        )

    def get_by_id(self, division_id: int):
        division = self.repository.get_by_id(division_id)

        if division is None:
            raise ResourceNotFoundError("Division not found.")

        return division

    def get_all(
        self,
        organization_id=None,
        period_id=None,
    ):
        if organization_id is not None:
            self._validate_organization(organization_id)

        if period_id is not None:
            period = self.period_repository.get_by_id(period_id)

            if period is None:
                raise ResourceNotFoundError("Period not found.")

            if (
                organization_id is not None
                and period.organization_id != organization_id
            ):
                raise BusinessRuleError(
                    "Period does not belong to the organization."
                )

        return self.repository.get_all(
            organization_id=organization_id,
            period_id=period_id,
        )

    def update(self, division_id: int, name: str):
        name = name.strip()

        if not name:
            raise BusinessRuleError("Division name cannot be empty.")

        division = self.repository.update(
            division_id=division_id,
            name=name,
        )

        if division is None:
            raise ResourceNotFoundError("Division not found.")

        return division

    def delete(self, division_id: int):
        if not self.repository.delete(division_id):
            raise ResourceNotFoundError("Division not found.")

        return True

    def _validate_organization(self, organization_id: int):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise ResourceNotFoundError("Organization not found.")

    def _validate_period_context(
        self,
        organization_id: int,
        period_id: int,
    ):
        period = self.period_repository.get_by_id(period_id)

        if period is None:
            raise ResourceNotFoundError("Period not found.")

        if period.organization_id != organization_id:
            raise BusinessRuleError(
                "Period does not belong to the organization."
            )