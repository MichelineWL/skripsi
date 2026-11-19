from datetime import date

from app.models.organization import Organization

from app.repositories.period_repository import PeriodRepository
from app.repositories.division_repository import DivisionRepository
from app.repositories.program_repository import ProgramRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.document_version_repository import (
    DocumentVersionRepository,
)


# =========================================================
# Helpers
# =========================================================

def create_organization(db_session):
    organization = Organization(name="Test Organization")
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    return organization


def create_period(db_session, organization_id):
    return PeriodRepository(db_session).create(
        organization_id=organization_id,
        name="2025/2026",
        start_date=date(2025, 7, 1),
        end_date=date(2026, 6, 30),
    )


def create_division(db_session, organization_id, period_id):
    return DivisionRepository(db_session).create(
        organization_id=organization_id,
        period_id=period_id,
        name="Research Division",
    )


def create_program(
    db_session,
    organization_id,
    period_id,
    division_id,
):
    return ProgramRepository(db_session).create(
        organization_id=organization_id,
        period_id=period_id,
        division_id=division_id,
        name="Research Festival",
        description="Annual research event",
        status="planned",
    )


def create_document(
    db_session,
    organization_id,
    period_id=None,
    program_id=None,
    division_id=None,
):
    return DocumentRepository(db_session).create(
        organization_id=organization_id,
        period_id=period_id,
        program_id=program_id,
        division_id=division_id,
        title="Research Festival Proposal",
        document_type="proposal",
    )


# =========================================================
# Period Repository
# =========================================================

def test_period_create(db_session):
    organization = create_organization(db_session)

    repository = PeriodRepository(db_session)

    period = repository.create(
        organization_id=organization.id,
        name="2025/2026",
        start_date=date(2025, 7, 1),
        end_date=date(2026, 6, 30),
    )

    assert period.id is not None
    assert period.organization_id == organization.id
    assert period.name == "2025/2026"


def test_period_get_by_id(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)

    result = PeriodRepository(db_session).get_by_id(period.id)

    assert result is not None
    assert result.id == period.id


def test_period_get_by_id_not_found(db_session):
    result = PeriodRepository(db_session).get_by_id(999)

    assert result is None


def test_period_get_all_filter_by_organization(db_session):
    organization_1 = create_organization(db_session)

    organization_2 = Organization(name="Another Organization")
    db_session.add(organization_2)
    db_session.commit()

    create_period(db_session, organization_1.id)

    PeriodRepository(db_session).create(
        organization_id=organization_2.id,
        name="2024/2025",
    )

    result = PeriodRepository(db_session).get_all(
        organization_id=organization_1.id
    )

    assert len(result) == 1
    assert result[0].organization_id == organization_1.id


def test_period_update(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)

    result = PeriodRepository(db_session).update(
        period_id=period.id,
        name="2026/2027",
        start_date=date(2026, 7, 1),
        end_date=date(2027, 6, 30),
    )

    assert result.name == "2026/2027"


def test_period_delete(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)

    result = PeriodRepository(db_session).delete(period.id)

    assert result is True
    assert PeriodRepository(db_session).get_by_id(period.id) is None


# =========================================================
# Division Repository
# =========================================================

def test_division_create(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)

    division = DivisionRepository(db_session).create(
        organization_id=organization.id,
        period_id=period.id,
        name="Research Division",
    )

    assert division.id is not None
    assert division.organization_id == organization.id
    assert division.period_id == period.id


def test_division_get_by_id(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )

    result = DivisionRepository(db_session).get_by_id(division.id)

    assert result is not None
    assert result.id == division.id


def test_division_get_by_id_not_found(db_session):
    result = DivisionRepository(db_session).get_by_id(999)

    assert result is None


def test_division_get_all_filter_by_period(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)

    create_division(db_session, organization.id, period.id)

    result = DivisionRepository(db_session).get_all(
        period_id=period.id
    )

    assert len(result) == 1
    assert result[0].period_id == period.id


def test_division_update(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )

    result = DivisionRepository(db_session).update(
        division_id=division.id,
        name="Updated Division",
    )

    assert result.name == "Updated Division"


def test_division_delete(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )

    result = DivisionRepository(db_session).delete(division.id)

    assert result is True
    assert DivisionRepository(db_session).get_by_id(division.id) is None


# =========================================================
# Program Repository
# =========================================================

def test_program_create(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )

    program = create_program(
        db_session,
        organization.id,
        period.id,
        division.id,
    )

    assert program.id is not None
    assert program.name == "Research Festival"
    assert program.status == "planned"


def test_program_get_by_id(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )
    program = create_program(
        db_session,
        organization.id,
        period.id,
        division.id,
    )

    result = ProgramRepository(db_session).get_by_id(program.id)

    assert result is not None
    assert result.id == program.id


def test_program_get_by_id_not_found(db_session):
    result = ProgramRepository(db_session).get_by_id(999)

    assert result is None


def test_program_get_all_filter_by_division(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )

    create_program(
        db_session,
        organization.id,
        period.id,
        division.id,
    )

    result = ProgramRepository(db_session).get_all(
        division_id=division.id
    )

    assert len(result) == 1
    assert result[0].division_id == division.id


def test_program_update(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )
    program = create_program(
        db_session,
        organization.id,
        period.id,
        division.id,
    )

    result = ProgramRepository(db_session).update(
        program_id=program.id,
        name="Updated Program",
        description="Updated description",
        status="completed",
    )

    assert result.name == "Updated Program"
    assert result.status == "completed"


def test_program_delete(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )
    program = create_program(
        db_session,
        organization.id,
        period.id,
        division.id,
    )

    result = ProgramRepository(db_session).delete(program.id)

    assert result is True
    assert ProgramRepository(db_session).get_by_id(program.id) is None

# =========================================================
# Document Repository
# =========================================================

def test_document_create(db_session):
    organization = create_organization(db_session)
    period = create_period(db_session, organization.id)
    division = create_division(
        db_session,
        organization.id,
        period.id,
    )
    program = create_program(
        db_session,
        organization.id,
        period.id,
        division.id,
    )

    document = create_document(
        db_session,
        organization.id,
        period.id,
        program.id,
        division.id,
    )

    assert document.id is not None
    assert document.title == "Research Festival Proposal"
    assert document.program_id == program.id


def test_document_get_by_id(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    result = DocumentRepository(db_session).get_by_id(document.id)

    assert result is not None
    assert result.id == document.id


def test_document_get_by_id_not_found(db_session):
    result = DocumentRepository(db_session).get_by_id(999)

    assert result is None


def test_document_get_all_filter_by_organization(db_session):
    organization = create_organization(db_session)

    create_document(
        db_session,
        organization.id,
    )

    result = DocumentRepository(db_session).get_all(
        organization_id=organization.id
    )

    assert len(result) == 1
    assert result[0].organization_id == organization.id


def test_document_update(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    result = DocumentRepository(db_session).update(
        document_id=document.id,
        title="Updated Document",
        document_type="report",
    )

    assert result.title == "Updated Document"
    assert result.document_type == "report"


def test_document_delete(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    result = DocumentRepository(db_session).delete(document.id)

    assert result is True
    assert DocumentRepository(db_session).get_by_id(document.id) is None


# =========================================================
# Document Version Repository
# =========================================================

def test_document_version_create(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    version = DocumentVersionRepository(db_session).create(
        document_id=document.id,
        version_number=1,
        file_path="storage/documents/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    assert version.id is not None
    assert version.document_id == document.id
    assert version.version_number == 1
    assert version.processing_status == "uploaded"


def test_document_version_get_by_id(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    version = DocumentVersionRepository(db_session).create(
        document_id=document.id,
        version_number=1,
        file_path="storage/documents/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    result = DocumentVersionRepository(db_session).get_by_id(
        version.id
    )

    assert result is not None
    assert result.id == version.id


def test_document_version_get_by_id_not_found(db_session):
    result = DocumentVersionRepository(db_session).get_by_id(999)

    assert result is None


def test_document_version_get_all_by_document(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    repository = DocumentVersionRepository(db_session)

    repository.create(
        document_id=document.id,
        version_number=1,
        file_path="storage/documents/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    repository.create(
        document_id=document.id,
        version_number=2,
        file_path="storage/documents/proposal_v2.pdf",
        file_hash="hash_v2",
    )

    result = repository.get_all(document_id=document.id)

    assert len(result) == 2
    assert result[0].version_number == 1
    assert result[1].version_number == 2


def test_document_version_get_latest(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    repository = DocumentVersionRepository(db_session)

    repository.create(
        document_id=document.id,
        version_number=1,
        file_path="storage/documents/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    repository.create(
        document_id=document.id,
        version_number=2,
        file_path="storage/documents/proposal_v2.pdf",
        file_hash="hash_v2",
    )

    latest = repository.get_latest(document.id)

    assert latest is not None
    assert latest.version_number == 2


def test_document_version_update_processing_status(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    repository = DocumentVersionRepository(db_session)

    version = repository.create(
        document_id=document.id,
        version_number=1,
        file_path="storage/documents/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    result = repository.update_processing_status(
        document_version_id=version.id,
        processing_status="processed",
    )

    assert result.processing_status == "processed"


def test_document_version_delete(db_session):
    organization = create_organization(db_session)
    document = create_document(
        db_session,
        organization.id,
    )

    repository = DocumentVersionRepository(db_session)

    version = repository.create(
        document_id=document.id,
        version_number=1,
        file_path="storage/documents/proposal_v1.pdf",
        file_hash="hash_v1",
    )

    result = repository.delete(version.id)

    assert result is True
    assert repository.get_by_id(version.id) is None