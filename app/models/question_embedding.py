from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint , text
from sqlalchemy.sql import func
from sqlalchemy.types import UUID
from pgvector.sqlalchemy import Vector

from app.database.base import Base


class QuestionEmbedding(Base):
    __tablename__ = "question_embeddings"
    __table_args__ = (UniqueConstraint("question_id", "model_name", name="uq_question_model"),)

    embedding_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.question_id"), nullable=False)
    model_name = Column(String, nullable=False)
    embedding = Column(Vector(1024), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
