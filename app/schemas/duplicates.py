from enum import Enum
from pydantic import BaseModel

from app.schemas.retrieval import RecommendationFilters


class DuplicateMatchType(str, Enum):
    exact_or_near_exact = "exact_or_near_exact"
    semantic_duplicate = "semantic_duplicate"


class DuplicateDetectionRequest(BaseModel):
    question_text: str
    language: str | None = None
    top_k: int = 10
    filters: RecommendationFilters | None = None


class DuplicateCandidate(BaseModel):
    question_id: str
    text: str
    language: str
    category: str | None = None
    source: str
    similarity_score: float
    match_type: DuplicateMatchType
    metadata: dict[str, object] | None = None


class DuplicateDetectionResponse(BaseModel):
    duplicates: list[DuplicateCandidate]
