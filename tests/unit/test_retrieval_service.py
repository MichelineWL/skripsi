from types import SimpleNamespace

from app.services.retrieval_service import RetrievalService


class FakeEmbeddingService:
    def __init__(self, vector=None):
        self.vector = vector or [0.1, 0.2, 0.3]
        self.calls = []

    def embed_text(self, text):
        self.calls.append(text)
        return self.vector


class FakeQdrantService:
    def __init__(self, points=None):
        self.points = points or []
        self.calls = []

    def search(
        self,
        query_vector,
        limit,
        organization_id,
    ):
        self.calls.append(
            {
                "query_vector": query_vector,
                "limit": limit,
                "organization_id": organization_id,
            }
        )

        return self.points


def create_fake_point(
    score=0.75,
    payload=None,
):
    if payload is None:
        payload = {
            "content": "Relevant test content",
            "extracted_content_id": 10,
            "document_version_id": 20,
            "chunk_index": 2,
            "locator": "page:3",
            "page_number": 3,
        }

    return SimpleNamespace(
        score=score,
        payload=payload,
    )


def create_service(
    points=None,
):
    embedding_service = FakeEmbeddingService()

    qdrant_service = FakeQdrantService(
        points=points,
    )

    service = RetrievalService(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    return {
        "service": service,
        "embedding": embedding_service,
        "qdrant": qdrant_service,
    }


def test_retrieval_embeds_query():
    dependencies = create_service()
    service = dependencies["service"]

    service.search(
        query="Test retrieval query",
        organization_id=1,
        limit=3,
    )

    assert dependencies["embedding"].calls == [
        "Test retrieval query"
    ]


def test_retrieval_searches_qdrant_with_query_vector_and_organization():
    dependencies = create_service()
    service = dependencies["service"]

    service.search(
        query="Test retrieval query",
        organization_id=7,
        limit=5,
    )

    assert dependencies["qdrant"].calls == [
        {
            "query_vector": [0.1, 0.2, 0.3],
            "limit": 5,
            "organization_id": 7,
        }
    ]


def test_retrieval_maps_point_to_result():
    point = create_fake_point(
        score=0.85,
    )

    dependencies = create_service(
        points=[point],
    )

    result = dependencies["service"].search(
        query="Test retrieval query",
        organization_id=1,
        limit=3,
    )

    assert result["query"] == "Test retrieval query"
    assert result["result_count"] == 1

    retrieved = result["results"][0]

    assert retrieved["score"] == 0.85
    assert retrieved["content"] == "Relevant test content"
    assert retrieved["extracted_content_id"] == 10
    assert retrieved["document_version_id"] == 20
    assert retrieved["chunk_index"] == 2
    assert retrieved["locator"] == "page:3"
    assert retrieved["page_number"] == 3


def test_retrieval_returns_empty_results_when_no_points():
    dependencies = create_service(
        points=[],
    )

    result = dependencies["service"].search(
        query="No matching content",
        organization_id=1,
        limit=3,
    )

    assert result["query"] == "No matching content"
    assert result["result_count"] == 0
    assert result["results"] == []