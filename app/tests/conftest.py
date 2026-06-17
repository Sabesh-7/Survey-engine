import json
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.core.config import get_settings
from app.schemas.approval import ApprovalDecision, ApprovalRequest
from app.schemas.duplicates import DuplicateCandidate, DuplicateDetectionRequest, DuplicateDetectionResponse, DuplicateMatchType
from app.schemas.generation import GenerationContextQuestion, GenerationItem, GenerationRequest, GenerationResponse
from app.schemas.intent import IntentRequest
from app.schemas.recommendations import RecommendationRequest
from app.schemas.retrieval import RecommendationFilters, RetrievalReason
from app.schemas.validation import ValidationIssue, ValidationResult, ValidationStatus
from app.services.audit_service import AuditService
from app.services.duplicate_detection import DuplicateDetectionService
from app.services.gap_detection import GapDetectionService
from app.services.intent_analyzer import IntentAnalyzerService
from app.services.question_approval import QuestionApprovalService
from app.services.question_generation import QuestionGenerationService
from app.services.question_validation import QuestionValidationService


FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "multilingual_questions.json"


def _pad_vector(seed: list[float], dim: int = 1024) -> list[float]:
    vector = [0.0] * dim
    for index, value in enumerate(seed):
        if index < dim:
            vector[index] = value
    return vector


@pytest.fixture(scope="session")
def multilingual_dataset() -> list[dict]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture()
def sample_context_questions(multilingual_dataset: list[dict]) -> list[GenerationContextQuestion]:
    return [
        GenerationContextQuestion(
            question_id=item["question_id"],
            text=item["text"],
            language=item["language"],
            category=item["category"],
        )
        for item in multilingual_dataset
        if item["category"] in {"employment", "education", "health"}
    ]


class FakeRun:
    def __init__(self, run_id: str = "run-1") -> None:
        self.run_id = run_id


class FakeAuditRepository:
    def __init__(self, fail_on_add: bool = False) -> None:
        self.runs: list[dict] = []
        self.items: list[dict] = []
        self.finished: list[dict] = []
        self.fail_on_add = fail_on_add

    def start_run(self, **kwargs):
        run = SimpleNamespace(run_id=f"run-{len(self.runs) + 1}", **kwargs)
        self.runs.append(kwargs)
        return run

    def add_item(self, **kwargs) -> None:
        if self.fail_on_add:
            raise RuntimeError("audit_write_failed")
        self.items.append(kwargs)

    def finish_run(self, **kwargs) -> None:
        if self.fail_on_add:
            raise RuntimeError("audit_write_failed")
        self.finished.append(kwargs)


class FakeAuditService(AuditService):
    def __init__(self, repository: FakeAuditRepository) -> None:
        super().__init__(repository)  # type: ignore[arg-type]
        self._repository = repository


@dataclass
class FakeQuestionRepository:
    rows: list[dict] = field(default_factory=list)
    fail_on_search: bool = False
    fail_on_create: bool = False

    def create_question(self, payload):
        if self.fail_on_create:
            raise RuntimeError("database_unavailable")
        question_id = f"q-{len(self.rows) + 1}"
        row = {
            "question_id": question_id,
            "text": payload.text,
            "language": payload.language,
            "category": payload.category,
            "source": payload.source,
            "classification_codes": payload.classification_codes or [],
            "embedding": None,
        }
        self.rows.append(row)
        return SimpleNamespace(question_id=question_id)

    async def search_semantic(self, embedding, top_k, language=None, sources=None, categories=None, classification_codes=None, model_name="bge-m3"):
        if self.fail_on_search:
            raise RuntimeError("database_unavailable")
        results = list(self.rows)
        if language:
            results = [row for row in results if row["language"] == language]
        if sources:
            results = [row for row in results if row["source"] in sources]
        if categories:
            results = [row for row in results if row["category"] in categories]
        if classification_codes:
            results = [row for row in results if set(row.get("classification_codes", [])) & set(classification_codes)]
        return [
            {
                "question_id": row["question_id"],
                "text": row["text"],
                "language": row["language"],
                "category": row["category"],
                "source": row["source"],
                "vector_similarity": _cosine_proxy(embedding, row.get("embedding") or embedding),
            }
            for row in results[:top_k]
        ]


@dataclass
class FakeEmbeddingRepository:
    stored: list[dict] = field(default_factory=list)
    fail_on_store: bool = False

    def upsert_question_embedding(self, question_id, model_name, embedding, commit=True):
        if self.fail_on_store:
            raise RuntimeError("missing_embeddings")
        self.stored.append({"question_id": question_id, "model_name": model_name, "embedding": embedding, "commit": commit})

    def upsert_question_embeddings(self, question_embeddings, model_name, commit=True):
        if self.fail_on_store:
            raise RuntimeError("missing_embeddings")
        for item in question_embeddings:
            self.stored.append({"question_id": item["question_id"], "model_name": model_name, "embedding": item["embedding"], "commit": commit})


class FakeEmbeddingClient:
    def __init__(self, embedding: list[float], fail: Exception | None = None) -> None:
        self.embedding = embedding
        self.fail = fail
        self.calls: list[dict] = []

    async def embed(self, text: str, language: str) -> list[float]:
        self.calls.append({"text": text, "language": language})
        if self.fail:
            raise self.fail
        return self.embedding

    async def embed_batch(self, texts, languages=None):
        return [self.embedding for _ in texts]

    async def warm_up(self):
        return None


class FakeLLMClient:
    def __init__(self, responses: list[str], fail: Exception | None = None, timeout_error: bool = False) -> None:
        self.responses = responses
        self.calls: list[dict] = []
        self.fail = fail
        self.timeout_error = timeout_error
        self.index = 0

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt, "temperature": temperature})
        if self.timeout_error:
            raise TimeoutError("Qwen timeout")
        if self.fail:
            raise self.fail
        if self.index >= len(self.responses):
            return self.responses[-1]
        response = self.responses[self.index]
        self.index += 1
        return response


class FakeDuplicateDetector:
    def __init__(self, duplicates: list[DuplicateCandidate] | None = None, fail: bool = False) -> None:
        self.duplicates = duplicates or []
        self.fail = fail
        self.requests: list[dict] = []

    async def detect(self, payload: DuplicateDetectionRequest) -> DuplicateDetectionResponse:
        self.requests.append(payload.model_dump())
        if self.fail:
            raise RuntimeError("duplicate_detection_failed")
        return DuplicateDetectionResponse(duplicates=self.duplicates)


class FakeReviewRepository:
    def __init__(self) -> None:
        self.reviews: list[dict] = []

    def create_review(self, **kwargs):
        review_id = f"review-{len(self.reviews) + 1}"
        self.reviews.append({"review_id": review_id, **kwargs})
        return SimpleNamespace(review_id=review_id)


class FakeSession:
    def __init__(self, fail_begin: bool = False) -> None:
        self.fail_begin = fail_begin
        self.begins = 0

    def begin(self):
        if self.fail_begin:
            raise RuntimeError("database_unavailable")
        self.begins += 1
        return _DummyContext()


class _DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeMetricsService:
    def __init__(self) -> None:
        self.counts: dict[str, int] = {}

    def incr(self, key: str, value: int = 1) -> None:
        self.counts[key] = self.counts.get(key, 0) + value


@pytest.fixture()
def audit_repository() -> FakeAuditRepository:
    return FakeAuditRepository()


@pytest.fixture()
def audit_service(audit_repository: FakeAuditRepository) -> FakeAuditService:
    return FakeAuditService(audit_repository)


@pytest.fixture()
def embedding_repository() -> FakeEmbeddingRepository:
    return FakeEmbeddingRepository()


@pytest.fixture()
def embedding_client() -> FakeEmbeddingClient:
    return FakeEmbeddingClient(_pad_vector([0.99, 0.01]))


@pytest.fixture()
def llm_client() -> FakeLLMClient:
    return FakeLLMClient([
        '[{"text": "How many hours do you work per week?", "language": "en", "confidence": 0.81}]'
    ])


@pytest.fixture()
def question_repository(multilingual_dataset: list[dict]) -> FakeQuestionRepository:
    rows = []
    for item in multilingual_dataset:
        rows.append(
            {
                "question_id": item["question_id"],
                "text": item["text"],
                "language": item["language"],
                "category": item["category"],
                "source": item["source"],
                "classification_codes": item["classification_codes"],
                "embedding": item["embedding"],
            }
        )
    return FakeQuestionRepository(rows=rows)


@pytest.fixture()
def review_repository() -> FakeReviewRepository:
    return FakeReviewRepository()


@pytest.fixture()
def fake_session() -> FakeSession:
    return FakeSession()


@pytest.fixture()
def metrics_service() -> FakeMetricsService:
    return FakeMetricsService()


@pytest.fixture()
def duplicate_detector() -> FakeDuplicateDetector:
    return FakeDuplicateDetector(
        duplicates=[
            DuplicateCandidate(
                question_id="q-employment-en-1",
                text="What is your occupation?",
                language="en",
                category="employment",
                source="historical",
                similarity_score=0.99,
                match_type=DuplicateMatchType.exact_or_near_exact,
                metadata={"method": "vector_cosine"},
            )
        ]
    )


@pytest.fixture()
def duplicate_detector_empty() -> FakeDuplicateDetector:
    return FakeDuplicateDetector(duplicates=[])


@pytest.fixture()
def intent_service(audit_service: FakeAuditService) -> IntentAnalyzerService:
    return IntentAnalyzerService(audit_service)


@pytest.fixture()
def gap_service(audit_service: FakeAuditService) -> GapDetectionService:
    return GapDetectionService(audit_service)


@pytest.fixture()
def generation_service(audit_service: FakeAuditService, llm_client: FakeLLMClient) -> QuestionGenerationService:
    return QuestionGenerationService(llm=llm_client, audit_service=audit_service)


@pytest.fixture()
def validation_service(audit_service: FakeAuditService, duplicate_detector_empty: FakeDuplicateDetector) -> QuestionValidationService:
    return QuestionValidationService(duplicate_detector=duplicate_detector_empty, audit_service=audit_service)


@pytest.fixture()
def approval_service(fake_session: FakeSession, review_repository: FakeReviewRepository, audit_service: FakeAuditService) -> QuestionApprovalService:
    return QuestionApprovalService(
        session=fake_session,
        review_repository=review_repository,
        audit_service=audit_service,
    )


@pytest.fixture()
def recommendation_request() -> RecommendationRequest:
    return RecommendationRequest(
        prompt="Employment survey for workers in Tamil Nadu",
        top_k=5,
        filters=RecommendationFilters(language="en", sources=["historical", "standard"], categories=["employment"]),
    )


@pytest.fixture()
def multilingual_prompts() -> dict[str, str]:
    return {
        "employment_en": "Employment survey for workers",
        "employment_ta": "வேலைவாய்ப்பு கணக்கெடுப்பு",
        "migration_en": "Please add migration related questions",
        "health_hi": "स्वास्थ्य सर्वेक्षण",
    }


def _cosine_proxy(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    size = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(size))
    return float(min(1.0, max(0.0, dot)))
