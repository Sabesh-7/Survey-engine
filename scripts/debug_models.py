# scripts/debug_models.py

from app.database.base import Base

from app.models.question import Question

print(Base.metadata.tables.keys())