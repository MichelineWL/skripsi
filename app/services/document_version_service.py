from app.repositories.document_version_repository import (
    DocumentVersionRepository,
)
from app.repositories.document_repository import DocumentRepository

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class DocumentVersionService:
    def __init__(self, db):
        self.repository = DocumentVersionRepository(db)
        self.document_repository = DocumentRepository(db)

    def create(
        self,
        document_id: int,
        file_path: str,
        file_hash: str,
    ):
        document = self.document_repository.get_by_id(document_id)

        if document is None:
            raise ResourceNotFoundError("Document not found.")

        file_path = file_path.strip()
        file_hash = file_hash.strip()

        if not file_path:
            raise BusinessRuleError("File path cannot be empty.")

        if not file_hash:
            raise BusinessRuleError("File hash cannot be empty.")

        latest_version = self.repository.get_latest(document_id)

        if latest_version is None:
            next_version_number = 1
        else:
            next_version_number = latest_version.version_number + 1

        existing_versions = self.repository.get_all(document_id)

        if any(
            version.file_hash == file_hash
            for version in existing_versions
        ):
            raise BusinessRuleError(
                "This file has already been uploaded to the document."
            )

        return self.repository.create(
            document_id=document_id,
            version_number=next_version_number,
            file_path=file_path,
            file_hash=file_hash,
        )

    def get_by_id(self, document_version_id: int):
        version = self.repository.get_by_id(document_version_id)

        if version is None:
            raise ResourceNotFoundError(
                "Document version not found."
            )

        return version

    def get_all(self, document_id=None):
        if document_id is not None:
            document = self.document_repository.get_by_id(document_id)

            if document is None:
                raise ResourceNotFoundError("Document not found.")

        return self.repository.get_all(document_id)

    def get_latest(self, document_id: int):
        document = self.document_repository.get_by_id(document_id)

        if document is None:
            raise ResourceNotFoundError("Document not found.")

        return self.repository.get_latest(document_id)

    def update_processing_status(
        self,
        document_version_id: int,
        processing_status: str,
    ):
        processing_status = processing_status.strip()

        if not processing_status:
            raise BusinessRuleError(
                "Processing status cannot be empty."
            )

        version = self.repository.update_processing_status(
            document_version_id=document_version_id,
            processing_status=processing_status,
        )

        if version is None:
            raise ResourceNotFoundError(
                "Document version not found."
            )

        return version

    def delete(self, document_version_id: int):
        if not self.repository.delete(document_version_id):
            raise ResourceNotFoundError(
                "Document version not found."
            )

        return True