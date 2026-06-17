import asyncio

from app.core.dependencies import get_duplicate_detector
from app.schemas.duplicates import DuplicateDetectionRequest


async def main():
    detector = get_duplicate_detector()

    response = await detector.detect(
        DuplicateDetectionRequest(
            question_text="உங்கள் தொழில் என்ன?",
            language="en",
            top_k=10,
        )
    )

    print(f"Duplicates found: {len(response.duplicates)}")

    for item in response.duplicates:
        print(
            f"{item.text} | "
            f"{item.similarity_score:.4f} | "
            f"{item.match_type}"
        )


if __name__ == "__main__":
    asyncio.run(main())