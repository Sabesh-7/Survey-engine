from sqlalchemy import Column, DateTime, Float, ForeignKey, String, text
from sqlalchemy.sql import func
from sqlalchemy.types import UUID


from app.database.base import Base


class QuestionClassification(Base):
    __tablename__ = "question_classifications"

    classification_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.question_id"),
        nullable=False
    )
    tag = Column(String, nullable=True)
    classification_code = Column(String, nullable=True)
    source = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
