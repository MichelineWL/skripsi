from app.repositories.period_repository import PeriodRepository
from app.repositories.organization_repository import OrganizationRepository

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class PeriodService:
    def __init__(self, db):
        self.repository = PeriodRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def create(
        self,
        organization_id: int,
        name: str,
        start_date=None,
        end_date=None,
    ):
        self._validate_dates(start_date, end_date)
        self._validate_organization(organization_id)

        name = name.strip()

        if not name:
            raise BusinessRuleError("Period name cannot be empty.")

        return self.repository.create(
            organization_id=organization_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

    def get_by_id(self, period_id: int):
        period = self.repository.get_by_id(period_id)

        if period is None:
            raise ResourceNotFoundError("Period not found.")

        return period

    def get_all(self, organization_id=None):
        if organization_id is not None:
            self._validate_organization(organization_id)

        return self.repository.get_all(organization_id)

    def update(
        self,
        period_id: int,
        name: str,
        start_date=None,
        end_date=None,
    ):
        self._validate_dates(start_date, end_date)

        name = name.strip()

        if not name:
            raise BusinessRuleError("Period name cannot be empty.")

        period = self.repository.update(
            period_id=period_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

        if period is None:
            raise ResourceNotFoundError("Period not found.")

        return period

    def delete(self, period_id: int):
        if not self.repository.delete(period_id):
            raise ResourceNotFoundError("Period not found.")

        return True

    def _validate_organization(self, organization_id: int):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise ResourceNotFoundError("Organization not found.")

    @staticmethod
    def _validate_dates(start_date, end_date):
        if (
            start_date is not None
            and end_date is not None
            and end_date < start_date
        ):
            raise BusinessRuleError(
                "Period end date cannot be earlier than start date."
            )