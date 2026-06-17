import asyncio

from app.schemas.ingestion import IngestionQuestion, IngestionRequest
from app.services.embedding_service import EmbeddingService
from app.services.question_ingestion_service import QuestionIngestionService


class Session:
    def begin(self):
        return __import__("app.tests.conftest", fromlist=["_DummyContext"])._DummyContext()


class QuestionRepo:
    def __init__(self):
        self.questions = []

    def create_question(self, payload):
        qid = f"q-{len(self.questions)+1}"
        self.questions.append(payload)
        return type("Q", (), {"question_id": qid})()


class ClassificationRepo:
    def __init__(self):
        self.calls = []

    def add_classifications(self, question_id, tags, codes):
        self.calls.append((question_id, tags, codes))


def test_ingestion_to_embedding_and_storage(audit_service):
    from app.tests.conftest import FakeEmbeddingClient, FakeEmbeddingRepository
    session = Session()
    question_repo = QuestionRepo()
    classification_repo = ClassificationRepo()
    embedding_repo = FakeEmbeddingRepository()
    embedding_service = EmbeddingService(FakeEmbeddingClient([0.1, 0.2, 0.3, 0.4] + [0.0] * 1020), embedding_repo)
    service = QuestionIngestionService(session, question_repo, classification_repo, embedding_service, audit_service)
    response = asyncio.run(
        service.ingest(
            IngestionRequest(
                questions=[
                    IngestionQuestion(text="What is your occupation?", language="en", category="employment", source="historical", tags=["work"], classification_codes=["EMP"])
                ]
            )
        )
    )
    assert response.audit.success == 1
    assert embedding_repo.stored
