from pathlib import Path
import hashlib

from pypdf import PdfReader

from app.repositories.document_version_repository import (
    DocumentVersionRepository,
)
from app.repositories.extracted_content_repository import (
    ExtractedContentRepository,
)

from app.core.exceptions import (
    BusinessRuleError,
    ResourceNotFoundError,
)


class ExtractionService:
    SUPPORTED_EXTENSIONS = {".txt", ".pdf"}

    def __init__(self, db):
        self.db = db
        self.extracted_content_repository = (
            ExtractedContentRepository(db)
        )
        self.document_version_repository = (
            DocumentVersionRepository(db)
        )

    def extract(self, document_version_id: int):
        version = self.document_version_repository.get_by_id(
            document_version_id
        )

        if version is None:
            raise ResourceNotFoundError(
                "Document version not found."
            )

        file_path = Path(version.file_path)

        try:
            if not file_path.exists():
                raise BusinessRuleError(
                    "Source file does not exist."
                )

            if not file_path.is_file():
                raise BusinessRuleError(
                    "Source path is not a file."
                )

            extension = file_path.suffix.lower()

            if extension not in self.SUPPORTED_EXTENSIONS:
                raise BusinessRuleError(
                    "Unsupported file format. "
                    "Only PDF and TXT are supported."
                )

            actual_hash = self._calculate_hash(file_path)

            if actual_hash != version.file_hash:
                raise BusinessRuleError(
                    "Source file hash does not match "
                    "the registered document version."
                )

            self.document_version_repository.update_processing_status(
                document_version_id=document_version_id,
                processing_status="processing",
            )

            if extension == ".txt":
                content = self._extract_txt(file_path)
                extraction_method = "utf-8"

            else:
                content = self._extract_pdf(file_path)
                extraction_method = "pypdf"

            content = content.strip()

            if not content:
                raise BusinessRuleError(
                    "No text content could be extracted."
                )

            extracted_content = (
                self.extracted_content_repository.create(
                    document_version_id=document_version_id,
                    extraction_method=extraction_method,
                    content=content,
                    extraction_status="completed",
                )
            )

            self.document_version_repository.update_processing_status(
                document_version_id=document_version_id,
                processing_status="completed",
            )

            return extracted_content

        except BusinessRuleError:
            self.document_version_repository.update_processing_status(
                document_version_id=document_version_id,
                processing_status="failed",
            )
            raise

        except Exception as exc:
            self.document_version_repository.update_processing_status(
                document_version_id=document_version_id,
                processing_status="failed",
            )

            raise BusinessRuleError(
                "Document extraction failed."
            ) from exc

    @staticmethod
    def _calculate_hash(file_path: Path) -> str:
        sha256 = hashlib.sha256()

        with file_path.open("rb") as file:
            for block in iter(
                lambda: file.read(4096),
                b"",
            ):
                sha256.update(block)

        return sha256.hexdigest()

    @staticmethod
    def _extract_txt(file_path: Path) -> str:
        return file_path.read_text(
            encoding="utf-8"
        )

    @staticmethod
    def _extract_pdf(file_path: Path) -> str:
        reader = PdfReader(str(file_path))

        page_texts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            page_texts.append(page_text)

        return "\n\n".join(page_texts)