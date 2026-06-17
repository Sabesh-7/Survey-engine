from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import UUID

from app.database.base import Base


class QuestionReview(Base):
    __tablename__ = "question_reviews"

    review_id = Column(
    UUID(as_uuid=True),
    primary_key=True,
    server_default=text("gen_random_uuid()")
    )
    run_id = Column(UUID(as_uuid=True), ForeignKey("ai_runs.run_id"), nullable=True)
    run_item_id = Column(UUID(as_uuid=True), ForeignKey("ai_run_items.run_item_id"), nullable=True)
    question_text = Column(String, nullable=False)
    language = Column(String, nullable=False)
    decision = Column(String, nullable=False)
    reviewer = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    decision_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
