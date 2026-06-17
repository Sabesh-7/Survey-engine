from functools import lru_cache

from app.ai.embeddings.bge_m3_client import BgeM3Client
from app.ai.llm.qwen_client import QwenClient
from app.core.metrics import MetricsService
from app.database.session import get_db_session
from app.repositories.audit_repository import AuditRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.question_classification_repository import QuestionClassificationRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.question_review_repository import QuestionReviewRepository
from app.services.classification_service import ClassificationService
from app.services.audit_service import AuditService
from app.services.duplicate_detection import DuplicateDetectionService
from app.services.embedding_service import EmbeddingService
from app.services.gap_detection import GapDetectionService
from app.services.intent_analyzer import IntentAnalyzerService
from app.services.question_ingestion_service import QuestionIngestionService
from app.services.question_generation import QuestionGenerationService
from app.services.question_approval import QuestionApprovalService
from app.services.question_validation import QuestionValidationService
from app.services.retrieval_service import QuestionRetrievalService
@lru_cache
def get_metrics_service() -> MetricsService:
    return MetricsService()


def get_audit_service() -> AuditService:
    return AuditService(AuditRepository(get_db_session()))


@lru_cache
def get_embedding_client() -> BgeM3Client:
    return BgeM3Client()


def get_llm_client() -> QwenClient:
    return QwenClient()


def get_question_repository() -> QuestionRepository:
    return QuestionRepository(get_db_session())


def get_question_classification_repository() -> QuestionClassificationRepository:
    return QuestionClassificationRepository(get_db_session())


def get_embedding_repository() -> EmbeddingRepository:
    return EmbeddingRepository(get_db_session())


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService(get_embedding_client(), get_embedding_repository())


def get_gap_detector() -> GapDetectionService:
    return GapDetectionService(get_audit_service())


def get_classifier() -> ClassificationService:
    return ClassificationService()


def get_intent_analyzer() -> IntentAnalyzerService:
    return IntentAnalyzerService(get_audit_service())


def get_question_retrieval() -> QuestionRetrievalService:
    return QuestionRetrievalService(
        repository=get_question_repository(),
        embedder=get_embedding_service(),
        classifier=get_classifier(),
        gap_detector=get_gap_detector(),
        generator=get_question_generator(),
        validator=get_question_validator(),
        audit_service=get_audit_service(),
        metrics=get_metrics_service(),
    )


def get_duplicate_detector() -> DuplicateDetectionService:
    return DuplicateDetectionService(
        embedder=get_embedding_service(),
        repository=get_question_repository(),
        audit_service=get_audit_service(),
    )


def get_question_generator() -> QuestionGenerationService:
    return QuestionGenerationService(llm=get_llm_client(), audit_service=get_audit_service())


def get_question_validator() -> QuestionValidationService:
    return QuestionValidationService(
        duplicate_detector=get_duplicate_detector(),
        audit_service=get_audit_service(),
    )


def get_question_review_repository() -> QuestionReviewRepository:
    return QuestionReviewRepository(get_db_session())


def get_question_approval_service() -> QuestionApprovalService:
    session = get_db_session()
    return QuestionApprovalService(
        session=session,
        review_repository=QuestionReviewRepository(session),
        audit_service=get_audit_service(),
    )


def get_question_ingestion_service() -> QuestionIngestionService:
    session = get_db_session()
    return QuestionIngestionService(
        session=session,
        question_repository=QuestionRepository(session),
        classification_repository=QuestionClassificationRepository(session),
        embedding_service=EmbeddingService(get_embedding_client(), EmbeddingRepository(session)),
        audit_service=get_audit_service(),
    )
