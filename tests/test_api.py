"""
Unit Tests for FastAPI REST API Endpoints
Validates HTTP routes for Health Check, Invoice Processing, RBAC Approval, and ERP Dispatch.
"""

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


def test_health_check_endpoint():
    """Tests the /health service check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_process_invoice_api():
    """Tests POST /api/v1/invoices/process creates a draft entry."""
    payload = {
        "file_name": "supplier_invoice_sample.pdf",
        "company_coa": [
            {"account_code": "601005", "account_name_ar": "مصاريف صيانة وتشغيل"},
            {"account_code": "105001", "account_name_ar": "ضريبة قيمة مضافة مدخلات"},
            {"account_code": "201001", "account_name_ar": "الموردين - أوراق الدفع"}
        ]
    }
    response = client.post("/api/v1/invoices/process", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "DRAFT_PREPARED"
    assert data["workflow_stage"] == "Pending Review"


def test_approve_entry_api_success_and_forbidden():
    """Tests RBAC enforcement on POST /api/v1/entries/approve."""
    draft_payload = {
        "status": "DRAFT_PREPARED",
        "workflow_stage": "Pending Review",
        "supplier_name": "شركة التوريدات العامة",
        "journal_entry_draft": {"total_debit": 1150.0, "total_credit": 1150.0}
    }

    # 1. Success case: Financial Controller
    approve_req = {
        "draft_payload": draft_payload,
        "approver_id": "usr_fin_mgr_01",
        "approver_role": "Financial Controller",
        "approval_notes": "معتمد ومراجع"
    }
    resp = client.post("/api/v1/entries/approve", json=approve_req)
    assert resp.status_code == 200
    assert resp.json()["workflow_stage"] == "Approved"

    # 2. Forbidden case: Data Entry Clerk
    unauthorized_req = {
        "draft_payload": draft_payload,
        "approver_id": "usr_clerk_01",
        "approver_role": "Data Entry Clerk"
    }
    forbidden_resp = client.post("/api/v1/entries/approve", json=unauthorized_req)
    assert forbidden_resp.status_code == 403


def test_post_to_erp_api_blocked_if_not_approved():
    """Tests POST /api/v1/entries/post blocks direct unapproved dispatch with 403 Forbidden."""
    unapproved_payload = {
        "status": "DRAFT_PREPARED",
        "workflow_stage": "Pending Review"
    }
    response = client.post("/api/v1/entries/post", json={"approved_payload": unapproved_payload})
    assert response.status_code == 403
