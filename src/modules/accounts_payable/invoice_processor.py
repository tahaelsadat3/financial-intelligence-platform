"""
Accounts Payable Module - Invoice Processing Engine
Orchestrates AI Document Extraction, Deterministic Financial Validation,
and Automated Draft Journal Entry Generation.
"""

from typing import Dict, Any, List
from src.ai_layer.gemini_adapter import GeminiAdapter
from src.financial_engine.validators import validate_vat_calculation, validate_journal_entry_balance


class InvoiceProcessor:
    """
    Processes Supplier Invoices and creates verified Accounting Entry Drafts.
    Enforces the permanent rule: Maximum Automation -> Minimum Human Intervention -> Human-Controlled Posting.
    """

    def __init__(self, ai_adapter: GeminiAdapter = None):
        self.ai_adapter = ai_adapter or GeminiAdapter()

    def process_supplier_invoice(
        self,
        file_path_or_bytes: Any,
        company_coa: List[Dict[str, Any]],
        default_ap_account_code: str = "201001",
        default_vat_account_code: str = "105001",
        vat_rate: float = 0.15
    ) -> Dict[str, Any]:
        """
        End-to-end processing of a supplier invoice:
        1. AI extraction of JSON data.
        2. Deterministic calculation and tax validation.
        3. AI GL account suggestion for expense/item.
        4. Journal Entry Draft construction.
        5. Double-entry debit/credit balance verification.
        6. Setting status to 'Pending Review' (NEVER 'Posted').
        """
        # Step 1: AI Extraction
        ai_response = self.ai_adapter.extract_invoice_data(file_path_or_bytes)
        
        if ai_response.get("status") == "simulation_mode":
            extracted = ai_response["extracted_payload"]
        else:
            extracted = ai_response

        net_amount = extracted.get("net_amount", 0.0)
        vat_amount = extracted.get("vat_amount", 0.0)
        gross_amount = extracted.get("gross_amount", 0.0)

        # Step 2: Deterministic Tax & Math Validation
        is_tax_valid, tax_msg = validate_vat_calculation(
            net_amount=net_amount,
            vat_rate=vat_rate,
            extracted_vat=vat_amount,
            extracted_gross=gross_amount
        )

        if not is_tax_valid:
            return {
                "status": "REJECTED_VALIDATION_FAILED",
                "reason": tax_msg,
                "extracted_data": extracted
            }

        # Step 3: AI Account Classification Suggestion
        first_item_desc = (
            extracted["line_items"][0]["description"] 
            if extracted.get("line_items") 
            else "عام"
        )
        gl_suggestion = self.ai_adapter.suggest_gl_account(
            vendor_name=extracted.get("supplier_name", ""),
            line_item_description=first_item_desc,
            chart_of_accounts=company_coa
        )
        suggested_expense_account = gl_suggestion.get("suggested_account_code", "601000")

        # Step 4: Construct Journal Entry Draft Lines
        # Debit: Expense / Inventory Account
        # Debit: Input VAT Account
        # Credit: Accounts Payable Account
        entry_lines = [
            {
                "account_code": suggested_expense_account,
                "debit": net_amount,
                "credit": 0.0,
                "memo": f"فاتورة مورد {extracted.get('invoice_number')} - {first_item_desc}"
            },
            {
                "account_code": default_vat_account_code,
                "debit": vat_amount,
                "credit": 0.0,
                "memo": f"ضريبة قيمة مضافة مدخلات فاتورة رقم {extracted.get('invoice_number')}"
            },
            {
                "account_code": default_ap_account_code,
                "debit": 0.0,
                "credit": gross_amount,
                "memo": f"مستحقات المورد {extracted.get('supplier_name')}"
            }
        ]

        # Step 5: Deterministic Balance Check
        is_balanced, balance_msg, variance = validate_journal_entry_balance(entry_lines)

        if not is_balanced:
            return {
                "status": "REJECTED_UNBALANCED_ENTRY",
                "reason": balance_msg,
                "variance": float(variance)
            }

        # Step 6: Return Prepared Draft (Awaiting Authorized Human Approval)
        return {
            "status": "DRAFT_PREPARED",
            "workflow_stage": "Pending Review",
            "supplier_name": extracted.get("supplier_name"),
            "vat_number": extracted.get("vat_number"),
            "invoice_number": extracted.get("invoice_number"),
            "invoice_date": extracted.get("invoice_date"),
            "gl_suggestion_confidence": gl_suggestion.get("confidence_score"),
            "gl_explanation_ar": gl_suggestion.get("explanation_ar"),
            "journal_entry_draft": {
                "lines": entry_lines,
                "total_debit": net_amount + vat_amount,
                "total_credit": gross_amount,
                "is_balanced": True
            },
            "requires_human_approval": True,
            "can_auto_post": False  # Permanent Architectural Principle Safeguard
        }
