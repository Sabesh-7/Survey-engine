import re

from app.schemas.generation import GenerationItem
from app.schemas.validation import (
    ValidationIssue,
    ValidationResult,
    ValidationStatus,
)
from app.services.audit_service import AuditService
from app.services.duplicate_detection import DuplicateDetectionService


class QuestionValidationService:
    def __init__(
        self,
        duplicate_detector: DuplicateDetectionService,
        audit_service: AuditService,
    ) -> None:
        self._duplicate_detector = duplicate_detector
        self._audit = audit_service

    async def validate(
        self,
        items: list[GenerationItem],
        language: str,
    ) -> tuple[list[GenerationItem], list[GenerationItem]]:

        run = self._audit.start_run(
            run_type="validation",
            prompt=None,
            language=language,
            model_name=None,
            request_id=None,
            trace_id=None,
            input_metadata={
                "items": len(items),
                "language": language,
            },
        )

        try:
            accepted: list[GenerationItem] = []
            rejected: list[GenerationItem] = []

            for item in items:

                result = await self._validate_item(
                    item=item,
                    language=language,
                )

                item.metadata = {
                    **(item.metadata or {}),
                    "validation": result.model_dump(),
                }

                self._audit.add_stage(
                    run_id=run.run_id,
                    stage="validation_item",
                    status=result.status.value,
                    reason=",".join(
                        issue.code for issue in result.issues
                    )
                    if result.issues
                    else None,
                    payload={
                        "text": item.text,
                        "issues": result.model_dump(),
                    },
                )

                if result.status == ValidationStatus.accepted:
                    accepted.append(item)
                else:
                    rejected.append(item)

            self._audit.finish_run(
                run_id=run.run_id,
                run_status="completed",
                duration_ms=0,
                output_metadata={
                    "accepted": len(accepted),
                    "rejected": len(rejected),
                },
            )

            return accepted, rejected

        except Exception as exc:

            self._audit.add_stage(
                run_id=run.run_id,
                stage="validation",
                status="failed",
                reason=str(exc),
                payload={"items": len(items)},
            )

            self._audit.finish_run(
                run_id=run.run_id,
                run_status="failed",
                duration_ms=0,
                output_metadata={
                    "error": str(exc),
                },
            )

            raise

    async def _validate_item(
        self,
        item: GenerationItem,
        language: str,
    ) -> ValidationResult:

        issues: list[ValidationIssue] = []

        text = item.text.strip()

        if len(text) < 8:
            issues.append(
                ValidationIssue(
                    code="too_short",
                    message="Question text is too short.",
                )
            )

        if len(text) > 240:
            issues.append(
                ValidationIssue(
                    code="too_long",
                    message="Question text is too long.",
                )
            )

        if not text.endswith("?"):
            issues.append(
                ValidationIssue(
                    code="missing_question_mark",
                    message="Question should end with a question mark.",
                )
            )

        if self._contains_prohibited_request(text):
            issues.append(
                ValidationIssue(
                    code="policy_violation",
                    message="Question may request sensitive data.",
                )
            )

        duplicate_result = await self._duplicate_detector.detect(
            payload=self._build_duplicate_request(
                text=text,
                language=language,
            )
        )

        if duplicate_result.duplicates:
            issues.append(
                ValidationIssue(
                    code="potential_duplicate",
                    message="Potential duplicate detected.",
                )
            )

        status = (
            ValidationStatus.accepted
            if not issues
            else ValidationStatus.rejected
        )

        return ValidationResult(
            status=status,
            issues=issues,
        )

    def _contains_prohibited_request(
        self,
        text: str,
    ) -> bool:

        patterns = [
            r"\bpassword\b",
            r"\bbank\b",
            r"\bcredit\b",
            r"\bdebit\b",
            r"\baccount\b",
            r"\bpan\b",
            r"\baadhaar\b",
            r"\bsocial security\b",
            r"\bssn\b",
        ]

        combined = re.compile(
            "|".join(patterns),
            re.IGNORECASE,
        )

        return bool(combined.search(text))

    def _build_duplicate_request(
        self,
        text: str,
        language: str,
    ):
        from app.schemas.duplicates import DuplicateDetectionRequest

        return DuplicateDetectionRequest(
            question_text=text,
            language=language,
            top_k=5,
        )