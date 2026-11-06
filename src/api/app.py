"""
FastAPI Application Entry Point
Exposes HTTP REST Endpoints for Invoice Processing, Draft Approval, and ERP Dispatch.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from src.ai_layer.gemini_adapter import GeminiAdapter
from src.modules.accounts_payable.invoice_processor import InvoiceProcessor
from src.core.posting_engine import PostingEngine, UnauthorizedPostingError
from src.connectors.odoo_connector import OdooERPConnector

app = FastAPI(
    title="Financial Intelligence Platform API",
    description="Enterprise-grade AI-powered financial processing & ERP connector platform.",
    version="1.0.0"
)

# Core Instances
ai_adapter = GeminiAdapter()
processor = InvoiceProcessor(ai_adapter=ai_adapter)
posting_engine = PostingEngine()
odoo_connector = OdooERPConnector()


# Request / Response Schemas
class InvoiceProcessRequest(BaseModel):
    file_name: str = Field(..., example="supplier_invoice_101.pdf")
    company_coa: List[Dict[str, Any]] = Field(default_factory=list)


class ApprovalRequest(BaseModel):
    draft_payload: Dict[str, Any]
    approver_id: str = Field(..., example="usr_fin_ctrl_01")
    approver_role: str = Field(..., example="Financial Controller")
    approval_notes: Optional[str] = ""


class ERPPostRequest(BaseModel):
    approved_payload: Dict[str, Any]


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Service Health & Diagnostic Status Endpoint."""
    return {
        "status": "healthy",
        "service": "Financial Intelligence Engine",
        "version": "1.0.0"
    }


@app.post("/api/v1/invoices/process", status_code=status.HTTP_201_CREATED)
def process_invoice(request: InvoiceProcessRequest):
    """
    Ingests invoice file data, validates math & VAT, and outputs draft journal entry.
    """
    try:
        draft = processor.process_supplier_invoice(
            file_path_or_bytes=request.file_name,
            company_coa=request.company_coa
        )
        return draft
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invoice processing failed: {str(e)}"
        )


@app.post("/api/v1/entries/approve", status_code=status.HTTP_200_OK)
def approve_entry(request: ApprovalRequest):
    """
    Applies explicit human approval to a pending financial draft (RBAC Enforced).
    """
    try:
        approved = posting_engine.approve_draft_entry(
            draft_payload=request.draft_payload,
            approver_id=request.approver_id,
            approver_role=request.approver_role,
            approval_notes=request.approval_notes
        )
        return approved
    except UnauthorizedPostingError as upe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(upe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post("/api/v1/entries/post", status_code=status.HTTP_200_OK)
def post_to_erp(request: ERPPostRequest):
    """
    Posts an authorized & approved journal entry directly to the target ERP system.
    """
    try:
        # Step 1: Engine Guardrail Verification
        result = posting_engine.execute_erp_posting(
            approved_payload=request.approved_payload,
            erp_connector=odoo_connector
        )
        
        # Step 2: ERP Dispatch Transformation
        erp_result = odoo_connector.post_journal_entry(request.approved_payload)
        
        result["erp_response"] = erp_result
        return result
    except UnauthorizedPostingError as upe:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(upe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ERP posting dispatch failed: {str(e)}"
        )
