import pytest

from app.models.extracted_content import ExtractedContent
from app.models.chunk import Chunk
from app.services.chunking_service import ChunkingService


def create_extracted_content(db_session, content="This is extracted text."):
    extracted_content = ExtractedContent(
        document_version_id=1,
        extraction_method="text",
        content=content,
        extraction_status="success",
    )
    db_session.add(extracted_content)
    db_session.commit()
    db_session.refresh(extracted_content)
    return extracted_content


def test_chunk_extracted_content_persists_chunks(db_session):
    extracted_content = create_extracted_content(
        db_session,
        content="Paragraph one.\n\nParagraph two.\n\nParagraph three.",
    )

    service = ChunkingService(db_session)
    chunks = service.chunk_extracted_content(extracted_content.id)

    assert len(chunks) >= 1

    persisted_chunks = (
        db_session.query(Chunk)
        .filter(Chunk.extracted_content_id == extracted_content.id)
        .order_by(Chunk.chunk_index)
        .all()
    )

    assert len(persisted_chunks) == len(chunks)
    assert persisted_chunks[0].chunk_index == 0
    assert (
        persisted_chunks[0].document_version_id
        == extracted_content.document_version_id
    )


def test_chunk_extracted_content_creates_sequential_indexes(db_session):
    extracted_content = create_extracted_content(
        db_session,
        content="A" * 6000,
    )

    service = ChunkingService(db_session)
    chunks = service.chunk_extracted_content(extracted_content.id)

    indexes = [chunk.chunk_index for chunk in chunks]

    assert indexes == list(range(len(chunks)))


def test_chunk_extracted_content_creates_locator(db_session):
    extracted_content = create_extracted_content(db_session)

    service = ChunkingService(db_session)
    chunks = service.chunk_extracted_content(extracted_content.id)

    assert chunks[0].locator == (
        f"extracted_content:{extracted_content.id}:chunk:0"
    )

def test_chunk_extracted_content_rechunk_replaces_existing_chunks(db_session):
    extracted_content = create_extracted_content(
        db_session,
        content="Original content.",
    )

    service = ChunkingService(db_session)

    first_chunks = service.chunk_extracted_content(extracted_content.id)
    first_count = len(first_chunks)

    extracted_content.content = "Updated content." * 600
    db_session.commit()

    second_chunks = service.chunk_extracted_content(extracted_content.id)

    persisted_chunks = (
        db_session.query(Chunk)
        .filter(Chunk.extracted_content_id == extracted_content.id)
        .order_by(Chunk.chunk_index)
        .all()
    )

    # Konten baru menghasilkan chunk lebih banyak
    assert len(second_chunks) > first_count

    # Database berisi chunk hasil terbaru saja
    assert len(persisted_chunks) == len(second_chunks)

    # Index tetap berurutan mulai dari 0
    assert [chunk.chunk_index for chunk in persisted_chunks] == list(
        range(len(persisted_chunks))
    )

    # Konten baru tersimpan
    combined_content = " ".join(chunk.content for chunk in persisted_chunks)
    assert "Updated content." in combined_content

    # Konten lama tidak tersisa
    assert "Original content." not in combined_content

    # Tidak ada duplicate chunk berdasarkan index
    indexes = [chunk.chunk_index for chunk in persisted_chunks]
    assert len(indexes) == len(set(indexes))

def test_get_chunks_returns_persisted_chunks(db_session):
    extracted_content = create_extracted_content(
        db_session,
        content="Stored content for retrieval.",
    )

    service = ChunkingService(db_session)
    created_chunks = service.chunk_extracted_content(extracted_content.id)

    retrieved_chunks = service.get_chunks(extracted_content.id)

    assert len(retrieved_chunks) == len(created_chunks)
    assert retrieved_chunks[0].content == created_chunks[0].content


def test_chunk_extracted_content_not_found(db_session):
    service = ChunkingService(db_session)

    with pytest.raises(Exception):
        service.chunk_extracted_content(999999)


def test_get_chunks_extracted_content_not_found(db_session):
    service = ChunkingService(db_session)

    with pytest.raises(Exception):
        service.get_chunks(999999)


def test_chunk_extracted_content_empty_content(db_session):
    extracted_content = create_extracted_content(db_session, content="")

    service = ChunkingService(db_session)

    with pytest.raises(Exception):
        service.chunk_extracted_content(extracted_content.id)

def test_build_chunks_does_not_persist_chunks(db_session):
    extracted_content = create_extracted_content(
        db_session,
        content="Content for building chunks without persistence.",
    )

    service = ChunkingService(db_session)

    chunks = service.build_chunks(
        extracted_content.id
    )

    assert len(chunks) >= 1
    assert chunks[0].content == (
        "Content for building chunks without persistence."
    )

    persisted_chunks = (
        db_session.query(Chunk)
        .filter(
            Chunk.extracted_content_id
            == extracted_content.id
        )
        .all()
    )

    assert persisted_chunks == []


def test_build_chunks_preserves_chunk_metadata(db_session):
    extracted_content = create_extracted_content(
        db_session,
        content="Metadata test content.",
    )

    service = ChunkingService(db_session)

    chunks = service.build_chunks(
        extracted_content.id
    )

    assert chunks[0].extracted_content_id == (
        extracted_content.id
    )
    assert chunks[0].document_version_id == (
        extracted_content.document_version_id
    )
    assert chunks[0].chunk_index == 0
    assert chunks[0].locator == (
        f"extracted_content:{extracted_content.id}:chunk:0"
    )
    assert chunks[0].vector_id is None