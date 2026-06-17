from app.core.config import get_settings
from app.services.audit_service import AuditService
from app.repositories.question_repository import QuestionRepository
from app.schemas.duplicates import (
    DuplicateCandidate,
    DuplicateDetectionRequest,
    DuplicateDetectionResponse,
    DuplicateMatchType,
)
from app.services.embedding_service import EmbeddingService


class DuplicateDetectionService:
    def __init__(self, embedder: EmbeddingService, repository: QuestionRepository, audit_service: AuditService) -> None:
        self._embedder = embedder
        self._repository = repository
        self._settings = get_settings()
        self._audit = audit_service

    async def detect(self, payload: DuplicateDetectionRequest) -> DuplicateDetectionResponse:
        run = self._audit.start_run(
            run_type="duplicate_detection",
            prompt=payload.question_text,
            language=payload.language,
            model_name=self._settings.embeddings_model_name,
            request_id=None,
            trace_id=None,
            input_metadata=payload.model_dump(),
        )
        try:
            filters = payload.filters
            language = payload.language or (filters.language if filters else None)
            embedding = await self._embedder.embed(text=payload.question_text, language=language or "")

            results = await self._repository.search_semantic(
                embedding=embedding,
                top_k=payload.top_k,
                language=filters.language if filters else None,
                sources=filters.sources if filters else None,
                categories=filters.categories if filters else None,
                classification_codes=filters.classification_codes if filters else None,
            )

            duplicates: list[DuplicateCandidate] = []
            for row in results:
                score = row["vector_similarity"]
                if score < self._settings.duplicate_semantic_threshold:
                    continue

                match_type = (
                    DuplicateMatchType.exact_or_near_exact
                    if score >= self._settings.duplicate_exact_threshold
                    else DuplicateMatchType.semantic_duplicate
                )

                duplicates.append(
                    DuplicateCandidate(
                        question_id=row["question_id"],
                        text=row["text"],
                        language=row["language"],
                        category=row["category"],
                        source=row["source"],
                        similarity_score=score,
                        match_type=match_type,
                        metadata={
                            "method": "vector_cosine",
                        },
                    )
                )

            self._audit.add_stage(
                run_id=run.run_id,
                stage="duplicate_detection",
                status="ok",
                payload={"candidates": len(results), "duplicates": len(duplicates)},
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="completed",
                duration_ms=0,
                output_metadata={"duplicates": len(duplicates)},
            )

            return DuplicateDetectionResponse(duplicates=duplicates)
        except Exception as exc:
            self._audit.add_stage(
                run_id=run.run_id,
                stage="duplicate_detection",
                status="failed",
                reason=str(exc),
                payload={"question_text": payload.question_text},
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="failed",
                duration_ms=0,
                output_metadata={"error": str(exc)},
            )
            raise
