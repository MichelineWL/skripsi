from pathlib import Path
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    PointIdsList,
    VectorParams,
)

from app.core.config import settings
from app.core.exceptions import BusinessRuleError


class QdrantService:
    def __init__(self, client=None):
        if client is not None:
            self.client = client
        else:
            storage_path = Path(settings.qdrant_path)
            storage_path.mkdir(parents=True, exist_ok=True)

            self.client = QdrantClient(
                path=str(storage_path)
            )

        self.collection_name = (
            settings.qdrant_collection_name
        )
        self.vector_size = settings.qdrant_vector_size

        self.ensure_collection()

    def ensure_collection(self):
        if self.client.collection_exists(
            self.collection_name
        ):
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE,
            ),
        )

    def upsert_chunk(
        self,
        vector: list[float],
        payload: dict,
        vector_id: str | None = None,
    ) -> str:
        if not vector:
            raise BusinessRuleError(
                "Vector cannot be empty."
            )

        if len(vector) != self.vector_size:
            raise BusinessRuleError(
                "Vector dimension does not match "
                "configured Qdrant dimension."
            )

        point_id = vector_id or str(uuid4())

        try:
            point = PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )

            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True,
            )

            return point_id

        except BusinessRuleError:
            raise

        except Exception as exc:
            raise BusinessRuleError(
                "Failed to store vector in Qdrant."
            ) from exc

    def delete_vectors(
        self,
        vector_ids: list[str],
    ) -> None:
        if not vector_ids:
            return

        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(
                points=vector_ids
            	),
            	wait=True,
            )

        except Exception as exc:
            raise BusinessRuleError(
                "Failed to delete vectors from Qdrant."
            ) from exc

    def search(
        self,
        query_vector: list[float],
        limit: int = 5,
    ) -> list:
        if not query_vector:
            raise BusinessRuleError(
                "Query vector cannot be empty."
            )

        if len(query_vector) != self.vector_size:
            raise BusinessRuleError(
                "Query vector dimension does not match "
                "configured Qdrant dimension."
            )

        if limit <= 0:
            raise BusinessRuleError(
                "Search limit must be greater than zero."
            )

        try:
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                with_payload=True,
            )

            return response.points

        except Exception as exc:
            raise BusinessRuleError(
                "Vector search failed."
            ) from exc

    def close(self) -> None:
        self.client.close()