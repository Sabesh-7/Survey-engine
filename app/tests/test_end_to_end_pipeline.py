import asyncio

from app.schemas.recommendations import RecommendationRequest
from app.schemas.retrieval import RecommendationFilters
from app.schemas.generation import GenerationItem
from app.services.retrieval_service import QuestionRetrievalService
from app.services.classification_service import ClassificationService
from app.services.embedding_service import EmbeddingService


class PipelineGenerator:
    async def generate(self, payload):
        return type(
            "Resp",
            (),
            {
                "items": [
                    GenerationItem(
                        text="Have you migrated in the last five years?",
                        language=payload.language,
                        source="ai_generated",
                        review_status="pending_review",
                        confidence=0.8,
                        metadata={},
                    )
                ]
            },
        )()


def test_end_to_end_employment_and_migration_flow(question_repository, audit_service, metrics_service, embedding_client, embedding_repository, gap_service, validation_service):
    service = QuestionRetrievalService(
        repository=question_repository,
        embedder=EmbeddingService(embedding_client, embedding_repository),
        classifier=ClassificationService(),
        gap_detector=gap_service,
        generator=PipelineGenerator(),
        validator=validation_service,
        audit_service=audit_service,
        metrics=metrics_service,
    )
    result = asyncio.run(
        service.recommend(
            RecommendationRequest(
                    prompt="Please include migration related questions",
                top_k=5,
                    filters=RecommendationFilters(language="en", categories=["employment"]),
            )
        )
    )
    assert "migration" in result.gaps
    assert all(item.review_status == "pending_review" for item in result.generated_questions)
