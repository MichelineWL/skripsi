
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


def test_create_organization(api_client):
    response = api_client.post(
        "/organizations/",
        json={"name": "Organization A"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Organization A"
    assert "id" in response.json()


def test_get_organizations(api_client):
    api_client.post("/organizations/", json={"name": "Organization A"})
    api_client.post("/organizations/", json={"name": "Organization B"})

    response = api_client.get("/organizations/")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_organization_by_id(api_client):
    create_response = api_client.post(
        "/organizations/",
        json={"name": "Organization A"},
    )
    organization_id = create_response.json()["id"]

    response = api_client.get(
        f"/organizations/{organization_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == organization_id
    assert response.json()["name"] == "Organization A"


def test_update_organization(api_client):
    create_response = api_client.post(
        "/organizations/",
        json={"name": "Organization A"},
    )
    organization_id = create_response.json()["id"]

    response = api_client.put(
        f"/organizations/{organization_id}",
        json={"name": "Organization Updated"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Organization Updated"


def test_delete_organization(api_client):
    create_response = api_client.post(
        "/organizations/",
        json={"name": "Organization A"},
    )
    organization_id = create_response.json()["id"]

    response = api_client.delete(
        f"/organizations/{organization_id}"
    )

    assert response.status_code == 204

    get_response = api_client.get(
        f"/organizations/{organization_id}"
    )

    assert get_response.status_code == 404


def test_get_nonexistent_organization(api_client):
    response = api_client.get("/organizations/999")

    assert response.status_code == 404


def test_create_organization_empty_name(api_client):
    response = api_client.post(
        "/organizations/",
        json={"name": "   "},
    )

    assert response.status_code == 400


def test_create_organization_missing_name(api_client):
    response = api_client.post(
        "/organizations/",
        json={},
    )

    assert response.status_code == 422
