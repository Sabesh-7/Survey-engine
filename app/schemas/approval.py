from enum import Enum
from pydantic import BaseModel


class ApprovalDecision(str, Enum):
    approved = "approved"
    rejected = "rejected"
    changes_requested = "changes_requested"


class ApprovalRequest(BaseModel):
    question_text: str
    language: str
    decision: ApprovalDecision
    reviewer: str | None = None
    comments: str | None = None
    run_id: str | None = None
    run_item_id: str | None = None
    metadata: dict[str, object] | None = None


class ApprovalResponse(BaseModel):
    review_id: str
    decision: ApprovalDecision
    review_status: str
    comments: str | None = None
