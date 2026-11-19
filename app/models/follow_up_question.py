from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class FollowUpQuestion(Base):
    __tablename__ = "follow_up_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    knowledge_interview_id: Mapped[int] = mapped_column(
        ForeignKey("knowledge_interviews.id"),
        nullable=False,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )