from app.schemas.approval import ApprovalDecision, ApprovalRequest


def test_validation_to_approval_workflow(approval_service):
    response = approval_service.review(
        ApprovalRequest(
            question_text="Have you migrated in the last five years?",
            language="en",
            decision=ApprovalDecision.approved,
            reviewer="admin-1",
            comments="Approved",
            run_id="run-1",
            run_item_id="item-1",
        )
    )
    assert response.review_id
