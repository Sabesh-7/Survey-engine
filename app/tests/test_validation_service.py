import asyncio

from app.schemas.generation import GenerationItem
from app.services.question_validation import QuestionValidationService


def test_validation_rejects_low_quality_questions(audit_service, duplicate_detector_empty):
    service = QuestionValidationService(duplicate_detector=duplicate_detector_empty, audit_service=audit_service)
    item = GenerationItem(text="Bad?", language="en", confidence=0.4)
    accepted, rejected = asyncio.run(service.validate([item], "en"))
    assert not accepted
    assert rejected[0].metadata["validation"]["status"] == "rejected"


def test_validation_marks_pending_review(audit_service, duplicate_detector_empty):
    service = QuestionValidationService(duplicate_detector=duplicate_detector_empty, audit_service=audit_service)
    item = GenerationItem(text="Have you migrated in the last five years?", language="en", confidence=0.8)
    accepted, rejected = asyncio.run(service.validate([item], "en"))
    assert accepted[0].review_status == "pending_review"
    assert not rejected
