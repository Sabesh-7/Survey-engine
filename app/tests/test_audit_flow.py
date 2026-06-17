import asyncio

from app.schemas.recommendations import RecommendationRequest
from app.schemas.retrieval import RecommendationFilters
from app.services.classification_service import ClassificationService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import QuestionRetrievalService


class NoopGenerator:
    async def generate(self, payload):
        return type("Resp", (), {"items": []})()


def test_audit_contains_pipeline_records(question_repository, audit_service, metrics_service, embedding_client, embedding_repository, gap_service, validation_service):
    service = QuestionRetrievalService(
        repository=question_repository,
        embedder=EmbeddingService(embedding_client, embedding_repository),
        classifier=ClassificationService(),
        gap_detector=gap_service,
        generator=NoopGenerator(),
        validator=validation_service,
        audit_service=audit_service,
        metrics=metrics_service,
    )
    asyncio.run(
        service.recommend(
            RecommendationRequest(
                prompt="Employment survey for workers",
                top_k=3,
                filters=RecommendationFilters(language="en", categories=["employment"]),
            )
        )
    )
    stages = [item["stage"] for item in audit_service._repository.items]
    assert "retrieval" in stages
    assert "gap_detection" in stages
