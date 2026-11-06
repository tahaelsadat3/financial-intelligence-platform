"""
Unit Tests for Accounts Payable Invoice Processing Engine
Validates end-to-end draft generation, tax checks, and human control guardrails.
"""

from src.modules.accounts_payable.invoice_processor import InvoiceProcessor


def test_successful_invoice_processing():
    """Tests that a valid supplier invoice generates a balanced draft entry pending human review."""
    processor = InvoiceProcessor()
    
    # Mock COA for testing account matching
    sample_coa = [
        {"account_code": "601005", "account_name_ar": "مصاريف صيانة وتشغيل"},
        {"account_code": "105001", "account_name_ar": "ضريبة قيمة مضافة مدخلات"},
        {"account_code": "201001", "account_name_ar": "الموردين - أوراق الدفع"}
    ]

    result = processor.process_supplier_invoice(
        file_path_or_bytes="dummy_invoice.pdf",
        company_coa=sample_coa
    )

    assert result["status"] == "DRAFT_PREPARED"
    assert result["workflow_stage"] == "Pending Review"
    assert result["can_auto_post"] is False  # Safety constraint check
    assert result["journal_entry_draft"]["is_balanced"] is True
    
    # Check lines: Debit Expense + Debit VAT = Credit AP
    lines = result["journal_entry_draft"]["lines"]
    assert len(lines) == 3
    assert lines[0]["debit"] == 1000.00
    assert lines[1]["debit"] == 150.00
    assert lines[2]["credit"] == 1150.00


def test_rejected_invoice_on_tax_mismatch():
    """Tests that a invoice with incorrect tax data is rejected by deterministic engine."""
    processor = InvoiceProcessor()
    
    # Override simulation data to intentionally force a tax error
    processor.ai_adapter.extract_invoice_data = lambda file_path: {
        "supplier_name": "شركة التوريدات العامة",
        "vat_number": "310123456700003",
        "invoice_number": "INV-ERR-001",
        "invoice_date": "2026-03-01",
        "net_amount": 1000.00,
        "vat_amount": 200.00,  # Wrong VAT amount (should be 150.00)
        "gross_amount": 1200.00,
        "line_items": [{"description": "خدمة صيانة", "quantity": 1, "unit_price": 1000.00}]
    }

    result = processor.process_supplier_invoice(
        file_path_or_bytes="bad_invoice.pdf",
        company_coa=[]
    )

    assert result["status"] == "REJECTED_VALIDATION_FAILED"
    assert "VAT mismatch" in result["reason"]
