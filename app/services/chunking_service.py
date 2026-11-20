import re

from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.extracted_content_repository import (
    ExtractedContentRepository,
)
from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class ChunkingService:
    TARGET_CHUNK_SIZE = 2500
    MAX_CHUNK_SIZE = 3500
    CHUNK_OVERLAP = 400

    def __init__(self, db):
        self.db = db
        self.chunk_repository = ChunkRepository(db)
        self.extracted_content_repository = (
            ExtractedContentRepository(db)
        )

    def build_chunks(
        self,
        extracted_content_id: int,
    ) -> list[Chunk]:
        extracted_content = (
            self.extracted_content_repository.get_by_id(
                extracted_content_id
            )
        )

        if extracted_content is None:
            raise ResourceNotFoundError(
                "Extracted content not found."
            )

        content = extracted_content.content.strip()

        if not content:
            raise BusinessRuleError(
                "Extracted content is empty."
            )

        chunk_texts = self._split_content(content)

        if not chunk_texts:
            raise BusinessRuleError(
                "No chunks could be generated."
            )

        return [
            Chunk(
                extracted_content_id=extracted_content.id,
                document_version_id=(
                    extracted_content.document_version_id
                ),
                chunk_index=index,
                content=chunk_text,
                page_number=None,
                locator=(
                    f"extracted_content:"
                    f"{extracted_content.id}:"
                    f"chunk:{index}"
                ),
                vector_id=None,
            )
            for index, chunk_text in enumerate(chunk_texts)
        ]

    def chunk_extracted_content(
        self,
        extracted_content_id: int,
    ) -> list[Chunk]:
        chunks = self.build_chunks(
            extracted_content_id
        )

        # Mempertahankan perilaku lama:
        # replace chunk lama dan simpan hasil terbaru.
        return self.chunk_repository.replace_by_extracted_content(
            extracted_content_id=extracted_content_id,
            chunks=chunks,
        )

    def get_chunks(
        self,
        extracted_content_id: int,
    ) -> list[Chunk]:
        extracted_content = (
            self.extracted_content_repository.get_by_id(
                extracted_content_id
            )
        )

        if extracted_content is None:
            raise ResourceNotFoundError(
                "Extracted content not found."
            )

        return self.chunk_repository.get_by_extracted_content(
            extracted_content_id
        )

    @classmethod
    def _split_content(
        cls,
        content: str,
    ) -> list[str]:
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(
                r"\n\s*\n",
                content,
            )
            if paragraph.strip()
        ]

        fragments = []

        for paragraph in paragraphs:
            fragments.extend(
                cls._split_long_text(paragraph)
            )

        chunks = []
        current = ""

        for fragment in fragments:
            if not current:
                current = fragment
                continue

            candidate = f"{current}\n\n{fragment}"

            if len(candidate) <= cls.TARGET_CHUNK_SIZE:
                current = candidate
            else:
                chunks.append(current.strip())
                current = fragment

        if current:
            chunks.append(current.strip())

        return cls._apply_overlap(chunks)

    @classmethod
    def _split_long_text(
        cls,
        text: str,
    ) -> list[str]:
        if len(text) <= cls.MAX_CHUNK_SIZE:
            return [text]

        # First try splitting by sentence.
        sentences = re.split(
            r"(?<=[.!?])\s+",
            text,
        )

        if len(sentences) > 1:
            result = []
            current = ""

            for sentence in sentences:
                if len(sentence) > cls.MAX_CHUNK_SIZE:
                    if current:
                        result.append(current.strip())
                        current = ""

                    result.extend(
                        cls._split_by_character(
                            sentence,
                            cls.MAX_CHUNK_SIZE,
                        )
                    )
                    continue

                candidate = (
                    f"{current} {sentence}".strip()
                )

                if len(candidate) <= cls.MAX_CHUNK_SIZE:
                    current = candidate
                else:
                    if current:
                        result.append(current.strip())

                    current = sentence

            if current:
                result.append(current.strip())

            return result

        # Fallback: split at whitespace near the limit.
        return cls._split_by_character(
            text,
            cls.MAX_CHUNK_SIZE,
        )

    @staticmethod
    def _split_by_character(
        text: str,
        max_size: int,
    ) -> list[str]:
        result = []
        remaining = text.strip()

        while len(remaining) > max_size:
            split_at = remaining.rfind(
                " ",
                0,
                max_size,
            )

            if split_at <= 0:
                split_at = max_size

            result.append(
                remaining[:split_at].strip()
            )

            remaining = remaining[split_at:].strip()

        if remaining:
            result.append(remaining)

        return result

    @classmethod
    def _apply_overlap(
        cls,
        chunks: list[str],
    ) -> list[str]:
        if len(chunks) <= 1:
            return chunks

        result = [chunks[0]]

        for index in range(1, len(chunks)):
            previous_chunk = chunks[index - 1]
            current_chunk = chunks[index]

            overlap = previous_chunk[
                -cls.CHUNK_OVERLAP:
            ].strip()

            merged = (
                f"{overlap}\n\n{current_chunk}"
                if overlap
                else current_chunk
            )

            result.append(merged.strip())

        return result