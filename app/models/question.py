from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, text
from sqlalchemy.sql import func
from sqlalchemy.types import UUID
from sqlalchemy.dialects.postgresql import ENUM

from app.database.base import Base


question_source_enum = ENUM(
    "standard",
    "historical",
    "ai_generated",
    "manual",
    name="question_source",
    create_type=False,
)


class Question(Base):
    __tablename__ = "questions"

    question_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    question_group_id = Column(
        UUID(as_uuid=True),
        ForeignKey("question_groups.question_group_id"),
        nullable=True
    )

    canonical_question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("questions.question_id"),
        nullable=True
    )

    text = Column(String, nullable=False)
    language = Column(String, nullable=False)
    category = Column(String, nullable=True)

    source = Column(question_source_enum, nullable=False)

    source_reference = Column(String, nullable=True)
    created_by = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)