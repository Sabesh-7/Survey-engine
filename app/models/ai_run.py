from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.types import UUID
from sqlalchemy import text

from app.database.base import Base


class AiRun(Base):
    __tablename__ = "ai_runs"

    run_id = Column(
    UUID(as_uuid=True),
    primary_key=True,
    server_default=text("gen_random_uuid()")
    )
    run_type = Column(String, nullable=False)
    run_status = Column(String, nullable=True)
    prompt = Column(String, nullable=True)
    language = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    run_metadata = Column("metadata", JSONB, nullable=True)
    input_metadata = Column(JSONB, nullable=True)
    output_metadata = Column(JSONB, nullable=True)
    request_id = Column(String, nullable=True)
    trace_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
