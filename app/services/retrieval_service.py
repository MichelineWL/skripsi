from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService


class RetrievalService:
    def __init__(
        self,
        embedding_service=None,
        qdrant_service=None,
    ):
        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

        self.qdrant_service = (
            qdrant_service or QdrantService()
        )

    def search(
        self,
        query: str,
        organization_id: int,
        limit: int = 3,
    ) -> dict:
        query_vector = (
            self.embedding_service.embed_text(query)
        )

        points = self.qdrant_service.search(
            query_vector=query_vector,
            limit=limit,
            organization_id=organization_id,
        )

        results = []

        for point in points:
            payload = point.payload or {}

            results.append({
                "score": point.score,
                "content": payload.get("content", ""),
                "extracted_content_id": (
                    payload.get("extracted_content_id")
                ),
                "document_version_id": (
                    payload.get("document_version_id")
                ),
                "chunk_index": payload.get("chunk_index"),
                "locator": payload.get("locator"),
                "page_number": payload.get("page_number"),
            })

        return {
            "query": query,
            "result_count": len(results),
            "results": results,
        }