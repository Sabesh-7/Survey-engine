from app.schemas.recommendations import RecommendationRequest, RecommendationResponse
from app.schemas.retrieval import RetrievalReason

from app.core.config import get_settings
from app.core.metrics import MetricsService
from app.repositories.question_repository import QuestionRepository
from app.services.audit_service import AuditService
from app.services.classification_service import ClassificationService
from app.services.embedding_service import EmbeddingService
from app.schemas.generation import GenerationContextQuestion, GenerationRequest
from app.services.gap_detection import GapDetectionService
from app.services.question_generation import QuestionGenerationService
from app.services.question_validation import QuestionValidationService


class QuestionRetrievalService:
    def __init__(
        self,
        repository: QuestionRepository,
        embedder: EmbeddingService,
        classifier: ClassificationService,
        gap_detector: GapDetectionService,
        generator: QuestionGenerationService,
        validator: QuestionValidationService,
        audit_service: AuditService,
        metrics: MetricsService,
    ) -> None:
        self._repository = repository
        self._embedder = embedder
        self._classifier = classifier
        self._gap_detector = gap_detector
        self._generator = generator
        self._validator = validator
        self._audit = audit_service
        self._metrics = metrics
        self._settings = get_settings()

    async def recommend(self, payload: RecommendationRequest) -> RecommendationResponse:
        timer = self._audit.start_timer()
        run = self._audit.start_run(
            run_type="recommendation",
            prompt=payload.prompt,
            language=payload.filters.language if payload.filters else None,
            model_name=self._settings.embeddings_model_name,
            request_id=None,
            trace_id=None,
            input_metadata={
                "top_k": payload.top_k,
                "has_embedding": payload.embedding is not None,
                "filters": payload.filters.model_dump() if payload.filters else None,
            },
        )
        self._metrics.incr("recommendation.requests")
        try:
            filters = payload.filters
            if payload.embedding is None:
                embedding = await self._embedder.embed(
                    text=payload.prompt,
                    language=(filters.language if filters else None) or "",
                )
            else:
                embedding = payload.embedding

            results = await self._repository.search_semantic(
                embedding=embedding,
                top_k=payload.top_k,
                language=filters.language if filters else None,
                sources=filters.sources if filters else None,
                categories=filters.categories if filters else None,
                classification_codes=filters.classification_codes if filters else None,
                model_name=self._embedder.model_name,
            )
            self._audit.add_stage(
                run_id=run.run_id,
                stage="retrieval",
                status="ok",
                payload={"retrieved": len(results)},
            )

            items = [
                {
                    "question_id": row["question_id"],
                    "text": row["text"],
                    "language": row["language"],
                    "category": row["category"],
                    "source": row["source"],
                    "retrieval_reason": RetrievalReason.semantic_match,
                    "metadata": {
                        "match_type": "vector",
                    },
                }
                for row in results
            ]
            gaps = await self._gap_detector.detect(payload.prompt, results)
            self._audit.add_stage(
                run_id=run.run_id,
                stage="gap_detection",
                status="ok",
                payload={"gaps": gaps},
            )
            print("Retrieved:", len(items))
            print("Gaps:", gaps)
            if gaps:
                self._metrics.incr("recommendation.gaps", len(gaps))
            generated_questions = []
            rejected_items = []

            if gaps:
                language = (filters.language if filters else None) or (items[0]["language"] if items else "")
                context = [
                    GenerationContextQuestion(
                        question_id=item["question_id"],
                        text=item["text"],
                        language=item["language"],
                        category=item["category"],
                    )
                    for item in items
                ]
                generation_request = GenerationRequest(
                    language=language,
                    gaps=gaps,
                    retrieved_questions=context,
                    max_questions=payload.top_k,
                )
                generation_response = await self._generator.generate(generation_request)

                self._audit.add_stage(
                    run_id=run.run_id,
                    stage="generation",
                    status="ok",
                    payload={"generated": len(generation_response.items)},
                )
                gap_filtered = []
                gap_rejected = []
                for item in generation_response.items:
                    categories = await self._classifier.classify(
                        item.text,
                        language,
                    )

                    if not any(category in gaps for category in categories):
                        gap_rejected.append(item)
                        continue

                    gap_filtered.append(item)

                # Existing validation
                generated_questions, validation_rejected = await self._validator.validate(
                    gap_filtered,
                    language,
                )

                rejected_items = gap_rejected + validation_rejected

                self._audit.add_stage(
                    run_id=run.run_id,
                    stage="validation",
                    status="ok",
                    payload={
                        "accepted": len(generated_questions),
                        "rejected": len(rejected_items),
                    },
                )
                self._metrics.incr("recommendation.generated", len(generated_questions))
                self._metrics.incr("recommendation.rejected", len(rejected_items))

            self._audit.finish_run(
                run_id=run.run_id,
                run_status="completed",
                duration_ms=self._audit.elapsed_ms(timer),
                output_metadata={
                    "retrieved": len(items),
                    "gaps": gaps,
                    "generated": len(generated_questions),
                    "rejected": len(rejected_items),
                },
            )

            return RecommendationResponse(
                items=items,
                gaps=gaps,
                generated_questions=generated_questions,
                rejected_items=rejected_items,
            )
        except Exception as exc:
            self._audit.add_stage(
                run_id=run.run_id,
                stage="recommendation",
                status="failed",
                reason=str(exc),
                payload={"prompt": payload.prompt},
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="failed",
                duration_ms=self._audit.elapsed_ms(timer),
                output_metadata={"error": str(exc)},
            )
            raise
