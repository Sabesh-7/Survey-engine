import asyncio

from app.core.dependencies import get_question_validator
from app.schemas.generation import GenerationItem


async def main():

    validator = get_question_validator()

    items = [
        GenerationItem(
            text="What is your occupation?",
            language="en",
            confidence=0.95,
        ),
        GenerationItem(
            text="Age?",
            language="en",
            confidence=0.90,
        ),
        GenerationItem(
            text="What is your bank account number?",
            language="en",
            confidence=0.95,
        ),
        GenerationItem(
            text="How many hours do you work per week?",
            language="en",
            confidence=0.95,
        ),
    ]

    accepted, rejected = await validator.validate(
        items=items,
        language="en",
    )

    print(f"Accepted: {len(accepted)}")
    print(f"Rejected: {len(rejected)}")

    print("\nREJECTED")
    for item in rejected:
        print("\nQUESTION:", item.text)
        print(item.metadata)

    print("\nACCEPTED")
    for item in accepted:
        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())