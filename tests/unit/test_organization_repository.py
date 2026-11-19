import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.organization import Organization
from app.repositories.organization_repository import OrganizationRepository


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def repository(db_session):
    return OrganizationRepository(db_session)


def test_create_organization(repository, db_session):
    organization = repository.create("Test Organization")

    assert organization.id is not None
    assert organization.name == "Test Organization"

    stored_organization = db_session.get(
        Organization,
        organization.id,
    )

    assert stored_organization is not None
    assert stored_organization.name == "Test Organization"


def test_get_organization_by_id(repository):
    created = repository.create("Test Organization")

    organization = repository.get_by_id(created.id)

    assert organization is not None
    assert organization.id == created.id
    assert organization.name == "Test Organization"


def test_get_organization_by_id_returns_none_when_not_found(repository):
    organization = repository.get_by_id(999)

    assert organization is None


def test_get_all_organizations(repository):
    repository.create("Organization A")
    repository.create("Organization B")

    organizations = repository.get_all()

    assert len(organizations) == 2
    assert [organization.name for organization in organizations] == [
        "Organization A",
        "Organization B",
    ]


def test_update_organization(repository):
    created = repository.create("Old Name")

    updated = repository.update(
        organization_id=created.id,
        name="New Name",
    )

    assert updated is not None
    assert updated.name == "New Name"


def test_update_organization_returns_none_when_not_found(repository):
    updated = repository.update(
        organization_id=999,
        name="New Name",
    )

    assert updated is None


def test_delete_organization(repository):
    created = repository.create("Test Organization")

    result = repository.delete(created.id)

    assert result is True
    assert repository.get_by_id(created.id) is None


def test_delete_organization_returns_false_when_not_found(repository):
    result = repository.delete(999)

    assert result is False