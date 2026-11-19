from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_version import DocumentVersion


class DocumentVersionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document_id: int,
        version_number: int,
        file_path: str,
        file_hash: str,
        processing_status: str = "uploaded",
    ) -> DocumentVersion:
        version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            file_path=file_path,
            file_hash=file_hash,
            processing_status=processing_status,
        )

        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)

        return version

    def get_by_id(
        self,
        document_version_id: int,
    ) -> DocumentVersion | None:
        statement = select(DocumentVersion).where(
            DocumentVersion.id == document_version_id
        )
        return self.db.scalar(statement)

    def get_all(
        self,
        document_id: int | None = None,
    ) -> list[DocumentVersion]:
        statement = select(DocumentVersion).order_by(
            DocumentVersion.document_id,
            DocumentVersion.version_number,
        )

        if document_id is not None:
            statement = statement.where(
                DocumentVersion.document_id == document_id
            )

        return list(self.db.scalars(statement).all())

    def get_latest(
        self,
        document_id: int,
    ) -> DocumentVersion | None:
        statement = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .limit(1)
        )

        return self.db.scalar(statement)

    def update_processing_status(
        self,
        document_version_id: int,
        processing_status: str,
    ) -> DocumentVersion | None:
        version = self.get_by_id(document_version_id)

        if version is None:
            return None

        version.processing_status = processing_status

        self.db.commit()
        self.db.refresh(version)

        return version

    def delete(
        self,
        document_version_id: int,
    ) -> bool:
        version = self.get_by_id(document_version_id)

        if version is None:
            return False

        self.db.delete(version)
        self.db.commit()

        return True