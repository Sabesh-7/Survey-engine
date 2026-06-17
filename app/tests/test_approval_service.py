from app.schemas.approval import ApprovalDecision, ApprovalRequest


def test_approval_creates_review_ledger_entry(approval_service, review_repository, audit_service):
    response = approval_service.review(
        ApprovalRequest(
            question_text="Have you migrated in the last five years?",
            language="en",
            decision=ApprovalDecision.approved,
            reviewer="admin-1",
            comments="Looks good",
            run_id="run-123",
            run_item_id="item-456",
            metadata={"source": "test"},
        )
    )

    assert response.review_status == "approved"
    assert review_repository.reviews[0]["decision"] == "approved"
    assert audit_service._repository.items[0]["stage"] == "approval_decision"
