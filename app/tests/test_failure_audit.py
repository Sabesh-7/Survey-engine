import asyncio

import pytest

from app.schemas.recommendations import RecommendationRequest
from app.schemas.retrieval import RecommendationFilters
from app.services.classification_service import ClassificationService
from app.services.embedding_service import EmbeddingService
from app.services.retrieval_service import QuestionRetrievalService


class FailRepo:
    async def search_semantic(self, *args, **kwargs):
        raise RuntimeError("database_unavailable")


def test_database_unavailable_is_audited(audit_service, metrics_service, embedding_client, embedding_repository, gap_service, validation_service):
    service = QuestionRetrievalService(
        repository=FailRepo(),
        embedder=EmbeddingService(embedding_client, embedding_repository),
        classifier=ClassificationService(),
        gap_detector=gap_service,
        generator=type("Gen", (), {"generate": lambda self, payload: None})(),
        validator=validation_service,
        audit_service=audit_service,
        metrics=metrics_service,
    )
    with pytest.raises(RuntimeError):
        asyncio.run(service.recommend(RecommendationRequest(prompt="Employment survey", filters=RecommendationFilters(language="en"))))
    assert any(item["status"] == "failed" for item in audit_service._repository.items)
