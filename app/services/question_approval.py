from sqlalchemy.orm import Session

from app.repositories.question_review_repository import QuestionReviewRepository
from app.schemas.approval import ApprovalDecision, ApprovalRequest, ApprovalResponse
from app.services.audit_service import AuditService


class QuestionApprovalService:
    def __init__(
        self,
        session: Session,
        review_repository: QuestionReviewRepository,
        audit_service: AuditService,
    ) -> None:
        self._session = session
        self._reviews = review_repository
        self._audit = audit_service

    def review(self, payload: ApprovalRequest) -> ApprovalResponse:
        run = self._audit.start_run(
            run_type="approval",
            prompt=payload.question_text,
            language=payload.language,
            model_name=None,
            request_id=None,
            trace_id=None,
            input_metadata=payload.model_dump(),
        )

        with self._session.begin():
            review = self._reviews.create_review(
                question_text=payload.question_text,
                language=payload.language,
                decision=payload.decision.value,
                reviewer=payload.reviewer,
                comments=payload.comments,
                run_id=payload.run_id,
                run_item_id=payload.run_item_id,
                metadata=payload.metadata,
            )

        self._audit.add_stage(
            run_id=run.run_id,
            stage="approval_decision",
            status=payload.decision.value,
            reason=payload.comments,
            payload={
                "question_text": payload.question_text,
                "decision": payload.decision.value,
                "reviewer": payload.reviewer,
            },
        )
        self._audit.finish_run(
            run_id=run.run_id,
            run_status="completed",
            duration_ms=0,
            output_metadata={"decision": payload.decision.value, "review_id": str(review.review_id)},
        )

        review_status = "approved" if payload.decision == ApprovalDecision.approved else "rejected"
        return ApprovalResponse(
            review_id=str(review.review_id),
            decision=payload.decision,
            review_status=review_status,
            comments=payload.comments,
        )
