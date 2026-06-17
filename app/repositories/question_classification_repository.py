from sqlalchemy.orm import Session

from app.models.question_classification import QuestionClassification


class QuestionClassificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_classifications(self, question_id: str, tags: list[str], codes: list[str]) -> None:
        records: list[QuestionClassification] = []

        for tag in tags:
            records.append(
                QuestionClassification(
                    question_id=question_id,
                    tag=tag,
                )
            )

        for code in codes:
            records.append(
                QuestionClassification(
                    question_id=question_id,
                    classification_code=code,
                )
            )

        if records:
            self._session.add_all(records)
