import asyncio

from app.schemas.recommendations import RecommendationRequest
from app.schemas.retrieval import RecommendationFilters
from app.services.retrieval_service import QuestionRetrievalService


class RetrievalGenerator:
    def __init__(self):
        self.requests = []

    async def generate(self, payload):
        self.requests.append(payload)
        return type("Resp", (), {"items": []})()


def test_retrieval_filters_and_gaps(question_repository, audit_service, metrics_service, embedding_client, embedding_repository, duplicate_detector_empty, gap_service, validation_service):
    from app.services.embedding_service import EmbeddingService
    from app.services.classification_service import ClassificationService

    service = QuestionRetrievalService(
        repository=question_repository,
        embedder=EmbeddingService(embedding_client, embedding_repository),
        classifier=ClassificationService(),
        gap_detector=gap_service,
        generator=RetrievalGenerator(),
        validator=validation_service,
        audit_service=audit_service,
        metrics=metrics_service,
    )
    result = asyncio.run(
        service.recommend(
            RecommendationRequest(
                prompt="Employment survey for workers",
                top_k=3,
                filters=RecommendationFilters(language="en", categories=["employment"]),
            )
        )
    )
    assert result.items
    assert any(item.category == "employment" for item in result.items)
