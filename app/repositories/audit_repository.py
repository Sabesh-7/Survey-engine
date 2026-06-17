from datetime import datetime, timezone

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models.ai_run import AiRun
from app.models.ai_run_item import AiRunItem


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def start_run(
        self,
        run_type: str,
        prompt: str | None,
        language: str | None,
        model_name: str | None,
        request_id: str | None,
        trace_id: str | None,
        input_metadata: dict | None,
    ) -> AiRun:
        run = AiRun(
            run_type=run_type,
            run_status="started",
            prompt=prompt,
            language=language,
            model_name=model_name,
            request_id=request_id,
            trace_id=trace_id,
            input_metadata=input_metadata,
            started_at=datetime.now(timezone.utc),
        )
        self._session.add(run)
        self._session.flush()
        return run

    def add_item(
        self,
        run_id,
        stage: str,
        item_type: str,
        status: str,
        reason: str | None,
        score: float | None,
        payload: dict | None,
    ) -> None:
        item = AiRunItem(
            run_id=run_id,
            stage=stage,
            item_type=item_type,
            status=status,
            reason=reason,
            score=score,
            payload=payload,
        )
        self._session.add(item)

    def finish_run(
        self,
        run_id,
        run_status: str,
        duration_ms: int | None,
        output_metadata: dict | None,
    ) -> None:
        stmt = (
            update(AiRun)
            .where(AiRun.run_id == run_id)
            .values(
                run_status=run_status,
                finished_at=datetime.now(timezone.utc),
                duration_ms=duration_ms,
                output_metadata=output_metadata,
            )
        )
        self._session.execute(stmt)
        self._session.commit()
