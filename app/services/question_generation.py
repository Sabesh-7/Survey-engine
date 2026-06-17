import json

from pydantic import TypeAdapter, ValidationError

from app.schemas.generation import GenerationItem, GenerationRequest, GenerationResponse

from app.ai.llm.qwen_client import QwenClient
from app.services.audit_service import AuditService


class QuestionGenerationService:
    def __init__(self, llm: QwenClient, audit_service: AuditService) -> None:
        self._llm = llm
        self._audit = audit_service

    async def generate(self, payload: GenerationRequest) -> GenerationResponse:
        if not payload.gaps:
            return GenerationResponse(items=[])

        run = self._audit.start_run(
            run_type="generation",
            prompt=None,
            language=payload.language,
            model_name=None,
            request_id=None,
            trace_id=None,
            input_metadata=payload.model_dump(),
        )
        schema = (
            "[{\"text\": \"string\", \"language\": \"string\", \"confidence\": 0.0}]"
        )
        system_prompt = f"""
        You are a survey question generation engine.
        Generate survey questions ONLY for the categories listed in gaps.
        STRICT RULES:
        - Every generated question MUST belong to one of the gap categories.
        - Do NOT generate questions for categories not listed in gaps.
        - Do NOT generate questions similar to retrieved questions.
        - Do NOT generate duplicate questions.
        - Questions must be short, clear and survey-ready.
        - Questions must end with a question mark.
        - Return ONLY valid JSON.
        - No explanations.
        - No markdown.
        Schema:
        {schema}
        """
        retrieved = [
            {
                "text": item.text,
                "language": item.language,
                "category": item.category,
            }
            for item in payload.retrieved_questions
        ]

        user_prompt = (
            "Gaps:\n"
            f"{json.dumps(payload.gaps, ensure_ascii=True)}\n\n"
            "Retrieved questions:\n"
            f"{json.dumps(retrieved, ensure_ascii=True)}\n\n"
            f"Target language: {payload.language}\n"
            f"Max questions: {payload.max_questions}\n"
        )

        try:
            raw = await self._llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)
            items, parsed_ok = await self._parse_items_with_retry(raw, system_prompt, payload.language, run.run_id)

            self._audit.add_stage(
                run_id=run.run_id,
                stage="generation",
                status="ok" if parsed_ok else "empty",
                payload={"generated": len(items)},
            )
            if parsed_ok:
                self._audit.finish_run(
                    run_id=run.run_id,
                    run_status="completed",
                    duration_ms=0,
                    output_metadata={"generated": len(items)},
                )

            return GenerationResponse(items=items)
        except Exception as exc:
            self._audit.add_stage(
                run_id=run.run_id,
                stage="generation",
                status="failed",
                reason=str(exc),
                payload={"gaps": payload.gaps},
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="failed",
                duration_ms=0,
                output_metadata={"error": str(exc)},
            )
            raise

    async def _parse_items_with_retry(
        self,
        raw: str,
        system_prompt: str,
        language: str,
        run_id,
        max_attempts: int = 3,
    ) -> tuple[list[GenerationItem], bool]:
        last_error: str | None = None
        candidate = raw

        for attempt in range(max_attempts):
            parsed = self._extract_json(candidate)
            if parsed is not None:
                items = self._validate_items(parsed, language)
                if items is not None:
                    self._audit.add_stage(
                        run_id=run_id,
                        stage="generation_parse",
                        status="ok",
                        payload={"attempt": attempt + 1, "items": len(items)},
                    )
                    return items, True
                last_error = "validation_failed"
            else:
                last_error = "json_parse_failed"

            if attempt < max_attempts - 1:
                self._audit.add_stage(
                    run_id=run_id,
                    stage="generation_repair",
                    status="retrying",
                    reason=last_error,
                    payload={"attempt": attempt + 1},
                )
                repair_prompt = (
                    "Repair the following content into a strict JSON array of objects with fields: "
                    "text, language, confidence. Return JSON only.\n\n"
                    f"Content:\n{candidate}"
                )
                candidate = await self._llm.generate(
                    system_prompt=system_prompt,
                    user_prompt=repair_prompt,
                    temperature=0.1,
                )

        if last_error:
            self._audit.add_stage(
                run_id=run_id,
                stage="generation_parse",
                status="failed",
                reason=last_error,
                payload={"attempts": max_attempts},
            )
            self._audit.finish_run(
                run_id=run_id,
                run_status="failed",
                duration_ms=0,
                output_metadata={"reason": last_error},
            )
        return [], False

    def _extract_json(self, raw: str) -> list[object] | None:
        raw = raw.strip()
        if not raw:
            return None

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("[")
            end = raw.rfind("]")
            if start == -1 or end == -1 or end <= start:
                return None
            try:
                parsed = json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                return None

        if isinstance(parsed, list):
            return parsed

        return None

    def _validate_items(self, parsed: list[object], language: str) -> list[GenerationItem] | None:
        adapter = TypeAdapter(list[GenerationItem])
        try:
            items = adapter.validate_python(
                [
                    {
                        **entry,
                        "language": entry.get("language") or language,
                        "metadata": {"origin": "gap_based"},
                    }
                    for entry in parsed
                    if isinstance(entry, dict)
                ]
            )
        except ValidationError:
            return None

        return items
