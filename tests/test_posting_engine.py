"""
Unit Tests for Human-Controlled Posting Engine
Validates RBAC permissions, state transition guardrails, and anti-auto-posting enforcement.
"""

import pytest
from src.core.posting_engine import PostingEngine, UnauthorizedPostingError


def test_successful_human_approval_and_posting():
    """Tests that a valid draft can be approved by a Financial Controller and then posted to ERP."""
    engine = PostingEngine()

    draft_payload = {
        "status": "DRAFT_PREPARED",
        "workflow_stage": "Pending Review",
        "supplier_name": "شركة التوريدات العامة",
        "journal_entry_draft": {"total_debit": 1150.0, "total_credit": 1150.0}
    }

    # Step 1: Human Approval
    approved_draft = engine.approve_draft_entry(
        draft_payload=draft_payload,
        approver_id="usr_finance_mgr_01",
        approver_role="Financial Controller",
        approval_notes="تمت مراجعة الفاتورة والمطابقة مع طلب الشراء."
    )

    assert approved_draft["workflow_stage"] == "Approved"
    assert approved_draft["approved_by"] == "usr_finance_mgr_01"

    # Step 2: ERP Posting
    posting_result = engine.execute_erp_posting(approved_payload=approved_draft)

    assert posting_result["status"] == "SUCCESSFULLY_POSTED"
    assert posting_result["workflow_stage"] == "Posted"
    assert posting_result["audit_trail"]["approved_by"] == "usr_finance_mgr_01"


def test_unauthorized_role_approval_fails():
    """Tests that an unauthorized role (e.g. Data Entry) is blocked from approving financial drafts."""
    engine = PostingEngine()

    draft_payload = {
        "status": "DRAFT_PREPARED",
        "workflow_stage": "Pending Review"
    }

    with pytest.raises(UnauthorizedPostingError) as exc_info:
        engine.approve_draft_entry(
            draft_payload=draft_payload,
            approver_id="usr_clerk_02",
            approver_role="Junior Clerk"
        )

    assert "is not authorized" in str(exc_info.value)


def test_direct_auto_posting_is_blocked():
    """Tests that attempting to post directly without human approval raises an explicit error."""
    engine = PostingEngine()

    unapproved_draft = {
        "status": "DRAFT_PREPARED",
        "workflow_stage": "Pending Review"
    }

    with pytest.raises(UnauthorizedPostingError) as exc_info:
        engine.execute_erp_posting(approved_payload=unapproved_draft)

    assert "Posting DENIED!" in str(exc_info.value)
