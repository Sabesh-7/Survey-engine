from app.core.dependencies import get_question_approval_service
from app.schemas.approval import (
    ApprovalRequest,
    ApprovalDecision,
)


def main():
    service = get_question_approval_service()

    response = service.review(
        ApprovalRequest(
            question_text="How many hours do you spend commuting each day?",
            language="en",
            decision=ApprovalDecision.approved,
            reviewer="Sabesh",
            comments="Approved during testing",
            run_id=None,
            run_item_id=None,
            metadata={"test": True},
        )
    )

    print(response.model_dump())


if __name__ == "__main__":
    main()