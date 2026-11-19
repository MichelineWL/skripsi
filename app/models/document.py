from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )
    period_id: Mapped[int | None] = mapped_column(
        ForeignKey("periods.id"),
        nullable=True,
    )
    program_id: Mapped[int | None] = mapped_column(
        ForeignKey("programs.id"),
        nullable=True,
    )
    division_id: Mapped[int | None] = mapped_column(
        ForeignKey("divisions.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_type: Mapped[str] = mapped_column(String(100), nullable=False)