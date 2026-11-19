from app.core.database import Base, engine
from app.models import (
    Organization,
    Period,
    Division,
    Program,
    Document,
    DocumentVersion,
    ExtractedContent,
    Chunk,
    KnowledgeInterview,
    FollowUpQuestion,
    KnowledgeAnswer,
    DecisionContext,
    TaskGuide,
    LessonLearned,
)


def create_database():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_database()