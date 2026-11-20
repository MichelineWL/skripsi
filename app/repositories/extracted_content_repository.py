from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.extracted_content import ExtractedContent


class ExtractedContentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document_version_id: int,
        extraction_method: str,
        content: str,
        extraction_status: str,
    ) -> ExtractedContent:
        extracted_content = ExtractedContent(
            document_version_id=document_version_id,
            extraction_method=extraction_method,
            content=content,
            extraction_status=extraction_status,
        )

        self.db.add(extracted_content)
        self.db.commit()
        self.db.refresh(extracted_content)

        return extracted_content

    def get_by_id(
        self,
        extracted_content_id: int,
    ) -> ExtractedContent | None:
        statement = select(ExtractedContent).where(
            ExtractedContent.id == extracted_content_id
        )

        return self.db.scalar(statement)

    def get_by_document_version(
        self,
        document_version_id: int,
    ) -> list[ExtractedContent]:
        statement = (
            select(ExtractedContent)
            .where(
                ExtractedContent.document_version_id
                == document_version_id
            )
            .order_by(ExtractedContent.created_at, ExtractedContent.id)
        )

        return list(self.db.scalars(statement).all())

    def get_all(self) -> list[ExtractedContent]:
        statement = select(ExtractedContent).order_by(
            ExtractedContent.id
        )

        return list(self.db.scalars(statement).all())

    def delete(self, extracted_content_id: int) -> bool:
        extracted_content = self.get_by_id(extracted_content_id)

        if extracted_content is None:
            return False

        self.db.delete(extracted_content)
        self.db.commit()

        return True