import pytest

from app.core.exceptions import BusinessRuleError
from app.services.ingestion_service import IngestionService


class FakeDB:
    def __init__(self, organization_id=1):
        self.organization_id = organization_id
        self.rollback_called = False
        self.scalar_calls = []

    def scalar(self, statement):
        self.scalar_calls.append(statement)
        return self.organization_id

    def rollback(self):
        self.rollback_called = True


class FakeChunk:
    def __init__(
        self,
        extracted_content_id=1,
        document_version_id=1,
        chunk_index=0,
        content="Test chunk content",
        locator="page:1",
        page_number=1,
        vector_id=None,
    ):
        self.extracted_content_id = extracted_content_id
        self.document_version_id = document_version_id
        self.chunk_index = chunk_index
        self.content = content
        self.locator = locator
        self.page_number = page_number
        self.vector_id = vector_id


class FakeChunkRepository:
    def __init__(self, old_chunks=None):
        self.old_chunks = old_chunks or []
        self.persisted_chunks = None

    def get_by_extracted_content(self, extracted_content_id):
        return self.old_chunks

    def replace_by_extracted_content(
        self,
        extracted_content_id,
        chunks,
    ):
        self.persisted_chunks = chunks
        return chunks


class FakeChunkingService:
    def __init__(self, chunks=None):
        self.chunks = chunks or []

    def build_chunks(self, extracted_content_id):
        return self.chunks


class FakeEmbeddingService:
    def __init__(self, vectors=None):
        self.vectors = vectors or [[0.1, 0.2, 0.3]]
        self.calls = []

    def embed_text(self, text):
        self.calls.append(text)
        return self.vectors[len(self.calls) - 1]


class FakeQdrantService:
    def __init__(self):
        self.upsert_calls = []
        self.delete_calls = []
        self.fail_upsert = False
        self.fail_delete = False
        self.vector_counter = 0

    def upsert_chunk(self, vector, payload):
        if self.fail_upsert:
            raise BusinessRuleError(
                "Failed to store vector."
            )

        self.vector_counter += 1
        vector_id = f"vector-{self.vector_counter}"

        self.upsert_calls.append(
            {
                "vector": vector,
                "payload": payload,
                "vector_id": vector_id,
            }
        )

        return vector_id

    def delete_vectors(self, vector_ids):
        if self.fail_delete:
            raise BusinessRuleError(
                "Failed to delete vectors."
            )

        self.delete_calls.append(vector_ids)


@pytest.fixture
def ingestion_dependencies(monkeypatch):
    repository = FakeChunkRepository()

    chunking_service = FakeChunkingService(
        chunks=[
            FakeChunk(chunk_index=0),
            FakeChunk(
                chunk_index=1,
                content="Second chunk",
            ),
        ]
    )

    embedding_service = FakeEmbeddingService(
        vectors=[
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
        ]
    )

    qdrant_service = FakeQdrantService()
    fake_db = FakeDB(organization_id=1)

    monkeypatch.setattr(
        "app.services.ingestion_service.ChunkRepository",
        lambda db: repository,
    )

    service = IngestionService(
        db=fake_db,
        chunking_service=chunking_service,
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
    )

    return {
        "service": service,
        "db": fake_db,
        "repository": repository,
        "chunking": chunking_service,
        "embedding": embedding_service,
        "qdrant": qdrant_service,
    }


def test_ingestion_successfully_processes_chunks(
    ingestion_dependencies,
):
    dependencies = ingestion_dependencies
    service = dependencies["service"]

    result = service.ingest_extracted_content(1)

    assert result["status"] == "completed"
    assert result["chunk_count"] == 2
    assert result["vector_count"] == 2
    assert result["cleanup_warning"] is None

    assert len(
        dependencies["embedding"].calls
    ) == 2

    assert len(
        dependencies["qdrant"].upsert_calls
    ) == 2

    assert (
        dependencies["repository"].persisted_chunks
        is not None
    )

    assert len(dependencies["db"].scalar_calls) == 1


def test_ingestion_assigns_vector_ids_to_chunks(
    ingestion_dependencies,
):
    dependencies = ingestion_dependencies

    dependencies["service"].ingest_extracted_content(1)

    persisted_chunks = (
        dependencies["repository"].persisted_chunks
    )

    assert persisted_chunks[0].vector_id == "vector-1"
    assert persisted_chunks[1].vector_id == "vector-2"


def test_ingestion_saves_correct_qdrant_payload(
    ingestion_dependencies,
):
    dependencies = ingestion_dependencies

    dependencies["service"].ingest_extracted_content(1)

    payload = (
        dependencies["qdrant"].upsert_calls[0]["payload"]
    )

    assert payload["extracted_content_id"] == 1
    assert payload["document_version_id"] == 1
    assert payload["organization_id"] == 1
    assert payload["chunk_index"] == 0
    assert payload["content"] == "Test chunk content"
    assert payload["locator"] == "page:1"
    assert payload["page_number"] == 1


def test_ingestion_deletes_old_vectors_after_success(
    ingestion_dependencies,
):
    dependencies = ingestion_dependencies

    dependencies["repository"].old_chunks = [
        FakeChunk(vector_id="old-vector-1"),
        FakeChunk(vector_id="old-vector-2"),
    ]

    dependencies["service"].ingest_extracted_content(1)

    assert dependencies["qdrant"].delete_calls == [
        ["old-vector-1", "old-vector-2"]
    ]


def test_ingestion_returns_warning_when_old_vector_cleanup_fails(
    ingestion_dependencies,
):
    dependencies = ingestion_dependencies

    dependencies["repository"].old_chunks = [
        FakeChunk(vector_id="old-vector-1")
    ]

    dependencies["qdrant"].fail_delete = True

    result = dependencies["service"].ingest_extracted_content(1)

    assert result["status"] == "completed"
    assert result["cleanup_warning"] is not None


def test_ingestion_rolls_back_when_vector_storage_fails(
    ingestion_dependencies,
):
    dependencies = ingestion_dependencies

    dependencies["qdrant"].fail_upsert = True

    fake_db = FakeDB(organization_id=1)

    service = IngestionService(
        db=fake_db,
        chunking_service=dependencies["chunking"],
        embedding_service=dependencies["embedding"],
        qdrant_service=dependencies["qdrant"],
    )

    with pytest.raises(BusinessRuleError):
        service.ingest_extracted_content(1)

    assert fake_db.rollback_called is True