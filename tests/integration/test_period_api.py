
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


def test_create_period(api_client, organization_id):
    response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "2025-2026",
            "start_date": "2025-08-01",
            "end_date": "2026-07-31",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "2025-2026"
    assert data["organization_id"] == organization_id
    assert data["start_date"] == "2025-08-01"
    assert data["end_date"] == "2026-07-31"


def test_create_period_without_dates(api_client, organization_id):
    response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period Without Dates",
        },
    )

    assert response.status_code == 201
    assert response.json()["start_date"] is None
    assert response.json()["end_date"] is None


def test_get_periods(api_client, organization_id):
    api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period A",
        },
    )
    api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period B",
        },
    )

    response = api_client.get("/periods/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_periods_filtered_by_organization(
    api_client,
    organization_id,
):
    second_org = api_client.post(
        "/organizations/",
        json={"name": "Organization B"},
    ).json()

    api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period A",
        },
    )
    api_client.post(
        "/periods/",
        json={
            "organization_id": second_org["id"],
            "name": "Period B",
        },
    )

    response = api_client.get(
        "/periods/",
        params={"organization_id": organization_id},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Period A"


def test_get_period_by_id(api_client, organization_id):
    create_response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period A",
        },
    )

    period_id = create_response.json()["id"]

    response = api_client.get(f"/periods/{period_id}")

    assert response.status_code == 200
    assert response.json()["id"] == period_id


def test_update_period(api_client, organization_id):
    create_response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period A",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
        },
    )

    period_id = create_response.json()["id"]

    response = api_client.put(
        f"/periods/{period_id}",
        json={
            "name": "Period Updated",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Period Updated"
    assert response.json()["start_date"] == "2026-01-01"
    assert response.json()["end_date"] == "2026-12-31"


def test_delete_period(api_client, organization_id):
    create_response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Period A",
        },
    )

    period_id = create_response.json()["id"]

    response = api_client.delete(f"/periods/{period_id}")
    get_response = api_client.get(f"/periods/{period_id}")

    assert response.status_code == 204
    assert get_response.status_code == 404


def test_create_period_nonexistent_organization(api_client):
    response = api_client.post(
        "/periods/",
        json={
            "organization_id": 999,
            "name": "Period A",
        },
    )

    assert response.status_code == 404


def test_create_period_invalid_dates(api_client, organization_id):
    response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "Invalid Period",
            "start_date": "2026-12-31",
            "end_date": "2026-01-01",
        },
    )

    assert response.status_code == 400


def test_create_period_empty_name(api_client, organization_id):
    response = api_client.post(
        "/periods/",
        json={
            "organization_id": organization_id,
            "name": "   ",
        },
    )

    assert response.status_code == 400


def test_get_nonexistent_period(api_client):
    response = api_client.get("/periods/999")

    assert response.status_code == 404


def test_delete_nonexistent_period(api_client):
    response = api_client.delete("/periods/999")

    assert response.status_code == 404
