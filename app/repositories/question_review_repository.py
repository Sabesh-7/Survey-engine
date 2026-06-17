from sqlalchemy.orm import Session

from app.models.question_review import QuestionReview


class QuestionReviewRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_review(
        self,
        question_text: str,
        language: str,
        decision: str,
        reviewer: str | None,
        comments: str | None,
        run_id: str | None,
        run_item_id: str | None,
        metadata: dict | None,
    ) -> QuestionReview:
        review = QuestionReview(
            question_text=question_text,
            language=language,
            decision=decision,
            reviewer=reviewer,
            comments=comments,
            run_id=run_id,
            run_item_id=run_item_id,
            decision_metadata=metadata,
        )
        self._session.add(review)
        self._session.flush()
        return review
