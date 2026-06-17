from enum import Enum

from pydantic import BaseModel


class IntentType(str, Enum):
    topic_scope = "topic_scope"
    question_request = "question_request"
    update_request = "update_request"
    unknown = "unknown"


class IntentRequest(BaseModel):
    prompt: str
    language: str


class IntentResponse(BaseModel):
    intent: IntentType
    confidence: float
    topics: list[str]
    metadata: dict[str, object] | None = None
