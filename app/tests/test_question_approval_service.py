from app.schemas.approval import ApprovalDecision, ApprovalRequest


def test_question_approval_service_pending_review(approval_service):
    response = approval_service.review(
        ApprovalRequest(
            question_text="Have you migrated in the last five years?",
            language="en",
            decision=ApprovalDecision.changes_requested,
            reviewer="admin",
            comments="Rephrase it",
            run_id="run-1",
            run_item_id="item-1",
        )
    )
    assert response.review_status == "rejected"
