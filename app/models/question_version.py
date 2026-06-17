from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.types import UUID

from app.database.base import Base


class QuestionVersion(Base):
    __tablename__ = "question_versions"
    __table_args__ = (
        UniqueConstraint("question_id", "version_number", name="uq_question_version"),
    )

    question_version_id = Column(UUID(as_uuid=True), primary_key=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    language = Column(String, nullable=False)
    changed_by = Column(String, nullable=True)
    change_reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
