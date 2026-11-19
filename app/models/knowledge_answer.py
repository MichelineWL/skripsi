from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class KnowledgeAnswer(Base):
    __tablename__ = "knowledge_answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    follow_up_question_id: Mapped[int] = mapped_column(
        ForeignKey("follow_up_questions.id"),
        nullable=False,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    contributor: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    review_status: Mapped[str] = mapped_column(
        String(50),
        default="pending_review",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )