from enum import Enum
from pydantic import BaseModel


class ValidationStatus(str, Enum):
    accepted = "accepted"
    rejected = "rejected"


class ValidationIssue(BaseModel):
    code: str
    message: str


class ValidationResult(BaseModel):
    status: ValidationStatus
    issues: list[ValidationIssue]
