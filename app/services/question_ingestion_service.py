from sqlalchemy.orm import Session

from app.schemas.ingestion import IngestionRequest, IngestionResponse, IngestionResult
from app.services.embedding_service import EmbeddingService
from app.repositories.question_repository import QuestionRepository
from app.repositories.question_classification_repository import QuestionClassificationRepository
from app.services.audit_service import AuditService
from app.utils.errors import ServiceError


class QuestionIngestionService:
    def __init__(
        self,
        session: Session,
        question_repository: QuestionRepository,
        classification_repository: QuestionClassificationRepository,
        embedding_service: EmbeddingService,
        audit_service: AuditService,
    ) -> None:
        self._session = session
        self._question_repository = question_repository
        self._classification_repository = classification_repository
        self._embedding_service = embedding_service
        self._audit = audit_service

    async def ingest(self, payload: IngestionRequest) -> IngestionResponse:
        run = self._audit.start_run(
            run_type="ingestion",
            prompt=None,
            language=None,
            model_name=self._embedding_service.model_name,
            request_id=None,
            trace_id=None,
            input_metadata=payload.model_dump(),
        )
        try:
            items: list[IngestionResult] = []
            success = 0
            failed = 0

            for question in payload.questions:
                errors = self._validate(question)
                if errors:
                    failed += 1
                    self._audit.add_stage(
                        run_id=run.run_id,
                        stage="ingestion_validation",
                        status="rejected",
                        reason=",".join(errors),
                        payload={"question": question.model_dump(), "errors": errors},
                    )
                    items.append(IngestionResult(status="rejected", errors=errors))
                    continue

                try:
                    with self._session.begin():
                        created = self._question_repository.create_question(question)
                        if question.tags or question.classification_codes:
                            self._classification_repository.add_classifications(
                                question_id=str(created.question_id),
                                tags=question.tags or [],
                                codes=question.classification_codes or [],
                            )

                        embedding = await self._embedding_service.embed(
                            text=question.text,
                            language=question.language,
                        )
                        self._embedding_service.store_question_embedding(
                            question_id=str(created.question_id),
                            embedding=embedding,
                            commit=False,
                        )

                    self._audit.add_stage(
                        run_id=run.run_id,
                        stage="ingestion_persist",
                        status="ok",
                        payload={"question_id": str(created.question_id), "language": question.language},
                    )

                    success += 1
                    items.append(
                        IngestionResult(
                            question_id=str(created.question_id),
                            status="ingested",
                            metadata={
                                "embedding_model": self._embedding_service.model_name,
                            },
                        )
                    )
                except ServiceError as exc:
                    failed += 1
                    self._audit.add_stage(
                        run_id=run.run_id,
                        stage="ingestion_persist",
                        status="failed",
                        reason=str(exc),
                        payload={"question": question.model_dump()},
                    )
                    items.append(IngestionResult(status="failed", errors=[str(exc)]))
                except Exception as exc:
                    print("INGESTION ERROR:", repr(exc))

                    failed += 1

                    self._audit.add_stage(
                        run_id=run.run_id,
                        stage="ingestion_persist",
                        status="failed",
                        reason=str(exc),
                        payload={"question": question.model_dump()},
                    )

                    items.append(
                        IngestionResult(
                            status="failed",
                            errors=[str(exc)],
                        )
                    )

            self._audit.finish_run(
                run_id=run.run_id,
                run_status="completed",
                duration_ms=0,
                output_metadata={"total": len(payload.questions), "success": success, "failed": failed},
            )

            return IngestionResponse(
                items=items,
                audit={
                    "total": len(payload.questions),
                    "success": success,
                    "failed": failed,
                },
            )
        except Exception as exc:
            self._audit.add_stage(
                run_id=run.run_id,
                stage="ingestion",
                status="failed",
                reason=str(exc),
                payload={"total": len(payload.questions)},
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="failed",
                duration_ms=0,
                output_metadata={"error": str(exc)},
            )
            raise

    def _validate(self, question) -> list[str]:
        errors: list[str] = []
        if not question.text or not question.text.strip():
            errors.append("text_required")
        if not question.language or not question.language.strip():
            errors.append("language_required")
        if not question.source:
            errors.append("source_required")
        elif question.source not in {"standard", "historical", "ai_generated", "manual"}:
            errors.append("source_invalid")
        return errors
