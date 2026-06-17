from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import UUID

from app.database.base import Base


class SurveyQuestion(Base):
    __tablename__ = "survey_questions"

    survey_question_id = Column(UUID(as_uuid=True), primary_key=True)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.survey_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    position = Column(Integer, nullable=False)
    is_required = Column(Boolean, nullable=False, default=True)
    survey_metadata = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
