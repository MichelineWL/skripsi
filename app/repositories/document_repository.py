from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: int,
        title: str,
        document_type: str,
        period_id: int | None = None,
        program_id: int | None = None,
        division_id: int | None = None,
    ) -> Document:
        document = Document(
            organization_id=organization_id,
            period_id=period_id,
            program_id=program_id,
            division_id=division_id,
            title=title,
            document_type=document_type,
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def get_by_id(self, document_id: int) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id
        )
        return self.db.scalar(statement)

    def get_all(
        self,
        organization_id: int | None = None,
        period_id: int | None = None,
        program_id: int | None = None,
        division_id: int | None = None,
    ) -> list[Document]:
        statement = select(Document).order_by(Document.id)

        if organization_id is not None:
            statement = statement.where(
                Document.organization_id == organization_id
            )

        if period_id is not None:
            statement = statement.where(
                Document.period_id == period_id
            )

        if program_id is not None:
            statement = statement.where(
                Document.program_id == program_id
            )

        if division_id is not None:
            statement = statement.where(
                Document.division_id == division_id
            )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        document_id: int,
        title: str,
        document_type: str,
        period_id: int | None = None,
        program_id: int | None = None,
        division_id: int | None = None,
    ) -> Document | None:
        document = self.get_by_id(document_id)

        if document is None:
            return None

        document.title = title
        document.document_type = document_type
        document.period_id = period_id
        document.program_id = program_id
        document.division_id = division_id

        self.db.commit()
        self.db.refresh(document)

        return document

    def delete(self, document_id: int) -> bool:
        document = self.get_by_id(document_id)

        if document is None:
            return False

        self.db.delete(document)
        self.db.commit()

        return True