from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import UUID
from sqlalchemy import text

from app.database.base import Base


class AiRunItem(Base):
    __tablename__ = "ai_run_items"

    run_item_id = Column(
    UUID(as_uuid=True),
    primary_key=True,
    server_default=text("gen_random_uuid()")
    )
    run_id = Column(UUID(as_uuid=True), ForeignKey("ai_runs.run_id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=True)
    score = Column(Float, nullable=True)
    stage = Column(String, nullable=True)
    item_type = Column(String, nullable=True)
    status = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
