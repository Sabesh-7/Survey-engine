from pydantic import BaseModel

from app.schemas.generation import GenerationItem
from app.schemas.retrieval import RecommendationFilters, RetrievalReason


class RecommendationRequest(BaseModel):
    prompt: str
    top_k: int = 10
    embedding: list[float] | None = None
    filters: RecommendationFilters | None = None


class RecommendationItem(BaseModel):
    question_id: str
    text: str
    language: str
    category: str | None = None
    source: str
    retrieval_reason: RetrievalReason
    metadata: dict[str, object] | None = None


class RecommendationResponse(BaseModel):
    items: list[RecommendationItem]
    gaps: list[str]
    generated_questions: list[GenerationItem] = []
    rejected_items: list[GenerationItem] = []
