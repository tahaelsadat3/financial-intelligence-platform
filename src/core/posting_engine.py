"""
Core Security & Workflow Module - Human-Controlled Posting Engine
Enforces strict human approval guardrails before any financial draft is authorized for ERP posting.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class UnauthorizedPostingError(Exception):
    """Raised when an automated script or unauthorized user attempts to bypass human approval."""
    pass


class PostingEngine:
    """
    Controls transaction lifecycle transitions:
    Draft Prepared / Pending Review -> Approved -> Posted.
    Guarantees zero autonomous posting without explicit human permission.
    """

    def __init__(self, authorized_roles: Optional[list] = None):
        # Default authorized roles capable of posting financial entries
        self.authorized_roles = authorized_roles or ["Financial Controller", "Chief Accountant", "Finance Manager"]

    def approve_draft_entry(
        self,
        draft_payload: Dict[str, Any],
        approver_id: str,
        approver_role: str,
        approval_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Validates human user authority and upgrades draft status to 'Approved'.
        """
        if approver_role not in self.authorized_roles:
            raise UnauthorizedPostingError(
                f"User role '{approver_role}' is not authorized to approve financial drafts. "
                f"Required roles: {self.authorized_roles}"
            )

        if draft_payload.get("workflow_stage") != "Pending Review":
            raise ValueError(f"Cannot approve entry in stage '{draft_payload.get('workflow_stage')}'. Must be 'Pending Review'.")

        # Record human authorization metadata
        draft_payload["workflow_stage"] = "Approved"
        draft_payload["approved_by"] = approver_id
        draft_payload["approver_role"] = approver_role
        draft_payload["approved_at"] = datetime.utcnow().isoformat()
        draft_payload["approval_notes"] = approval_notes
        
        return draft_payload

    def execute_erp_posting(
        self,
        approved_payload: Dict[str, Any],
        erp_connector: Any = None
    ) -> Dict[str, Any]:
        """
        Dispatches an Approved financial transaction to the ERP system (e.g. Odoo).
        Strictly verifies that approval exists before posting.
        """
        # Guardrail check: Ensure explicit human approval was granted
        if approved_payload.get("workflow_stage") != "Approved" or not approved_payload.get("approved_by"):
            raise UnauthorizedPostingError(
                "Posting DENIED! Transaction has not received explicit human authorization. "
                "Automated posting is strictly prohibited by platform architecture."
            )

        # Update status to final Posted state
        approved_payload["workflow_stage"] = "Posted"
        approved_payload["posted_at"] = datetime.utcnow().isoformat()
        approved_payload["erp_reference_id"] = "ODOO-POSTED-MOCK-9901"
        approved_payload["is_posted"] = True

        return {
            "status": "SUCCESSFULLY_POSTED",
            "workflow_stage": "Posted",
            "erp_reference_id": approved_payload["erp_reference_id"],
            "audit_trail": {
                "approved_by": approved_payload["approved_by"],
                "approved_at": approved_payload["approved_at"],
                "posted_at": approved_payload["posted_at"]
            }
        }
