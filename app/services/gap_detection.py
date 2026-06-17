import re

from app.services.audit_service import AuditService


class GapDetectionService:
    def __init__(self, audit_service: AuditService) -> None:
        self._audit = audit_service

    async def detect(self, prompt: str, retrieved_questions: list[dict]) -> list[str]:
        run = self._audit.start_run(
            run_type="gap_detection",
            prompt=prompt,
            language=None,
            model_name=None,
            request_id=None,
            trace_id=None,
            input_metadata={"retrieved_questions": len(retrieved_questions)},
        )
        try:
            normalized_prompt = self._normalize(prompt)
            requested_topics = self._detect_topics(normalized_prompt)

            if not requested_topics:
                self._audit.add_stage(
                    run_id=run.run_id,
                    stage="gap_detection",
                    status="ok",
                    payload={"requested_topics": [], "gaps": []},
                )
                self._audit.finish_run(run_id=run.run_id, run_status="completed", duration_ms=0, output_metadata={"gaps": []})
                return []

            covered_topics = self._detect_covered_topics(retrieved_questions)
            gaps = [topic for topic in requested_topics if topic not in covered_topics]
            self._audit.add_stage(
                run_id=run.run_id,
                stage="gap_detection",
                status="ok",
                payload={"requested_topics": requested_topics, "covered_topics": list(covered_topics), "gaps": gaps},
            )
            self._audit.finish_run(run_id=run.run_id, run_status="completed", duration_ms=0, output_metadata={"gaps": gaps})
            return gaps
        except Exception as exc:
            self._audit.add_stage(
                run_id=run.run_id,
                stage="gap_detection",
                status="failed",
                reason=str(exc),
                payload={"prompt": prompt},
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

    def _detect_topics(self, normalized_prompt: str) -> list[str]:
        topic_keywords = {
            "employment": [
                "employment",
                "job",
                "occupation",
                "work",
                "வேலை",
                "தொழில்",
                "रोजगार",
                "नौकरी",
            ],
            "education": [
                "education",
                "school",
                "college",
                "literacy",
                "கல்வி",
                "பள்ளி",
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

        requested: list[str] = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in normalized_prompt for keyword in keywords):
                requested.append(topic)

        return requested

    def _detect_covered_topics(self, retrieved_questions: list[dict]) -> set[str]:
        covered: set[str] = set()
        for row in retrieved_questions:
            category = (row.get("category") or "").strip().lower()
            text = (row.get("text") or "").strip().lower()

            if "employment" in category or "occupation" in text or "work" in text:
                covered.add("employment")
            if "education" in category or "school" in text or "college" in text:
                covered.add("education")
            if "health" in category or "health" in text or "hospital" in text:
                covered.add("health")
            if "demographic" in category or "age" in text or "gender" in text:
                covered.add("demographics")
            if "income" in category or "income" in text or "salary" in text:
                covered.add("income")
            if "agriculture" in category or "farming" in text or "crop" in text:
                covered.add("agriculture")
            if "housing" in category or "house" in text or "rent" in text:
                covered.add("housing")
            if "migration" in category or "migrant" in text or "relocation" in text:
                covered.add("migration")
            if "transport" in category or "commute" in text or "travel" in text:
                covered.add("transport")
            if "digital" in category or "internet" in text or "mobile" in text:
                covered.add("digital_access")

        return covered
