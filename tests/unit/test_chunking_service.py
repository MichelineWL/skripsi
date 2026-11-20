from app.services.chunking_service import ChunkingService


def test_split_content_returns_single_chunk_for_short_text():
    text = "Ini adalah dokumen pendek."

    chunks = ChunkingService._split_content(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_content_splits_by_paragraph():
    paragraphs = [
        "Paragraf pertama berisi informasi organisasi.",
        "Paragraf kedua menjelaskan program kerja.",
    ]

    text = "\n\n".join(paragraphs)

    chunks = ChunkingService._split_content(text)

    assert chunks
    assert all(chunk.strip() for chunk in chunks)


def test_split_content_handles_empty_text():
    chunks = ChunkingService._split_content("")

    assert chunks == []


def test_split_long_text_splits_long_paragraph():
    text = "A" * (
        ChunkingService.MAX_CHUNK_SIZE + 500
    )

    fragments = ChunkingService._split_long_text(text)

    assert len(fragments) > 1
    assert all(
        len(fragment)
        <= ChunkingService.MAX_CHUNK_SIZE
        for fragment in fragments
    )


def test_split_by_character_respects_max_size():
    text = "word " * 2000
    max_size = 1000

    fragments = ChunkingService._split_by_character(
        text,
        max_size,
    )

    assert len(fragments) > 1
    assert all(
        len(fragment) <= max_size
        for fragment in fragments
    )


def test_split_by_character_preserves_content():
    text = "This is a long text that must be split into fragments."

    fragments = ChunkingService._split_by_character(
        text,
        15,
    )

    reconstructed = " ".join(fragments)

    assert reconstructed == text.strip()


def test_apply_overlap_returns_original_for_single_chunk():
    chunks = ["Dokumen pendek."]

    result = ChunkingService._apply_overlap(chunks)

    assert result == chunks


def test_apply_overlap_adds_previous_context():
    chunks = [
        "A" * 500,
        "B" * 500,
    ]

    result = ChunkingService._apply_overlap(chunks)

    assert len(result) == 2
    assert result[0] == chunks[0]
    assert result[1].startswith(
        "A" * ChunkingService.CHUNK_OVERLAP
    )


def test_split_content_produces_sequential_chunks():
    text = "\n\n".join(
        f"Paragraph {index}. "
        + ("This is content. " * 150)
        for index in range(10)
    )

    chunks = ChunkingService._split_content(text)

    assert len(chunks) > 1
    assert all(
        isinstance(chunk, str)
        for chunk in chunks
    )
    assert all(chunk.strip() for chunk in chunks)


def test_split_content_uses_overlap_for_multiple_chunks():
    text = "Sentence content. " * 1000

    chunks = ChunkingService._split_content(text)

    assert len(chunks) > 1

    for index in range(1, len(chunks)):
        previous_chunk = chunks[index - 1]
        current_chunk = chunks[index]

        expected_overlap = previous_chunk[
            -ChunkingService.CHUNK_OVERLAP:
        ].strip()

        assert current_chunk.startswith(
            expected_overlap
        )