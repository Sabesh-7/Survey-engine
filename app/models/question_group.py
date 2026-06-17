from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.types import UUID

from app.database.base import Base


class QuestionGroup(Base):
    __tablename__ = "question_groups"

    question_group_id = Column(UUID(as_uuid=True), primary_key=True)
    group_label = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
