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
def document_id(api_client):
    organization_response = api_client.post(
        "/organizations/",
        json={"name": "Test Organization"},
    )
    assert organization_response.status_code == 201

    organization_id = organization_response.json()["id"]

    document_response = api_client.post(
        "/documents/",
        json={
            "organization_id": organization_id,
            "title": "Test Document",
            "document_type": "report",
        },
    )
    assert document_response.status_code == 201

    return document_response.json()["id"]


def create_version(
    api_client,
    document_id,
    file_path="uploads/report.pdf",
    file_hash="hash-001",
):
    return api_client.post(
        f"/documents/{document_id}/versions",
        json={
            "file_path": file_path,
            "file_hash": file_hash,
        },
    )


def test_create_document_version(api_client, document_id):
    response = create_version(
        api_client,
        document_id,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["document_id"] == document_id
    assert data["version_number"] == 1
    assert data["file_path"] == "uploads/report.pdf"
    assert data["file_hash"] == "hash-001"
    assert data["processing_status"] == "uploaded"


def test_create_sequential_document_versions(
    api_client,
    document_id,
):
    first_response = create_version(
        api_client,
        document_id,
        file_hash="hash-001",
    )
    second_response = create_version(
        api_client,
        document_id,
        file_path="uploads/report-v2.pdf",
        file_hash="hash-002",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    assert first_response.json()["version_number"] == 1
    assert second_response.json()["version_number"] == 2


def test_create_document_version_nonexistent_document(
    api_client,
):
    response = create_version(
        api_client,
        document_id=999,
    )

    assert response.status_code == 404


def test_create_duplicate_document_version_hash(
    api_client,
    document_id,
):
    first_response = create_version(
        api_client,
        document_id,
        file_hash="duplicate-hash",
    )
    second_response = create_version(
        api_client,
        document_id,
        file_path="uploads/another-file.pdf",
        file_hash="duplicate-hash",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


def test_get_document_versions(
    api_client,
    document_id,
):
    first_response = create_version(
        api_client,
        document_id,
        file_hash="hash-001",
    )
    second_response = create_version(
        api_client,
        document_id,
        file_path="uploads/report-v2.pdf",
        file_hash="hash-002",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = api_client.get(
        f"/documents/{document_id}/versions",
    )

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["version_number"] == 1
    assert data[1]["version_number"] == 2


def test_get_document_versions_empty(
    api_client,
    document_id,
):
    response = api_client.get(
        f"/documents/{document_id}/versions",
    )

    assert response.status_code == 200
    assert response.json() == []


def test_get_document_versions_nonexistent_document(
    api_client,
):
    response = api_client.get(
        "/documents/999/versions",
    )

    assert response.status_code == 404


def test_get_document_version_by_id(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    response = api_client.get(
        f"/documents/{document_id}/versions/{version_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == version_id
    assert response.json()["document_id"] == document_id


def test_get_latest_document_version(
    api_client,
    document_id,
):
    first_response = create_version(
        api_client,
        document_id,
        file_hash="hash-001",
    )
    second_response = create_version(
        api_client,
        document_id,
        file_path="uploads/report-v2.pdf",
        file_hash="hash-002",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = api_client.get(
        f"/documents/{document_id}/versions/latest",
    )

    assert response.status_code == 200
    assert response.json()["version_number"] == 2
    assert response.json()["file_hash"] == "hash-002"


def test_get_latest_document_version_when_empty(
    api_client,
    document_id,
):
    response = api_client.get(
        f"/documents/{document_id}/versions/latest",
    )

    assert response.status_code == 404


def test_get_nonexistent_document_version(
    api_client,
    document_id,
):
    response = api_client.get(
        f"/documents/{document_id}/versions/999",
    )

    assert response.status_code == 404


def test_get_version_from_wrong_document(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    second_organization_response = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    assert second_organization_response.status_code == 201

    second_document_response = api_client.post(
        "/documents/",
        json={
            "organization_id": (
                second_organization_response.json()["id"]
            ),
            "title": "Second Document",
            "document_type": "report",
        },
    )
    assert second_document_response.status_code == 201

    second_document_id = second_document_response.json()["id"]

    response = api_client.get(
        f"/documents/{second_document_id}/versions/{version_id}",
    )

    assert response.status_code == 404


def test_update_document_version_processing_status(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    response = api_client.put(
        f"/documents/{document_id}/versions/{version_id}/status",
        json={"processing_status": "processed"},
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "processed"


def test_update_document_version_empty_status(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    response = api_client.put(
        f"/documents/{document_id}/versions/{version_id}/status",
        json={"processing_status": "   "},
    )

    assert response.status_code == 400


def test_update_document_version_wrong_document(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    second_organization_response = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    assert second_organization_response.status_code == 201

    second_document_response = api_client.post(
        "/documents/",
        json={
            "organization_id": (
                second_organization_response.json()["id"]
            ),
            "title": "Second Document",
            "document_type": "report",
        },
    )
    assert second_document_response.status_code == 201

    second_document_id = second_document_response.json()["id"]

    response = api_client.put(
        f"/documents/{second_document_id}/versions/{version_id}/status",
        json={"processing_status": "processed"},
    )

    assert response.status_code == 404


def test_delete_document_version(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    delete_response = api_client.delete(
        f"/documents/{document_id}/versions/{version_id}",
    )

    assert delete_response.status_code == 204

    get_response = api_client.get(
        f"/documents/{document_id}/versions/{version_id}",
    )

    assert get_response.status_code == 404


def test_delete_document_version_wrong_document(
    api_client,
    document_id,
):
    create_response = create_version(
        api_client,
        document_id,
    )
    assert create_response.status_code == 201

    version_id = create_response.json()["id"]

    second_organization_response = api_client.post(
        "/organizations/",
        json={"name": "Second Organization"},
    )
    assert second_organization_response.status_code == 201

    second_document_response = api_client.post(
        "/documents/",
        json={
            "organization_id": (
                second_organization_response.json()["id"]
            ),
            "title": "Second Document",
            "document_type": "report",
        },
    )
    assert second_document_response.status_code == 201

    second_document_id = second_document_response.json()["id"]

    response = api_client.delete(
        f"/documents/{second_document_id}/versions/{version_id}",
    )

    assert response.status_code == 404

    verify_response = api_client.get(
        f"/documents/{document_id}/versions/{version_id}",
    )

    assert verify_response.status_code == 200


def test_delete_nonexistent_document_version(
    api_client,
    document_id,
):
    response = api_client.delete(
        f"/documents/{document_id}/versions/999",
    )

    assert response.status_code == 404