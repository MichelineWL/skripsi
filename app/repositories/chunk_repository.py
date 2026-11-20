from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


class ChunkRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_extracted_content(
        self,
        extracted_content_id: int,
    ) -> list[Chunk]:
        statement = (
            select(Chunk)
            .where(
                Chunk.extracted_content_id
                == extracted_content_id
            )
            .order_by(Chunk.chunk_index)
        )

        return list(self.db.scalars(statement).all())

    def replace_by_extracted_content(
        self,
        extracted_content_id: int,
        chunks: list[Chunk],
    ) -> list[Chunk]:
        self.db.execute(
            delete(Chunk).where(
                Chunk.extracted_content_id
                == extracted_content_id
            )
        )

        self.db.add_all(chunks)
        self.db.commit()

        for chunk in chunks:
            self.db.refresh(chunk)

        return chunks