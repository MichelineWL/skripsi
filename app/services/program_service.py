from app.repositories.program_repository import ProgramRepository
from app.repositories.period_repository import PeriodRepository
from app.repositories.division_repository import DivisionRepository
from app.repositories.organization_repository import OrganizationRepository

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class ProgramService:
    def __init__(self, db):
        self.repository = ProgramRepository(db)
        self.period_repository = PeriodRepository(db)
        self.division_repository = DivisionRepository(db)
        self.organization_repository = OrganizationRepository(db)

    def create(
        self,
        organization_id: int,
        period_id: int,
        division_id: int,
        name: str,
        description: str | None = None,
        status: str = "planned",
    ):
        name = name.strip()

        if not name:
            raise BusinessRuleError("Program name cannot be empty.")

        self._validate_context(
            organization_id,
            period_id,
            division_id,
        )

        return self.repository.create(
            organization_id=organization_id,
            period_id=period_id,
            division_id=division_id,
            name=name,
            description=description,
            status=status,
        )

    def get_by_id(self, program_id: int):
        program = self.repository.get_by_id(program_id)

        if program is None:
            raise ResourceNotFoundError("Program not found.")

        return program

    def get_all(
        self,
        organization_id=None,
        period_id=None,
        division_id=None,
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

        if division_id is not None:
            division = self.division_repository.get_by_id(division_id)

            if division is None:
                raise ResourceNotFoundError("Division not found.")

            if organization_id is not None and (
                division.organization_id != organization_id
            ):
                raise BusinessRuleError(
                    "Division does not belong to the organization."
                )

            if period_id is not None and division.period_id != period_id:
                raise BusinessRuleError(
                    "Division does not belong to the specified period."
                )

        return self.repository.get_all(
            organization_id=organization_id,
            period_id=period_id,
            division_id=division_id,
        )

    def update(
        self,
        program_id: int,
        name: str,
        description: str | None,
        status: str,
    ):
        name = name.strip()

        if not name:
            raise BusinessRuleError("Program name cannot be empty.")

        program = self.repository.update(
            program_id=program_id,
            name=name,
            description=description,
            status=status,
        )

        if program is None:
            raise ResourceNotFoundError("Program not found.")

        return program

    def delete(self, program_id: int):
        if not self.repository.delete(program_id):
            raise ResourceNotFoundError("Program not found.")

        return True

    def _validate_organization(self, organization_id: int):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise ResourceNotFoundError("Organization not found.")

    def _validate_context(
        self,
        organization_id: int,
        period_id: int,
        division_id: int,
    ):
        self._validate_organization(organization_id)

        period = self.period_repository.get_by_id(period_id)

        if period is None:
            raise ResourceNotFoundError("Period not found.")

        division = self.division_repository.get_by_id(division_id)

        if division is None:
            raise ResourceNotFoundError("Division not found.")

        if period.organization_id != organization_id:
            raise BusinessRuleError(
                "Period does not belong to the organization."
            )

        if division.organization_id != organization_id:
            raise BusinessRuleError(
                "Division does not belong to the organization."
            )

        if division.period_id != period_id:
            raise BusinessRuleError(
                "Division does not belong to the specified period."
            )