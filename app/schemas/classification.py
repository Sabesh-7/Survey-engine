from pydantic import BaseModel


class ClassificationRequest(BaseModel):
    text: str
    language: str


class ClassificationResponse(BaseModel):
    tags: list[str]
    classification_codes: list[str]
