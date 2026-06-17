import asyncio

from app.core.dependencies import get_question_retrieval
from app.schemas.recommendations import RecommendationRequest


async def main():
    service = get_question_retrieval()

    response = await service.recommend(
        RecommendationRequest(
            prompt="Survey about internet access and smartphone usage in rural areas",
            top_k=5,
        )
    )

    print("\nRETRIEVED QUESTIONS\n")

    for item in response.items:
        print(
            f"{item.text}"
            f" | {item.category}"
            f" | {item.retrieval_reason}"
        )

    print("\nGAPS:")
    print(response.gaps)

    print("\nGENERATED QUESTIONS\n")

    for item in response.generated_questions:
        print(item.text)

    print("\nREJECTED QUESTIONS\n")

    for item in response.rejected_items:
        print(item.text)


if __name__ == "__main__":
    asyncio.run(main())