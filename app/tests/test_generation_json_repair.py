import asyncio

from app.schemas.generation import GenerationContextQuestion, GenerationRequest
from app.services.question_generation import QuestionGenerationService


class FakeQwenClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = responses
        self._index = 0

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        if self._index >= len(self._responses):
            return self._responses[-1]
        response = self._responses[self._index]
        self._index += 1
        return response


def _request() -> GenerationRequest:
    return GenerationRequest(
        language="en",
        gaps=["employment"],
        retrieved_questions=[
            GenerationContextQuestion(
                question_id="q1",
                text="What is your occupation?",
                language="en",
                category="employment",
            )
        ],
        max_questions=2,
    )


def test_generation_repair_on_malformed_json() -> None:
    responses = [
        "This is not JSON",
        '[{"text": "What is your primary occupation?", "language": "en", "confidence": 0.82}]',
    ]
    from app.tests.conftest import FakeAuditRepository, FakeAuditService
    service = QuestionGenerationService(llm=FakeQwenClient(responses), audit_service=FakeAuditService(FakeAuditRepository()))
    result = asyncio.run(service.generate(_request()))

    assert len(result.items) == 1
    assert result.items[0].text == "What is your primary occupation?"


def test_generation_extracts_json_from_wrapped_content() -> None:
    responses = [
        "Here you go: [{\"text\": \"How many hours do you work?\", \"language\": \"en\", \"confidence\": 0.7}]",
    ]
    from app.tests.conftest import FakeAuditRepository, FakeAuditService
    service = QuestionGenerationService(llm=FakeQwenClient(responses), audit_service=FakeAuditService(FakeAuditRepository()))
    result = asyncio.run(service.generate(_request()))

    assert len(result.items) == 1
    assert result.items[0].text == "How many hours do you work?"


def test_generation_validation_retry() -> None:
    responses = [
        '[{"text": 123, "language": "en", "confidence": "high"}]',
        '[{"text": "What sector do you work in?", "language": "en", "confidence": 0.6}]',
    ]
    from app.tests.conftest import FakeAuditRepository, FakeAuditService
    service = QuestionGenerationService(llm=FakeQwenClient(responses), audit_service=FakeAuditService(FakeAuditRepository()))
    result = asyncio.run(service.generate(_request()))

    assert len(result.items) == 1
    assert result.items[0].text == "What sector do you work in?"


def test_generation_gives_empty_after_retries() -> None:
    responses = [
        "nonsense",
        "still bad",
        "not json",
    ]
    from app.tests.conftest import FakeAuditRepository, FakeAuditService
    service = QuestionGenerationService(llm=FakeQwenClient(responses), audit_service=FakeAuditService(FakeAuditRepository()))
    result = asyncio.run(service.generate(_request()))

    assert result.items == []
