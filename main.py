"""
Financial Intelligence Platform - Main Orchestrator
Executes the full operational lifecycle:
Supplier Invoice -> AI OCR Extraction -> Deterministic Math Check -> 
Draft Creation -> Human Review & Approval -> ERP Posting Simulation.
"""

import json
from src.ai_layer.gemini_adapter import GeminiAdapter
from src.modules.accounts_payable.invoice_processor import InvoiceProcessor
from src.core.posting_engine import PostingEngine


def run_platform_pipeline():
    print("=" * 70)
    print(" FINANCIAL INTELLIGENCE PLATFORM - END-TO-END WORKFLOW DEMO")
    print(" Operating Principle: Maximum Automation -> Minimum Human Intervention -> Human-Controlled Posting")
    print("=" * 70)

    # Step 1: Initialize Core Services
    ai_adapter = GeminiAdapter()
    invoice_processor = InvoiceProcessor(ai_adapter=ai_adapter)
    posting_engine = PostingEngine()

    # Mock Chart of Accounts for testing
    company_coa = [
        {"account_code": "601005", "account_name_ar": "مصاريف صيانة وتشغيل"},
        {"account_code": "105001", "account_name_ar": "ضريبة قيمة مضافة مدخلات"},
        {"account_code": "201001", "account_name_ar": "الموردين - أوراق الدفع"}
    ]

    # Step 2: Receive & Process Supplier Invoice (Autonomous Processing)
    print("\n[STAGE 1] Ingesting Supplier Invoice & Executing AI Extraction + Validation...")
    raw_invoice_file = "sample_supplier_invoice.pdf"

    draft_result = invoice_processor.process_supplier_invoice(
        file_path_or_bytes=raw_invoice_file,
        company_coa=company_coa
    )

    print(f" -> Extraction Status: SUCCESS")
    print(f" -> Supplier Name: {draft_result.get('supplier_name')}")
    print(f" -> Invoice Number: {draft_result.get('invoice_number')}")
    print(f" -> Workflow Stage: {draft_result.get('workflow_stage')}")
    print(f" -> Auto-Post Allowed? {draft_result.get('can_auto_post')} (Enforced Safeguard)")

    print("\n [Generated Journal Entry Draft]:")
    for line in draft_result["journal_entry_draft"]["lines"]:
        print(f"    Account {line['account_code']} | Debit: {line['debit']:>8.2f} SAR | Credit: {line['credit']:>8.2f} SAR | Memo: {line['memo']}")

    # Step 3: Human Controller Review & Approval
    print("\n[STAGE 2] Submitting Draft to Human Financial Controller for Review...")
    
    # Simulate explicit human approval by authorized user
    approved_entry = posting_engine.approve_draft_entry(
        draft_payload=draft_result,
        approver_id="usr_financial_controller_01",
        approver_role="Financial Controller",
        approval_notes="تم التحقق من استلام الخدمات وصحة الرقم الضريبي للهيئة."
    )

    print(f" -> Human Authorization Status: APPROVED")
    print(f" -> Approved By: {approved_entry['approved_by']} ({approved_entry['approver_role']})")
    print(f" -> Approval Timestamp: {approved_entry['approved_at']}")

    # Step 4: Posting to ERP
    print("\n[STAGE 3] Executing Posting to ERP System (Odoo Bridge)...")
    posting_result = posting_engine.execute_erp_posting(approved_payload=approved_entry)

    print(f" -> ERP Posting Status: {posting_result['status']}")
    print(f" -> ERP Reference ID: {posting_result['erp_reference_id']}")
    print(f" -> Final Workflow Stage: {posting_result['workflow_stage']}")

    print("\n" + "=" * 70)
    print(" WORKFLOW COMPLETED SUCCESSFULLY - TRANSACTION FULLY AUDITED & POSTED")
    print("=" * 70)


if __name__ == "__main__":
    run_platform_pipeline()
