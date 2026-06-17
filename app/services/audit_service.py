import time

from app.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self._repository = repository

    def start_run(
        self,
        run_type: str,
        prompt: str | None,
        language: str | None,
        model_name: str | None,
        request_id: str | None,
        trace_id: str | None,
        input_metadata: dict | None,
    ):
        run = self._repository.start_run(
            run_type=run_type,
            prompt=prompt,
            language=language,
            model_name=model_name,
            request_id=request_id,
            trace_id=trace_id,
            input_metadata=input_metadata,
        )
        return run

    def add_stage(
        self,
        run_id,
        stage: str,
        status: str,
        payload: dict | None = None,
        reason: str | None = None,
        score: float | None = None,
        item_type: str = "stage",
    ) -> None:
        self._repository.add_item(
            run_id=run_id,
            stage=stage,
            item_type=item_type,
            status=status,
            reason=reason,
            score=score,
            payload=payload,
        )

    def finish_run(
        self,
        run_id,
        run_status: str,
        duration_ms: int | None,
        output_metadata: dict | None,
    ) -> None:
        self._repository.finish_run(
            run_id=run_id,
            run_status=run_status,
            duration_ms=duration_ms,
            output_metadata=output_metadata,
        )

    def start_timer(self) -> float:
        return time.perf_counter()

    def elapsed_ms(self, start: float) -> int:
        return int((time.perf_counter() - start) * 1000)
