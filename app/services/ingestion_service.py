from sqlalchemy import select

from app.core.exceptions import BusinessRuleError
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.extracted_content import ExtractedContent
from app.repositories.chunk_repository import ChunkRepository
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class IngestionService:
    def __init__(
        self,
        db,
        chunking_service=None,
        embedding_service=None,
        qdrant_service=None,
    ):
        self.db = db

        self.chunk_repository = ChunkRepository(db)

        self.chunking_service = (
            chunking_service
            or ChunkingService(db)
        )

        self.embedding_service = (
            embedding_service
            or EmbeddingService()
        )

        self.qdrant_service = (
            qdrant_service
            or QdrantService()
        )

    def ingest_extracted_content(
        self,
        extracted_content_id: int,
    ) -> dict:
        # Resolve organization dari relasi dokumen.
        statement = (
            select(Document.organization_id)
            .join(
                DocumentVersion,
                DocumentVersion.document_id
                == Document.id,
            )
            .join(
                ExtractedContent,
                ExtractedContent.document_version_id
                == DocumentVersion.id,
            )
            .where(
                ExtractedContent.id
                == extracted_content_id
            )
        )

        organization_id = self.db.scalar(statement)

        if organization_id is None:
            raise BusinessRuleError(
                "Organization could not be resolved "
                "for extracted content."
            )

        # Build chunk baru tanpa menghapus chunk lama.
        new_chunks = self.chunking_service.build_chunks(
            extracted_content_id
        )

        old_chunks = (
            self.chunk_repository.get_by_extracted_content(
                extracted_content_id
            )
        )

        old_vector_ids = [
            chunk.vector_id
            for chunk in old_chunks
            if chunk.vector_id
        ]

        new_vector_ids = []

        try:
            # Generate embedding dan simpan vector baru.
            for chunk in new_chunks:
                vector = self.embedding_service.embed_text(
                    chunk.content
                )

                payload = {
                    "organization_id": organization_id,
                    "extracted_content_id": (
                        chunk.extracted_content_id
                    ),
                    "document_version_id": (
                        chunk.document_version_id
                    ),
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "locator": chunk.locator,
                    "page_number": chunk.page_number,
                }

                vector_id = (
                    self.qdrant_service.upsert_chunk(
                        vector=vector,
                        payload=payload,
                    )
                )

                chunk.vector_id = vector_id
                new_vector_ids.append(vector_id)

            # Persist chunk baru ke SQLite.
            persisted_chunks = (
                self.chunk_repository
                .replace_by_extracted_content(
                    extracted_content_id=(
                        extracted_content_id
                    ),
                    chunks=new_chunks,
                )
            )

        except Exception as exc:
            # Compensating action:
            # hapus vector baru jika proses gagal.
            self._cleanup_vectors_safely(
                new_vector_ids
            )

            self.db.rollback()

            if isinstance(exc, BusinessRuleError):
                raise

            raise BusinessRuleError(
                "Ingestion process failed."
            ) from exc

        # Setelah SQLite berhasil, hapus vector lama.
        cleanup_warning = None

        try:
            self.qdrant_service.delete_vectors(
                old_vector_ids
            )

        except Exception:
            # Ingestion utama berhasil, tetapi vector lama
            # mungkin masih tertinggal di Qdrant.
            cleanup_warning = (
                "New chunks were ingested successfully, "
                "but old vectors could not be deleted."
            )

        return {
            "extracted_content_id": (
                extracted_content_id
            ),
            "chunk_count": len(persisted_chunks),
            "vector_count": len(new_vector_ids),
            "status": "completed",
            "cleanup_warning": cleanup_warning,
        }

    def _cleanup_vectors_safely(
        self,
        vector_ids: list[str],
    ) -> None:
        if not vector_ids:
            return

        try:
            self.qdrant_service.delete_vectors(
                vector_ids
            )
        except Exception:
            # Jangan menutupi error utama ingestion.
            pass