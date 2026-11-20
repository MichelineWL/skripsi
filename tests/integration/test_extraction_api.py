import hashlib

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.services.document_service import DocumentService
from app.services.document_version_service import (
    DocumentVersionService,
)


@pytest.fixture
def extraction_client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def calculate_hash(file_path):
    return hashlib.sha256(
        file_path.read_bytes()
    ).hexdigest()


@pytest.fixture
def extraction_context(db_session, tmp_path):
    organization = OrganizationRepository(db_session).create(
        "Extraction Test Organization"
    )

    document = DocumentService(db_session).create(
        organization_id=organization.id,
        title="Test Document",
        document_type="guideline",
    )

    file_path = tmp_path / "guideline.txt"

    file_path.write_text(
        "This is test content for document extraction.",
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


def test_extract_txt_success(
    extraction_client,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    response = extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_version_id"] == version.id
    assert data["extraction_method"] == "utf-8"
    assert data["extraction_status"] == "completed"
    assert (
        data["content"]
        == "This is test content for document extraction."
    )


def test_extract_updates_version_status(
    extraction_client,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    response = extraction_client.get(
        f"/documents/{document.id}/versions/{version.id}"
    )

    assert response.status_code == 200
    assert response.json()["processing_status"] == "completed"


def test_get_extracted_contents(
    extraction_client,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    response = extraction_client.get(
        f"/documents/{document.id}/versions/{version.id}/extracted-contents"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_extracted_content_by_id(
    extraction_client,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    extraction_response = extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    extracted_content_id = extraction_response.json()["id"]

    response = extraction_client.get(
        f"/documents/{document.id}/versions/{version.id}"
        f"/extracted-contents/{extracted_content_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == extracted_content_id


def test_extract_wrong_document(
    extraction_client,
    extraction_context,
):
    version = extraction_context["version"]

    response = extraction_client.post(
        f"/documents/999/versions/{version.id}/extract"
    )

    assert response.status_code == 404


def test_extract_missing_version(
    extraction_client,
    extraction_context,
):
    document = extraction_context["document"]

    response = extraction_client.post(
        f"/documents/{document.id}/versions/999/extract"
    )

    assert response.status_code == 404


def test_extract_hash_mismatch(
    extraction_client,
    db_session,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    version.file_hash = "incorrect_hash"
    db_session.commit()

    response = extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    assert response.status_code == 400

    status_response = extraction_client.get(
        f"/documents/{document.id}/versions/{version.id}"
    )

    assert status_response.json()["processing_status"] == "failed"


def test_extract_unsupported_file_format(
    extraction_client,
    db_session,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    version.file_path = "unsupported.docx"
    db_session.commit()

    response = extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    assert response.status_code == 400


def test_extract_missing_source_file(
    extraction_client,
    db_session,
    extraction_context,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    version.file_path = "missing_file.txt"
    db_session.commit()

    response = extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    assert response.status_code == 400


def test_extract_empty_txt(
    extraction_client,
    db_session,
    extraction_context,
    tmp_path,
):
    document = extraction_context["document"]
    version = extraction_context["version"]

    empty_file = tmp_path / "empty.txt"
    empty_file.write_text("", encoding="utf-8")

    version.file_path = str(empty_file)
    version.file_hash = calculate_hash(empty_file)
    db_session.commit()

    response = extraction_client.post(
        f"/documents/{document.id}/versions/{version.id}/extract"
    )

    assert response.status_code == 400

    status_response = extraction_client.get(
        f"/documents/{document.id}/versions/{version.id}"
    )

    assert status_response.json()["processing_status"] == "failed"