from datetime import date

import pytest

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)

from app.repositories.organization_repository import OrganizationRepository

from app.services.organization_service import OrganizationService
from app.services.period_service import PeriodService
from app.services.division_service import DivisionService
from app.services.program_service import ProgramService
from app.services.document_service import DocumentService
from app.services.document_version_service import DocumentVersionService


# =========================================================
# Shared helpers
# =========================================================

def setup_context(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    period = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2025/2026",
        start_date=date(2025, 7, 1),
        end_date=date(2026, 6, 30),
    )

    division = DivisionService(db_session).create(
        organization_id=organization.id,
        period_id=period.id,
        name="Research Division",
    )

    program = ProgramService(db_session).create(
        organization_id=organization.id,
        period_id=period.id,
        division_id=division.id,
        name="Research Festival",
        description="Annual event",
        status="planned",
    )

    return organization, period, division, program


# =========================================================
# Organization Service
# =========================================================

def test_organization_service_create(db_session):
    service = OrganizationService(db_session)

    organization = service.create("  Test Organization  ")

    assert organization.name == "Test Organization"


def test_organization_service_rejects_empty_name(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(ValueError):
        service.create("   ")


def test_organization_service_get_missing(db_session):
    service = OrganizationService(db_session)

    with pytest.raises(ResourceNotFoundError):
        service.get_by_id(999)


# =========================================================
# Period Service
# =========================================================

def test_period_service_create(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    period = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2025/2026",
    )

    assert period.organization_id == organization.id


def test_period_service_invalid_organization(db_session):
    service = PeriodService(db_session)

    with pytest.raises(ResourceNotFoundError):
        service.create(
            organization_id=999,
            name="2025/2026",
        )


def test_period_service_invalid_dates(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    with pytest.raises(BusinessRuleError):
        PeriodService(db_session).create(
            organization_id=organization.id,
            name="Invalid Period",
            start_date=date(2026, 6, 1),
            end_date=date(2025, 6, 1),
        )


def test_period_service_rejects_empty_name(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    with pytest.raises(BusinessRuleError):
        PeriodService(db_session).create(
            organization_id=organization.id,
            name="   ",
        )


# =========================================================
# Division Service
# =========================================================

def test_division_service_create(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    period = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2025/2026",
    )

    division = DivisionService(db_session).create(
        organization_id=organization.id,
        period_id=period.id,
        name="Research Division",
    )

    assert division.period_id == period.id


def test_division_service_wrong_organization_period(db_session):
    organization_1 = OrganizationRepository(db_session).create(
        "Organization 1"
    )

    organization_2 = OrganizationRepository(db_session).create(
        "Organization 2"
    )

    period_2 = PeriodService(db_session).create(
        organization_id=organization_2.id,
        name="2025/2026",
    )

    with pytest.raises(BusinessRuleError):
        DivisionService(db_session).create(
            organization_id=organization_1.id,
            period_id=period_2.id,
            name="Invalid Division",
        )


# =========================================================
# Program Service
# =========================================================

def test_program_service_create(db_session):
    _, _, _, program = setup_context(db_session)

    assert program.name == "Research Festival"


def test_program_service_wrong_division_period(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    period_1 = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2025/2026",
    )

    period_2 = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2026/2027",
    )

    division_2 = DivisionService(db_session).create(
        organization_id=organization.id,
        period_id=period_2.id,
        name="Division 2",
    )

    with pytest.raises(BusinessRuleError):
        ProgramService(db_session).create(
            organization_id=organization.id,
            period_id=period_1.id,
            division_id=division_2.id,
            name="Invalid Program",
        )


def test_program_service_missing_division(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    period = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2025/2026",
    )

    with pytest.raises(ResourceNotFoundError):
        ProgramService(db_session).create(
            organization_id=organization.id,
            period_id=period.id,
            division_id=999,
            name="Invalid Program",
        )


# =========================================================
# Document Service
# =========================================================

def test_document_service_create(db_session):
    organization, period, division, program = setup_context(db_session)

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Proposal",
        document_type="proposal",
        period_id=period.id,
        program_id=program.id,
        division_id=division.id,
    )

    assert document.organization_id == organization.id
    assert document.program_id == program.id


def test_document_service_general_document(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="General Guideline",
        document_type="guideline",
    )

    assert document.period_id is None
    assert document.program_id is None
    assert document.division_id is None


def test_document_service_division_without_period(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    with pytest.raises(BusinessRuleError):
        DocumentService(db_session).create(
            organization_id=organization.id,
            title="Invalid Document",
            document_type="report",
            division_id=1,
        )


def test_document_service_invalid_program_context(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    period_1 = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2025/2026",
    )

    period_2 = PeriodService(db_session).create(
        organization_id=organization.id,
        name="2026/2027",
    )

    division_2 = DivisionService(db_session).create(
        organization_id=organization.id,
        period_id=period_2.id,
        name="Division 2",
    )

    program_2 = ProgramService(db_session).create(
        organization_id=organization.id,
        period_id=period_2.id,
        division_id=division_2.id,
        name="Program 2",
    )

    with pytest.raises(BusinessRuleError):
        DocumentService(db_session).create(
            organization_id=organization.id,
            title="Invalid Document",
            document_type="proposal",
            period_id=period_1.id,
            program_id=program_2.id,
        )


# =========================================================
# Document Version Service
# =========================================================

def test_document_version_service_first_version(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Proposal",
        document_type="proposal",
    )

    version = DocumentVersionService(db_session).create(
        document_id=document.id,
        file_path="storage/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    assert version.version_number == 1


def test_document_version_service_sequential_versions(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Proposal",
        document_type="proposal",
    )

    service = DocumentVersionService(db_session)

    version_1 = service.create(
        document_id=document.id,
        file_path="storage/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    version_2 = service.create(
        document_id=document.id,
        file_path="storage/proposal_v2.pdf",
        file_hash="hash_v2",
    )

    assert version_1.version_number == 1
    assert version_2.version_number == 2


def test_document_version_duplicate_hash(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Proposal",
        document_type="proposal",
    )

    service = DocumentVersionService(db_session)

    service.create(
        document_id=document.id,
        file_path="storage/proposal_v1.pdf",
        file_hash="same_hash",
    )

    with pytest.raises(BusinessRuleError):
        service.create(
            document_id=document.id,
            file_path="storage/proposal_duplicate.pdf",
            file_hash="same_hash",
        )


def test_document_version_missing_document(db_session):
    service = DocumentVersionService(db_session)

    with pytest.raises(ResourceNotFoundError):
        service.create(
            document_id=999,
            file_path="storage/missing.pdf",
            file_hash="hash",
        )


def test_document_version_empty_hash(db_session):
    organization = OrganizationRepository(db_session).create(
        "Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Proposal",
        document_type="proposal",
    )

    with pytest.raises(BusinessRuleError):
        DocumentVersionService(db_session).create(
            document_id=document.id,
            file_path="storage/proposal.pdf",
            file_hash=" ",
        )