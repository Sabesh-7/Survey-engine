from pydantic import BaseModel


class GenerationContextQuestion(BaseModel):
    question_id: str
    text: str
    language: str
    category: str | None = None


class GenerationRequest(BaseModel):
    language: str
    gaps: list[str]
    retrieved_questions: list[GenerationContextQuestion]
    max_questions: int = 5


class GenerationItem(BaseModel):
    text: str
    language: str
    source: str = "ai_generated"
    review_status: str = "pending_review"
    confidence: float
    metadata: dict[str, object] | None = None


class GenerationResponse(BaseModel):
    items: list[GenerationItem]
