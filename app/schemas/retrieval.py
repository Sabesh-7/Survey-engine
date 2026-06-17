from enum import Enum
from pydantic import BaseModel


class RetrievalReason(str, Enum):
    semantic_match = "semantic_match"


class RecommendationFilters(BaseModel):
    language: str | None = None
    sources: list[str] | None = None
    categories: list[str] | None = None
    classification_codes: list[str] | None = None
