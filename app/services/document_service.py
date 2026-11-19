from app.repositories.document_repository import DocumentRepository
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.period_repository import PeriodRepository
from app.repositories.division_repository import DivisionRepository
from app.repositories.program_repository import ProgramRepository

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class DocumentService:
    def __init__(self, db):
        self.repository = DocumentRepository(db)
        self.organization_repository = OrganizationRepository(db)
        self.period_repository = PeriodRepository(db)
        self.division_repository = DivisionRepository(db)
        self.program_repository = ProgramRepository(db)

    def create(
        self,
        organization_id: int,
        title: str,
        document_type: str,
        period_id: int | None = None,
        program_id: int | None = None,
        division_id: int | None = None,
    ):
        title = title.strip()

        if not title:
            raise BusinessRuleError("Document title cannot be empty.")

        self._validate_context(
            organization_id=organization_id,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
        )

        return self.repository.create(
            organization_id=organization_id,
            title=title,
            document_type=document_type,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
        )

    def get_by_id(self, document_id: int):
        document = self.repository.get_by_id(document_id)

        if document is None:
            raise ResourceNotFoundError("Document not found.")

        return document

    def get_all(
        self,
        organization_id=None,
        period_id=None,
        program_id=None,
        division_id=None,
    ):
        if organization_id is not None:
            self._validate_organization(organization_id)

        if period_id is not None:
            self._validate_period(period_id, organization_id)

        if division_id is not None:
            self._validate_division(
                division_id,
                organization_id,
                period_id,
            )

        if program_id is not None:
            self._validate_program(
                program_id,
                organization_id,
                period_id,
                division_id,
            )

        return self.repository.get_all(
            organization_id=organization_id,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
        )

    def update(
        self,
        document_id: int,
        title: str,
        document_type: str,
        period_id: int | None = None,
        program_id: int | None = None,
        division_id: int | None = None,
    ):
        title = title.strip()

        if not title:
            raise BusinessRuleError("Document title cannot be empty.")

        document = self.repository.get_by_id(document_id)

        if document is None:
            raise ResourceNotFoundError("Document not found.")

        self._validate_context(
            organization_id=document.organization_id,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
        )

        return self.repository.update(
            document_id=document_id,
            title=title,
            document_type=document_type,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
        )

    def delete(self, document_id: int):
        if not self.repository.delete(document_id):
            raise ResourceNotFoundError("Document not found.")

        return True

    def _validate_context(
        self,
        organization_id,
        period_id,
        program_id,
        division_id,
    ):
        # Validate organization
        self._validate_organization(organization_id)

        # Validate period independently, even if no division/program is provided
        if period_id is not None:
            self._validate_period(
                period_id,
                organization_id,
            )

        # Validate division context
        if division_id is not None:
            if period_id is None:
                raise BusinessRuleError(
                    "A division requires a period context."
                )

            self._validate_division(
                division_id,
                organization_id,
                period_id,
            )

        # Validate program context
        if program_id is not None:
            if period_id is None:
                raise BusinessRuleError(
                    "A program requires a period context."
                )

            program = self._validate_program(
                program_id,
                organization_id,
                period_id,
                division_id,
            )

            if (
                division_id is not None
                and program.division_id != division_id
            ):
                raise BusinessRuleError(
                    "Program does not belong to the specified division."
                )

    def _validate_organization(self, organization_id):
        organization = self.organization_repository.get_by_id(
            organization_id
        )

        if organization is None:
            raise ResourceNotFoundError("Organization not found.")

        return organization

    def _validate_period(self, period_id, organization_id=None):
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

        return period

    def _validate_division(
        self,
        division_id,
        organization_id=None,
        period_id=None,
    ):
        division = self.division_repository.get_by_id(division_id)

        if division is None:
            raise ResourceNotFoundError("Division not found.")

        if (
            organization_id is not None
            and division.organization_id != organization_id
        ):
            raise BusinessRuleError(
                "Division does not belong to the organization."
            )

        if (
            period_id is not None
            and division.period_id != period_id
        ):
            raise BusinessRuleError(
                "Division does not belong to the specified period."
            )

        return division

    def _validate_program(
        self,
        program_id,
        organization_id=None,
        period_id=None,
        division_id=None,
    ):
        program = self.program_repository.get_by_id(program_id)

        if program is None:
            raise ResourceNotFoundError("Program not found.")

        if (
            organization_id is not None
            and program.organization_id != organization_id
        ):
            raise BusinessRuleError(
                "Program does not belong to the organization."
            )

        if (
            period_id is not None
            and program.period_id != period_id
        ):
            raise BusinessRuleError(
                "Program does not belong to the specified period."
            )

        if (
            division_id is not None
            and program.division_id != division_id
        ):
            raise BusinessRuleError(
                "Program does not belong to the specified division."
            )

        return program