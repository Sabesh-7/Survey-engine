from __future__ import annotations


class ClassificationService:
    CATEGORY_KEYWORDS = {
        "employment": [
            "job",
            "employment",
            "occupation",
            "salary",
            "income",
            "employer",
            "work",
            "working",
            "wage",
            "benefits",
        ],
        "education": [
            "education",
            "school",
            "college",
            "university",
            "literacy",
            "degree",
            "study",
            "student",
            "learning",
        ],
        "health": [
            "health",
            "hospital",
            "disease",
            "illness",
            "medical",
            "doctor",
            "medicine",
            "vaccination",
            "treatment",
        ],
        "transport": [
            "transport",
            "travel",
            "commute",
            "commuting",
            "bus",
            "train",
            "vehicle",
            "road",
        ],
        "migration": [
            "migration",
            "migrant",
            "moved",
            "relocated",
            "relocation",
            "resettled",
        ],
        "agriculture": [
            "farm",
            "farming",
            "agriculture",
            "crop",
            "land",
            "livestock",
            "harvest",
        ],
        "digital_access": [
            "internet",
            "smartphone",
            "mobile",
            "digital",
            "computer",
            "laptop",
            "online",
            "connectivity",
            "wifi",
        ],
        "demographics": [
            "age",
            "gender",
            "marital",
            "household",
            "family",
            "education level",
            "income level",
        ],
    }

    async def classify(
        self,
        text: str,
        language: str,
    ) -> list[str]:

        text_lower = text.lower()

        matches: list[str] = []

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                matches.append(category)

        return matches