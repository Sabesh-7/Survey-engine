from sqlalchemy import exists, select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.question import Question
from app.models.question_classification import QuestionClassification
from app.models.question_embedding import QuestionEmbedding


class QuestionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session    

    def create_question(self, payload) -> Question:
        question = Question(
            text=payload.text,
            language=payload.language,
            category=payload.category,
            source=payload.source,
            source_reference=payload.source_reference,
            created_by=payload.created_by,
            confidence_score=payload.confidence_score,
            is_active=True,
        )
        self._session.add(question)
        self._session.flush()
        return question

    async def search_semantic(
        self,
        embedding: list[float],
        top_k: int,
        language: str | None = None,
        sources: list[str] | None = None,
        categories: list[str] | None = None,
        classification_codes: list[str] | None = None,
        model_name: str | None = None,
    ) -> list[dict]:
        if model_name is None:
            model_name = get_settings().embeddings_model_name
        distance = QuestionEmbedding.embedding.cosine_distance(embedding)
        vector_similarity = (1 - distance).label("vector_similarity")

        stmt = (
            select(
                Question.question_id,
                Question.text,
                Question.language,
                Question.category,
                Question.source,
                vector_similarity,
            )
            .join(QuestionEmbedding, QuestionEmbedding.question_id == Question.question_id)
            .where(QuestionEmbedding.model_name == model_name)
            .where(Question.is_active.is_(True))
        )

        if language:
            stmt = stmt.where(Question.language == language)

        if sources:
            stmt = stmt.where(Question.source.in_(sources))

        if categories:
            stmt = stmt.where(Question.category.in_(categories))

        if classification_codes:
            classification_exists = (
                select(1)
                .select_from(QuestionClassification)
                .where(QuestionClassification.question_id == Question.question_id)
                .where(QuestionClassification.classification_code.in_(classification_codes))
                .exists()
            )
            stmt = stmt.where(classification_exists)

        stmt = stmt.order_by(distance).limit(top_k)
        rows = self._session.execute(stmt).all()

        return [
            {
                "question_id": str(row.question_id),
                "text": row.text,
                "language": row.language,
                "category": row.category,
                "source": row.source,
                "vector_similarity": float(row.vector_similarity),
            }
            for row in rows
        ]
    def get_questions_without_embeddings(self,model_name: str,):
            stmt = (
                select(Question)
                .where(Question.is_active.is_(True))
                .where(
                    ~Question.question_id.in_(
                        select(QuestionEmbedding.question_id)
                        .where(
                            QuestionEmbedding.model_name == model_name
                        )
                    )
                )
            )

            return self._session.execute(stmt).scalars().all()
