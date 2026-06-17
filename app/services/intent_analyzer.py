import re

from app.services.audit_service import AuditService
from app.schemas.intent import IntentRequest, IntentResponse, IntentType


class IntentAnalyzerService:
    def __init__(self, audit_service: AuditService) -> None:
        self._audit = audit_service

    async def analyze(self, payload: IntentRequest) -> IntentResponse:
        run = self._audit.start_run(
            run_type="intent_analysis",
            prompt=payload.prompt,
            language=payload.language,
            model_name=None,
            request_id=None,
            trace_id=None,
            input_metadata={"language": payload.language},
        )
        try:
            normalized = self._normalize(payload.prompt)
            topics, matched_keywords = self._extract_topics(normalized)
            intent = self._infer_intent(normalized, topics)
            confidence = self._confidence(intent, matched_keywords)

            if not topics and intent == IntentType.unknown:
                self._audit.add_stage(
                    run_id=run.run_id,
                    stage="intent_analysis",
                    status="ok",
                    payload={"intent": intent.value, "topics": ["general"], "confidence": 0.2},
                )
                self._audit.finish_run(
                    run_id=run.run_id,
                    run_status="completed",
                    duration_ms=0,
                    output_metadata={"topics": ["general"], "matched_keywords": []},
                )
                return IntentResponse(
                    intent=IntentType.unknown,
                    confidence=0.2,
                    topics=["general"],
                    metadata={"matched_keywords": []},
                )

            self._audit.add_stage(
                run_id=run.run_id,
                stage="intent_analysis",
                status="ok",
                payload={
                    "intent": intent.value,
                    "topics": topics,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords,
                },
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="completed",
                duration_ms=0,
                output_metadata={"topics": topics, "matched_keywords": matched_keywords},
            )

            return IntentResponse(
                intent=intent,
                confidence=confidence,
                topics=topics,
                metadata={"matched_keywords": matched_keywords},
            )
        except Exception as exc:
            self._audit.add_stage(
                run_id=run.run_id,
                stage="intent_analysis",
                status="failed",
                reason=str(exc),
                payload={"prompt": payload.prompt},
            )
            self._audit.finish_run(
                run_id=run.run_id,
                run_status="failed",
                duration_ms=0,
                output_metadata={"error": str(exc)},
            )
            raise

    def _normalize(self, text: str) -> str:
        normalized = text.strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized

    def _infer_intent(self, normalized_prompt: str, topics: list[str]) -> IntentType:
        if "?" in normalized_prompt:
            return IntentType.question_request

        if normalized_prompt.startswith(("add", "include", "create", "build", "make", "draft")):
            return IntentType.question_request

        if normalized_prompt.startswith(("update", "edit", "revise", "change", "modify")):
            return IntentType.update_request

        if topics:
            return IntentType.topic_scope

        return IntentType.unknown

    def _confidence(self, intent: IntentType, matched_keywords: list[str]) -> float:
        if intent == IntentType.unknown:
            return 0.2

        base = 0.5
        boost = min(0.3, 0.05 * len(matched_keywords))
        return base + boost

    def _extract_topics(self, normalized_prompt: str) -> tuple[list[str], list[str]]:
        topic_keywords = {
            "employment": [
                "employment",
                "job",
                "occupation",
                "work",
                "employment status",
                "வேலை",
                "தொழில்",
                "பணி",
                "रोजगार",
                "नौकरी",
                "काम",
            ],
            "education": [
                "education",
                "school",
                "college",
                "literacy",
                "பள்ளி",
                "கல்வி",
                "शिक्षा",
                "विद्यालय",
            ],
            "health": [
                "health",
                "disease",
                "illness",
                "hospital",
                "ஆரோக்கிய",
                "நோய்",
                "स्वास्थ्य",
                "बीमारी",
            ],
            "demographics": [
                "age",
                "gender",
                "household",
                "population",
                "வயது",
                "பாலினம்",
                "जनसंख्या",
                "उम्र",
            ],
            "income": [
                "income",
                "salary",
                "earnings",
                "wage",
                "வருமானம்",
                "சம்பளம்",
                "आय",
                "वेतन",
            ],
            "agriculture": [
                "agriculture",
                "farming",
                "crop",
                "farmer",
                "விவசாய",
                "பயிர்",
                "कृषि",
                "किसान",
            ],
            "housing": [
                "housing",
                "house",
                "rent",
                "ownership",
                "வீடு",
                "வாடகை",
                "आवास",
                "किराया",
            ],
            "migration": [
                "migration",
                "migrant",
                "moved",
                "relocation",
                "குடியேற்ற",
                "स्थानांतरण",
            ],
            "transport": [
                "transport",
                "commute",
                "travel",
                "bus",
                "train",
                "பயணம்",
                "போக்குவரத்து",
                "यात्रा",
                "परिवहन",
            ],
            "digital_access": [
                "internet",
                "mobile",
                "smartphone",
                "connectivity",
                "இணையம்",
                "மொபைல்",
                "इंटरनेट",
                "मोबाइल",
            ],
        }

        matched_topics: list[str] = []
        matched_keywords: list[str] = []

        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in normalized_prompt:
                    matched_topics.append(topic)
                    matched_keywords.append(keyword)
                    break

        return matched_topics, matched_keywords
