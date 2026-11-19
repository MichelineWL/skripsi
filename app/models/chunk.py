from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(primary_key=True)
    extracted_content_id: Mapped[int] = mapped_column(
        ForeignKey("extracted_contents.id"),
        nullable=False,
    )
    document_version_id: Mapped[int] = mapped_column(
        ForeignKey("document_versions.id"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    locator: Mapped[str] = mapped_column(String(255), nullable=False)
    vector_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )