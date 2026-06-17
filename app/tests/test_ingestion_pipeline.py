import asyncio

from types import SimpleNamespace

from app.schemas.ingestion import IngestionQuestion, IngestionRequest
from app.services.question_ingestion_service import QuestionIngestionService


class IngestionQuestionRepository:
    def __init__(self):
        self.created = []

    def create_question(self, payload):
        question_id = f"q-{len(self.created) + 1}"
        self.created.append(payload)
        return SimpleNamespace(question_id=question_id)


class IngestionClassificationRepository:
    def __init__(self):
        self.calls = []

    def add_classifications(self, question_id, tags, codes):
        self.calls.append({"question_id": question_id, "tags": tags, "codes": codes})


def test_ingestion_embedding_storage(audit_service):
    question_repo = IngestionQuestionRepository()
    classification_repo = IngestionClassificationRepository()
    from app.tests.conftest import FakeEmbeddingClient, FakeEmbeddingRepository
    from app.services.embedding_service import EmbeddingService

    embedding_repo = FakeEmbeddingRepository()
    embedding_service = EmbeddingService(FakeEmbeddingClient([0.1, 0.2, 0.3, 0.4] + [0.0] * 1020), embedding_repo)
    service = QuestionIngestionService(
        session=type("S", (), {"begin": lambda self: __import__("app.tests.conftest", fromlist=["_DummyContext"])._DummyContext()})(),
        question_repository=question_repo,
        classification_repository=classification_repo,
        embedding_service=embedding_service,
        audit_service=audit_service,
    )
    response = asyncio.run(
        service.ingest(
            IngestionRequest(
                questions=[
                    IngestionQuestion(
                        text="What is your occupation?",
                        language="en",
                        category="employment",
                        source="historical",
                        classification_codes=["EMP"],
                        tags=["work"],
                    )
                ]
            )
        )
    )
    assert response.audit.success == 1
    assert embedding_repo.stored
