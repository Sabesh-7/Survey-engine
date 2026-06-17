from pydantic import BaseModel


class ConfidenceScore(BaseModel):
    score: float
    reason: str | None = None
