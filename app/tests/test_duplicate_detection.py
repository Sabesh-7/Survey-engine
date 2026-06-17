import asyncio

from app.schemas.duplicates import DuplicateDetectionRequest


def test_duplicate_detection_returns_match(duplicate_detector):
    result = asyncio.run(
        duplicate_detector.detect(
            DuplicateDetectionRequest(question_text="What is your occupation?", language="en", top_k=5)
        )
    )
    assert result.duplicates
    assert result.duplicates[0].match_type.value == "exact_or_near_exact"
