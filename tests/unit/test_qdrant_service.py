import pytest
from qdrant_client import QdrantClient

from app.core.exceptions import BusinessRuleError
from app.services.qdrant_service import QdrantService


@pytest.fixture
def qdrant_service():
    client = QdrantClient(":memory:")
    service = QdrantService(client=client)

    yield service

    service.close()


def make_vector(value: float = 0.1) -> list[float]:
    return [value] * 3072


def test_collection_is_created(qdrant_service):
    assert qdrant_service.client.collection_exists(
        qdrant_service.collection_name
    )


def test_upsert_chunk_returns_vector_id(qdrant_service):
    vector_id = qdrant_service.upsert_chunk(
        vector=make_vector(),
        payload={"chunk_id": 1, "content": "Test content"},
    )

    assert isinstance(vector_id, str)
    assert vector_id


def test_upsert_chunk_stores_payload(qdrant_service):
    vector_id = qdrant_service.upsert_chunk(
        vector=make_vector(),
        payload={"chunk_id": 1, "content": "Test content"},
    )

    result = qdrant_service.client.retrieve(
        collection_name=qdrant_service.collection_name,
        ids=[vector_id],
        with_payload=True,
    )

    assert len(result) == 1
    assert result[0].payload["chunk_id"] == 1
    assert result[0].payload["content"] == "Test content"


def test_search_returns_stored_vector(qdrant_service):
    qdrant_service.upsert_chunk(
        vector=make_vector(),
        payload={"chunk_id": 1, "content": "Test content"},
    )

    results = qdrant_service.search(
        query_vector=make_vector(),
        limit=5,
    )

    assert len(results) == 1
    assert results[0].payload["chunk_id"] == 1


def test_delete_vectors_removes_vector(qdrant_service):
    vector_id = qdrant_service.upsert_chunk(
        vector=make_vector(),
        payload={"chunk_id": 1},
    )

    qdrant_service.delete_vectors([vector_id])

    results = qdrant_service.client.retrieve(
        collection_name=qdrant_service.collection_name,
        ids=[vector_id],
    )

    assert results == []


def test_upsert_rejects_wrong_vector_dimension(
    qdrant_service,
):
    with pytest.raises(BusinessRuleError):
        qdrant_service.upsert_chunk(
            vector=[0.1, 0.2],
            payload={},
        )


def test_search_rejects_wrong_vector_dimension(
    qdrant_service,
):
    with pytest.raises(BusinessRuleError):
        qdrant_service.search(
            query_vector=[0.1, 0.2],
        )


def test_upsert_rejects_empty_vector(qdrant_service):
    with pytest.raises(BusinessRuleError):
        qdrant_service.upsert_chunk(
            vector=[],
            payload={},
        )


def test_search_rejects_empty_vector(qdrant_service):
    with pytest.raises(BusinessRuleError):
        qdrant_service.search(
            query_vector=[],
        )


def test_search_rejects_non_positive_limit(
    qdrant_service,
):
    with pytest.raises(BusinessRuleError):
        qdrant_service.search(
            query_vector=make_vector(),
            limit=0,
        )


def test_delete_empty_list_does_nothing(qdrant_service):
    qdrant_service.delete_vectors([])

    assert qdrant_service.client.collection_exists(
        qdrant_service.collection_name
    )