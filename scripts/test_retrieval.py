import asyncio

from app.database.session import get_db_session
from app.repositories.question_repository import QuestionRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.embedding_service import EmbeddingService
from app.ai.embeddings.bge_m3_client import BgeM3Client


async def main():

    session = get_db_session()

    try:
        question_repo = QuestionRepository(session)

        embedding_service = EmbeddingService(
            client=BgeM3Client(),
            repository=EmbeddingRepository(session),
        )

        query = "தமிழ்நாட்டில் பருவகால இடம்பெயர்ந்த தொழிலாளர்கள் பற்றிய ஆய்வு"

        embedding = await embedding_service.embed(
            text=query,
            language="en"
        )

        results = await question_repo.search_semantic(
            embedding=embedding,
            top_k=5,
            model_name=embedding_service.model_name,
        )

        print(f"\nQUERY: {query}\n")

        for idx, item in enumerate(results, start=1):
            print(
                f"{idx}. {item['text']} "
                f"(score={item['vector_similarity']:.4f})"
            )

    finally:
        session.close()


if __name__ == "__main__":
    asyncio.run(main())