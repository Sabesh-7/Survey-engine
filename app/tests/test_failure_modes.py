import asyncio

import pytest

from app.schemas.generation import GenerationContextQuestion, GenerationRequest
from app.services.embedding_service import EmbeddingService
from app.services.question_generation import QuestionGenerationService


@pytest.mark.parametrize("embedding", [[1.0, 0.0], [0.1]])
def test_invalid_embedding_dimension_raises_service_error(audit_service, embedding_repository, embedding):
    from app.tests.conftest import FakeEmbeddingClient
    service = EmbeddingService(FakeEmbeddingClient(embedding), embedding_repository)
    with pytest.raises(Exception):
        asyncio.run(service.embed("text", "en"))


def test_qwen_timeout_triggers_failure(audit_service):
    llm = type("LLM", (), {"generate": lambda self, system_prompt, user_prompt, temperature=0.2: (_ for _ in ()).throw(TimeoutError("timeout"))})()
    service = QuestionGenerationService(llm=llm, audit_service=audit_service)
    with pytest.raises(TimeoutError):
        asyncio.run(service.generate(
            GenerationRequest(
                language="en",
                gaps=["migration"],
                retrieved_questions=[GenerationContextQuestion(question_id="q1", text="What is your occupation?", language="en", category="employment")],
                max_questions=2,
            )
        ))
