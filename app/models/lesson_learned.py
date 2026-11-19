from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class LessonLearned(Base):
    __tablename__ = "lessons_learned"

    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int] = mapped_column(
        ForeignKey("programs.id"),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    document_id: Mapped[int | None] = mapped_column(
        ForeignKey("documents.id"),
        nullable=True,
    )
    knowledge_answer_id: Mapped[int | None] = mapped_column(
        ForeignKey("knowledge_answers.id"),
        nullable=True,
    )