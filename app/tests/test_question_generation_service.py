import asyncio

from app.schemas.generation import GenerationContextQuestion, GenerationRequest
from app.services.question_generation import QuestionGenerationService


def test_generation_uses_gaps_only(audit_service):
    llm = type(
        "LLM",
        (),
        {"generate": lambda self, system_prompt, user_prompt, temperature=0.2: asyncio.sleep(0, result='[{"text": "Have you migrated in the last five years?", "language": "en", "confidence": 0.8}]')},
    )()
    service = QuestionGenerationService(llm=llm, audit_service=audit_service)
    result = asyncio.run(
        service.generate(
            GenerationRequest(
                language="en",
                gaps=["migration"],
                retrieved_questions=[GenerationContextQuestion(question_id="q1", text="What is your occupation?", language="en", category="employment")],
                max_questions=2,
            )
        )
    )
    assert result.items[0].source == "ai_generated"
