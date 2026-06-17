import asyncio

from app.database.session import get_db_session
from app.repositories.question_repository import QuestionRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.services.embedding_service import EmbeddingService
from app.ai.embeddings.bge_m3_client import BgeM3Client


BATCH_SIZE = 20


async def main():

    session = get_db_session()

    question_repo = QuestionRepository(session)
    embedding_repo = EmbeddingRepository(session)

    embedding_service = EmbeddingService(
        client=BgeM3Client(),
        repository=embedding_repo,
    )

    questions = question_repo.get_questions_without_embeddings(
        embedding_service.model_name
    )

    print(f"Found {len(questions)} questions")

    for i in range(0, len(questions), BATCH_SIZE):

        batch = questions[i:i + BATCH_SIZE]

        texts = [q.text for q in batch]
        languages = [q.language for q in batch]

        embeddings = await embedding_service.embed_batch(
            texts=texts,
            languages=languages,
        )

        payload = []

        for question, embedding in zip(batch, embeddings):
            payload.append(
                {
                    "question_id": str(question.question_id),
                    "embedding": embedding,
                }
            )

        await embedding_service.store_embeddings(payload)

        print(
            f"Processed {min(i + BATCH_SIZE, len(questions))}/{len(questions)}"
        )

    print("Backfill complete")


if __name__ == "__main__":
    asyncio.run(main())