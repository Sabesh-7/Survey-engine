from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.types import UUID

from app.database.base import Base


class QuestionDuplicate(Base):
    __tablename__ = "question_duplicates"
    __table_args__ = (
        UniqueConstraint("question_id", "duplicate_question_id", name="uq_question_duplicate"),
    )

    duplicate_id = Column(UUID(as_uuid=True), primary_key=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    duplicate_question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    method = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
