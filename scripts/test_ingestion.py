import asyncio

from app.core.dependencies import get_question_ingestion_service
from app.schemas.ingestion import (
    IngestionQuestion,
    IngestionRequest,
)


async def main():

    service = get_question_ingestion_service()

    response = await service.ingest(
        IngestionRequest(
            questions=[
                IngestionQuestion(
                    text="How many hours do you spend commuting each day?",
                    language="en",
                    category="transport",
                    source="manual",
                    created_by="test_script",
                    confidence_score=1.0,
                    tags=["transport"],
                    classification_codes=["TRANSPORT"],
                )
            ]
        )
    )

    print(response.model_dump())


if __name__ == "__main__":
    asyncio.run(main())