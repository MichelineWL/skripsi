
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
            "start_date": "2025-08-01",
            "end_date": "2026-07-31",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_create_division(api_client, organization_id, period_id):
    response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Research Division",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Research Division"
    assert data["organization_id"] == organization_id
    assert data["period_id"] == period_id


def test_get_divisions(api_client, organization_id, period_id):
    api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Division A",
        },
    )
    api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Division B",
        },
    )

    response = api_client.get("/divisions/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_divisions_by_organization_and_period(
    api_client,
    organization_id,
    period_id,
):
    api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Division A",
        },
    )

    response = api_client.get(
        "/divisions/",
        params={
            "organization_id": organization_id,
            "period_id": period_id,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Division A"


def test_filter_divisions_by_nonexistent_organization(api_client):
    response = api_client.get(
        "/divisions/",
        params={"organization_id": 999},
    )

    assert response.status_code == 404


def test_filter_divisions_with_mismatched_context(
    api_client,
    organization_id,
    period_id,
):
    second_org_response = api_client.post(
        "/organizations/",
        json={"name": "Organization B"},
    )
    second_org_id = second_org_response.json()["id"]

    response = api_client.get(
        "/divisions/",
        params={
            "organization_id": second_org_id,
            "period_id": period_id,
        },
    )

    assert response.status_code == 400


def test_get_division_by_id(api_client, organization_id, period_id):
    create_response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Division A",
        },
    )
    division_id = create_response.json()["id"]

    response = api_client.get(f"/divisions/{division_id}")

    assert response.status_code == 200
    assert response.json()["id"] == division_id
    assert response.json()["name"] == "Division A"


def test_update_division(api_client, organization_id, period_id):
    create_response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Division A",
        },
    )
    division_id = create_response.json()["id"]

    response = api_client.put(
        f"/divisions/{division_id}",
        json={"name": "Division Updated"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Division Updated"


def test_delete_division(api_client, organization_id, period_id):
    create_response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "Division A",
        },
    )
    division_id = create_response.json()["id"]

    response = api_client.delete(f"/divisions/{division_id}")
    get_response = api_client.get(f"/divisions/{division_id}")

    assert response.status_code == 204
    assert get_response.status_code == 404


def test_create_division_nonexistent_organization(api_client, period_id):
    response = api_client.post(
        "/divisions/",
        json={
            "organization_id": 999,
            "period_id": period_id,
            "name": "Division A",
        },
    )

    assert response.status_code == 404


def test_create_division_nonexistent_period(
    api_client,
    organization_id,
):
    response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": 999,
            "name": "Division A",
        },
    )

    assert response.status_code == 404


def test_create_division_period_wrong_organization(
    api_client,
    period_id,
):
    second_org_response = api_client.post(
        "/organizations/",
        json={"name": "Organization B"},
    )
    second_org_id = second_org_response.json()["id"]

    response = api_client.post(
        "/divisions/",
        json={
            "organization_id": second_org_id,
            "period_id": period_id,
            "name": "Division A",
        },
    )

    assert response.status_code == 400


def test_create_division_empty_name(
    api_client,
    organization_id,
    period_id,
):
    response = api_client.post(
        "/divisions/",
        json={
            "organization_id": organization_id,
            "period_id": period_id,
            "name": "   ",
        },
    )

    assert response.status_code == 400


def test_get_nonexistent_division(api_client):
    response = api_client.get("/divisions/999")

    assert response.status_code == 404


def test_delete_nonexistent_division(api_client):
    response = api_client.delete("/divisions/999")

    assert response.status_code == 404
