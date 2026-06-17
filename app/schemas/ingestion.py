from pydantic import BaseModel, Field

from app.schemas.retrieval import RecommendationFilters


class IngestionQuestion(BaseModel):
    text: str
    language: str
    category: str | None = None
    source: str
    source_reference: str | None = None
    created_by: str | None = None
    confidence_score: float | None = None
    tags: list[str] | None = None
    classification_codes: list[str] | None = None


class IngestionRequest(BaseModel):
    questions: list[IngestionQuestion]
    filters: RecommendationFilters | None = None


class IngestionResult(BaseModel):
    question_id: str | None = None
    status: str
    errors: list[str] | None = None
    metadata: dict[str, object] | None = None


class IngestionAudit(BaseModel):
    total: int
    success: int
    failed: int


class IngestionResponse(BaseModel):
    items: list[IngestionResult]
    audit: IngestionAudit
