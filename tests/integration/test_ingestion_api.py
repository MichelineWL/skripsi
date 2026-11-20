import hashlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.dependencies import get_ingestion_service
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.services.document_service import DocumentService
from app.services.document_version_service import (
    DocumentVersionService,
)


class FakeIngestionService:
    def __init__(self):
        self.calls = []

    def ingest_extracted_content(
        self,
        extracted_content_id,
    ):
        self.calls.append(extracted_content_id)

        return {
            "extracted_content_id": extracted_content_id,
            "chunk_count": 3,
            "vector_count": 3,
            "status": "completed",
            "cleanup_warning": None,
        }


@pytest.fixture
def ingestion_api_service():
    return FakeIngestionService()


@pytest.fixture
def ingestion_client(
    db_session,
    ingestion_api_service,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[
        get_ingestion_service
    ] = lambda: ingestion_api_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def calculate_hash(file_path):
    return hashlib.sha256(
        file_path.read_bytes()
    ).hexdigest()


@pytest.fixture
def ingestion_context(db_session, tmp_path):
    organization = OrganizationRepository(db_session).create(
        "Ingestion Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Test Document",
        document_type="guideline",
    )

    file_path = tmp_path / "guideline.txt"

    file_path.write_text(
        "This is test content for ingestion.",
        encoding="utf-8",
    )

    version = DocumentVersionService(db_session).create(
        document_id=document.id,
        file_path=str(file_path),
        file_hash=calculate_hash(file_path),
    )

    return {
        "organization": organization,
        "document": document,
        "version": version,
        "file_path": file_path,
    }


def create_extracted_content(
    client,
    document,
    version,
):
    response = client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    assert response.status_code == 200

    return response.json()


def test_ingest_extracted_content_success(
    ingestion_client,
    ingestion_context,
    ingestion_api_service,
):
    document = ingestion_context["document"]
    version = ingestion_context["version"]

    extracted_content = create_extracted_content(
        ingestion_client,
        document,
        version,
    )

    response = ingestion_client.post(
        f"/documents/{document.id}/versions/{version.id}"
        f"/extracted-contents/{extracted_content['id']}/ingest"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["extracted_content_id"] == extracted_content["id"]
    assert data["chunk_count"] == 3
    assert data["vector_count"] == 3
    assert data["status"] == "completed"
    assert data["cleanup_warning"] is None

    assert ingestion_api_service.calls == [
        extracted_content["id"]
    ]


def test_ingest_wrong_document_returns_404(
    ingestion_client,
    ingestion_context,
):
    document = ingestion_context["document"]
    version = ingestion_context["version"]

    extracted_content = create_extracted_content(
        ingestion_client,
        document,
        version,
    )

    response = ingestion_client.post(
        f"/documents/999/versions/{version.id}"
        f"/extracted-contents/{extracted_content['id']}/ingest"
    )

    assert response.status_code == 404


def test_ingest_missing_version_returns_404(
    ingestion_client,
    ingestion_context,
):
    document = ingestion_context["document"]

    response = ingestion_client.post(
        f"/documents/{document.id}/versions/999"
        f"/extracted-contents/999/ingest"
    )

    assert response.status_code == 404


def test_ingest_extracted_content_from_wrong_version_returns_404(
    ingestion_client,
    db_session,
    ingestion_context,
    tmp_path,
):
    document = ingestion_context["document"]
    first_version = ingestion_context["version"]

    first_extracted_content = create_extracted_content(
        ingestion_client,
        document,
        first_version,
    )

    second_file = tmp_path / "guideline_v2.txt"

    second_file.write_text(
        "This is different content for version two.",
        encoding="utf-8",
    )

    second_version = DocumentVersionService(db_session).create(
        document_id=document.id,
        file_path=str(second_file),
        file_hash=calculate_hash(second_file),
    )

    response = ingestion_client.post(
        f"/documents/{document.id}/versions/{second_version.id}"
        f"/extracted-contents/{first_extracted_content['id']}/ingest"
    )

    assert response.status_code == 404