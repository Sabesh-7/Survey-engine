from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.types import UUID

from app.database.base import Base


class Survey(Base):
    __tablename__ = "surveys"

    survey_id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=True)
    language = Column(String, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
