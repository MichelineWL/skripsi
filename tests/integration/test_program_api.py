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
            "description": "Test description",
            "status": "planned",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_program(
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
            "name": "New Program",
            "description": "Program description",
            "status": "planned",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "New Program"
    assert data["description"] == "Program description"
    assert data["status"] == "planned"
    assert data["organization_id"] == organization_id
    assert data["period_id"] == period_id
    assert data["division_id"] == division_id


def test_create_program_with_defaults(
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
            "name": "Default Program",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["description"] is None
    assert data["status"] == "planned"


def test_get_programs(
    api_client,
    program_id,
):
    response = api_client.get("/programs/")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == program_id


def test_filter_programs_by_context(
    api_client,
    organization_id,
    period_id,
    division_id,
    program_id,
):
    response = api_client.get(
        "/programs/",
        params={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": division_id,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == program_id


def test_filter_programs_by_nonexistent_organization(
    api_client,
):
    response = api_client.get(
        "/programs/",
        params={"organization_id": 999},
    )

    assert response.status_code == 404


def test_filter_programs_with_mismatched_context(
    api_client,
    organization_id,
    period_id,
):
    second_org = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    assert second_org.status_code == 201

    response = api_client.get(
        "/programs/",
        params={
            "organization_id": second_org.json()["id"],
            "period_id": period_id,
        },
    )

    assert response.status_code == 400


def test_get_program_by_id(
    api_client,
    program_id,
):
    response = api_client.get(
        f"/programs/{program_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == program_id


def test_update_program(
    api_client,
    program_id,
):
    response = api_client.put(
        f"/programs/{program_id}",
        json={
            "name": "Updated Program",
            "description": "Updated description",
            "status": "ongoing",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Program"
    assert data["description"] == "Updated description"
    assert data["status"] == "ongoing"


def test_delete_program(
    api_client,
    program_id,
):
    response = api_client.delete(
        f"/programs/{program_id}"
    )

    assert response.status_code == 204

    get_response = api_client.get(
        f"/programs/{program_id}"
    )
    assert get_response.status_code == 404


def test_create_program_nonexistent_organization(
    api_client,
    period_id,
    division_id,
):
    response = api_client.post(
        "/programs/",
        json={
            "organization_id": 999,
            "period_id": period_id,
            "division_id": division_id,
            "name": "Invalid Program",
        },
    )

    assert response.status_code == 404


def test_create_program_nonexistent_period(
    api_client,
    organization_id,
    division_id,
):
    response = api_client.post(
        "/programs/",
        json={
            "organization_id": organization_id,
            "period_id": 999,
            "division_id": division_id,
            "name": "Invalid Program",
        },
    )

    assert response.status_code == 404


def test_create_program_nonexistent_division(
    api_client,
    organization_id,
    period_id,
):
    response = api_client.post(
        "/programs/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "division_id": 999,
            "name": "Invalid Program",
        },
    )

    assert response.status_code == 404


def test_create_program_division_wrong_organization(
    api_client,
    organization_id,
    period_id,
    division_id,
):
    second_org = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    second_org_id = second_org.json()["id"]

    response = api_client.post(
        "/programs/",
        json={
            "organization_id": second_org_id,
            "period_id": period_id,
            "division_id": division_id,
            "name": "Invalid Program",
        },
    )

    assert response.status_code == 400


def test_create_program_division_wrong_period(
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
        "/programs/",
        json={
            "organization_id": organization_id,
            "period_id": second_period_id,
            "division_id": division_id,
            "name": "Invalid Program",
        },
    )

    assert response.status_code == 400


def test_create_program_empty_name(
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
            "name": "   ",
        },
    )

    assert response.status_code == 400


def test_get_nonexistent_program(
    api_client,
):
    response = api_client.get(
        "/programs/999"
    )

    assert response.status_code == 404


def test_delete_nonexistent_program(
    api_client,
):
    response = api_client.delete(
        "/programs/999"
    )

    assert response.status_code == 404