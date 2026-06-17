from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.models.question_embedding import QuestionEmbedding


class EmbeddingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert_question_embedding(
        self,
        question_id: str,
        model_name: str,
        embedding: list[float],
        commit: bool = True,
    ) -> None:
        stmt = (
            insert(QuestionEmbedding)
            .values(
                question_id=question_id,
                model_name=model_name,
                embedding=embedding,
            )
            .on_conflict_do_update(
                index_elements=["question_id", "model_name"],
                set_={
                    "embedding": embedding,
                    "created_at": func.now(),
                },
            )
        )
        self._session.execute(stmt)
        if commit:
            self._session.commit()

    def upsert_question_embeddings(
        self,
        question_embeddings: list[dict],
        model_name: str,
        commit: bool = True,
    ) -> None:
        values = [
            {
                "question_id": item["question_id"],
                "model_name": model_name,
                "embedding": item["embedding"],
            }
            for item in question_embeddings
        ]

        stmt = (
            insert(QuestionEmbedding)
            .values(values)
            .on_conflict_do_update(
                index_elements=["question_id", "model_name"],
                set_={
                    "embedding": insert(QuestionEmbedding).excluded.embedding,
                    "created_at": func.now(),
                },
            )
        )
        self._session.execute(stmt)
        if commit:
            self._session.commit()
