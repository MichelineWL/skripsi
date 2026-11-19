import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db


@pytest.fixture
def api_client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def organization_id(api_client):
    response = api_client.post(
        "/organizations/",
        json={"name": "Test Organization"},
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture
def period_id(api_client, organization_id):
    response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "2025-2026",
            "start_date": "2025-07-01",
            "end_date": "2026-06-30",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture
def division_id(api_client, organization_id, period_id):
    response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Research Division",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture
def program_id(
    api_client,
    organization_id,
    period_id,
    division_id,
):
    response = api_client.post(
        "/programs/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": division_id,
            "name": "Research Program",
            "status": "planned",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.fixture
def document_id(
    api_client,
    organization_id,
    period_id,
    division_id,
    program_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": division_id,
            "program_id": program_id,
            "title": "Research Report",
            "document_type": "report",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_document(api_client, organization_id):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "title": "Meeting Minutes",
            "document_type": "minutes",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Meeting Minutes"
    assert data["document_type"] == "minutes"
    assert data["organization_id"] == organization_id
    assert data["period_id"] is None
    assert data["program_id"] is None
    assert data["division_id"] is None


def test_create_document_with_context(
    api_client,
    organization_id,
    period_id,
    division_id,
    program_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": division_id,
            "program_id": program_id,
            "title": "Program Report",
            "document_type": "report",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["organization_id"] == organization_id
    assert data["period_id"] == period_id
    assert data["division_id"] == division_id
    assert data["program_id"] == program_id


def test_get_documents(api_client, document_id):
    response = api_client.get("/documents/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == document_id


def test_filter_documents_by_organization(
    api_client,
    organization_id,
    document_id,
):
    response = api_client.get(
        "/documents/",
        params={"organization_id": organization_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == document_id


def test_filter_documents_by_period(
    api_client,
    period_id,
    document_id,
):
    response = api_client.get(
        "/documents/",
        params={"period_id": period_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == document_id


def test_filter_documents_by_program(
    api_client,
    program_id,
    document_id,
):
    response = api_client.get(
        "/documents/",
        params={"program_id": program_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == document_id


def test_filter_documents_by_division(
    api_client,
    division_id,
    document_id,
):
    response = api_client.get(
        "/documents/",
        params={"division_id": division_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == document_id


def test_filter_documents_by_full_context(
    api_client,
    organization_id,
    period_id,
    division_id,
    program_id,
    document_id,
):
    response = api_client.get(
        "/documents/",
        params={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": division_id,
            "program_id": program_id,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == document_id


def test_filter_documents_nonexistent_organization(
    api_client,
):
    response = api_client.get(
        "/documents/",
        params={"organization_id": 999},
    )

    assert response.status_code == 404


def test_filter_documents_nonexistent_period(
    api_client,
):
    response = api_client.get(
        "/documents/",
        params={"period_id": 999},
    )

    assert response.status_code == 404


def test_get_document_by_id(
    api_client,
    document_id,
):
    response = api_client.get(
        f"/documents/{document_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_update_document(
    api_client,
    document_id,
    period_id,
    division_id,
    program_id,
):
    response = api_client.put(
        f"/documents/{document_id}",
        json={
            "title": "Updated Report",
            "document_type": "final_report",
            "period_id": period_id,
            "division_id": division_id,
            "program_id": program_id,
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated Report"
    assert data["document_type"] == "final_report"
    assert data["period_id"] == period_id
    assert data["division_id"] == division_id
    assert data["program_id"] == program_id


def test_update_document_remove_context(
    api_client,
    document_id,
):
    response = api_client.put(
        f"/documents/{document_id}",
        json={
            "title": "Standalone Document",
            "document_type": "general",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["period_id"] is None
    assert data["program_id"] is None
    assert data["division_id"] is None


def test_delete_document(
    api_client,
    document_id,
):
    response = api_client.delete(
        f"/documents/{document_id}",
    )

    assert response.status_code == 204

    get_response = api_client.get(
        f"/documents/{document_id}",
    )
    assert get_response.status_code == 404


def test_create_document_nonexistent_organization(
    api_client,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": 999,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 404


def test_create_document_nonexistent_period(
    api_client,
    organization_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": 999,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 404


def test_create_document_period_wrong_organization(
    api_client,
    organization_id,
    period_id,
):
    second_org = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    second_org_id = second_org.json()["id"]

    response = api_client.post(
        "/documents/",
        json={
            "organization_id": second_org_id,
            "period_id": period_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_division_without_period(
    api_client,
    organization_id,
    division_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "division_id": division_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_nonexistent_division(
    api_client,
    organization_id,
    period_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": 999,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 404


def test_create_document_division_wrong_period(
    api_client,
    organization_id,
    period_id,
    division_id,
):
    second_period = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "2026-2027",
        },
    )
    second_period_id = second_period.json()["id"]

    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": second_period_id,
            "division_id": division_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_nonexistent_program(
    api_client,
    organization_id,
    period_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "program_id": 999,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 404


def test_create_document_program_without_period(
    api_client,
    organization_id,
    program_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "program_id": program_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_program_wrong_organization(
    api_client,
    organization_id,
    period_id,
    program_id,
):
    second_org = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    second_org_id = second_org.json()["id"]

    response = api_client.post(
        "/documents/",
        json={
            "organization_id": second_org_id,
            "period_id": period_id,
            "program_id": program_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_program_wrong_period(
    api_client,
    organization_id,
    program_id,
):
    second_period = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "2026-2027",
        },
    )
    second_period_id = second_period.json()["id"]

    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": second_period_id,
            "program_id": program_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_program_wrong_division(
    api_client,
    organization_id,
    period_id,
    program_id,
    division_id,
):
    second_division = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Second Division",
        },
    )
    second_division_id = second_division.json()["id"]

    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": second_division_id,
            "program_id": program_id,
            "title": "Invalid Document",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_create_document_empty_title(
    api_client,
    organization_id,
):
    response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "title": "   ",
            "document_type": "report",
        },
    )

    assert response.status_code == 400


def test_get_nonexistent_document(
    api_client,
):
    response = api_client.get(
        "/documents/999",
    )

    assert response.status_code == 404


def test_delete_nonexistent_document(
    api_client,
):
    response = api_client.delete(
        "/documents/999",
    )

    assert response.status_code == 404