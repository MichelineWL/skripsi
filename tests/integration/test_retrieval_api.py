import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import get_retrieval_service


class FakeRetrievalService:
    def __init__(self):
        self.calls = []

    def search(
        self,
        query,
        organization_id,
        limit=3,
    ):
        self.calls.append(
            {
                "query": query,
                "organization_id": organization_id,
                "limit": limit,
            }
        )

        return {
            "query": query,
            "result_count": 1,
            "results": [
                {
                    "score": 0.85,
                    "content": "Relevant test content",
                    "extracted_content_id": 10,
                    "document_version_id": 20,
                    "chunk_index": 2,
                    "locator": "page:3",
                    "page_number": 3,
                }
            ],
        }


@pytest.fixture
def retrieval_api_service():
    return FakeRetrievalService()


@pytest.fixture
def retrieval_client(
    retrieval_api_service,
):
    app.dependency_overrides[
        get_retrieval_service
    ] = lambda: retrieval_api_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_retrieval_search_success(
    retrieval_client,
    retrieval_api_service,
):
    response = retrieval_client.post(
        "/retrieval/search",
        json={
            "query": "Test retrieval query",
            "organization_id": 7,
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "Test retrieval query"
    assert data["result_count"] == 1

    result = data["results"][0]

    assert result["score"] == 0.85
    assert result["content"] == "Relevant test content"
    assert result["extracted_content_id"] == 10
    assert result["document_version_id"] == 20
    assert result["chunk_index"] == 2
    assert result["locator"] == "page:3"
    assert result["page_number"] == 3

    assert retrieval_api_service.calls == [
        {
            "query": "Test retrieval query",
            "organization_id": 7,
            "limit": 3,
        }
    ]


def test_retrieval_search_uses_default_limit(
    retrieval_client,
    retrieval_api_service,
):
    response = retrieval_client.post(
        "/retrieval/search",
        json={
            "query": "Test retrieval query",
            "organization_id": 7,
        },
    )

    assert response.status_code == 200

    assert retrieval_api_service.calls == [
        {
            "query": "Test retrieval query",
            "organization_id": 7,
            "limit": 3,
        }
    ]


def test_retrieval_search_rejects_empty_query(
    retrieval_client,
):
    response = retrieval_client.post(
        "/retrieval/search",
        json={
            "query": "",
            "organization_id": 7,
            "limit": 3,
        },
    )

    assert response.status_code == 422


def test_retrieval_search_rejects_missing_organization_id(
    retrieval_client,
):
    response = retrieval_client.post(
        "/retrieval/search",
        json={
            "query": "Test retrieval query",
            "limit": 3,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "organization_id",
    [0, -1],
)
def test_retrieval_search_rejects_invalid_organization_id(
    retrieval_client,
    organization_id,
):
    response = retrieval_client.post(
        "/retrieval/search",
        json={
            "query": "Test retrieval query",
            "organization_id": organization_id,
            "limit": 3,
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "limit",
    [0, 11],
)
def test_retrieval_search_rejects_invalid_limit(
    retrieval_client,
    limit,
):
    response = retrieval_client.post(
        "/retrieval/search",
        json={
            "query": "Test retrieval query",
            "organization_id": 7,
            "limit": limit,
        },
    )

    assert response.status_code == 422