import asyncio
import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.models.question import Question
from app.models.question_classification import QuestionClassification
from app.models.question_embedding import QuestionEmbedding
from app.repositories.question_repository import QuestionRepository


def _vector_with_index(index: int, value: float, dim: int = 1024) -> list[float]:
    vector = [0.0] * dim
    vector[index] = value
    return vector


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="DATABASE_URL is not set")
def test_retrieval_semantic_multilingual() -> None:
    engine = create_engine(os.getenv("DATABASE_URL"))
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        session.execute(text('CREATE EXTENSION IF NOT EXISTS "vector";'))
        session.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto";'))
        session.commit()

        Base.metadata.create_all(engine)

        q_en = Question(
            question_id=uuid.uuid4(),
            text="What is your occupation?",
            language="en",
            source="historical",
            category="employment",
            is_active=True,
        )
        q_ta = Question(
            question_id=uuid.uuid4(),
            text="உங்கள் தொழில் என்ன?",
            language="ta",
            source="standard",
            category="employment",
            is_active=True,
        )
        q_other = Question(
            question_id=uuid.uuid4(),
            text="What is your age?",
            language="en",
            source="standard",
            category="demographics",
            is_active=True,
        )

        session.add_all([q_en, q_ta, q_other])
        session.flush()

        session.add_all(
            [
                QuestionEmbedding(
                    question_id=q_en.question_id,
                    model_name="bge-m3",
                    embedding=_vector_with_index(0, 1.0),
                ),
                QuestionEmbedding(
                    question_id=q_ta.question_id,
                    model_name="bge-m3",
                    embedding=_vector_with_index(0, 0.98),
                ),
                QuestionEmbedding(
                    question_id=q_other.question_id,
                    model_name="bge-m3",
                    embedding=_vector_with_index(1, 1.0),
                ),
            ]
        )

        session.add(
            QuestionClassification(
                question_id=q_en.question_id,
                classification_code="EMP",
            )
        )
        session.commit()

        repo = QuestionRepository(session)
        query_vector = _vector_with_index(0, 1.0)

        results = asyncio.run(
            repo.search_semantic(
                embedding=query_vector,
                top_k=2,
            )
        )

        assert results[0]["question_id"] == str(q_en.question_id)

        filtered = asyncio.run(
            repo.search_semantic(
                embedding=query_vector,
                top_k=5,
                language="ta",
            )
        )
        assert len(filtered) == 1
        assert filtered[0]["question_id"] == str(q_ta.question_id)

        classified = asyncio.run(
            repo.search_semantic(
                embedding=query_vector,
                top_k=5,
                classification_codes=["EMP"],
            )
        )
        assert classified[0]["question_id"] == str(q_en.question_id)
    finally:
        Base.metadata.drop_all(engine)
        session.close()
