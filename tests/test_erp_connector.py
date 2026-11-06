"""
Unit Tests for ERP Connectivity Layer & Odoo Adapter
Validates authentication fallbacks, COA retrieval, and journal entry transformation.
"""

from src.connectors.odoo_connector import OdooERPConnector


def test_odoo_connector_simulation_mode():
    """Tests that Odoo connector operates smoothly in simulation mode without active credentials."""
    connector = OdooERPConnector()
    
    assert connector.authenticate() is False
    
    coa = connector.fetch_chart_of_accounts()
    assert len(coa) > 0
    assert any(acc["account_code"] == "601005" for acc in coa)


def test_odoo_journal_entry_transformation():
    """Tests transformation of an approved platform draft into Odoo account.move payload structure."""
    connector = OdooERPConnector()

    approved_payload = {
        "invoice_number": "INV-2026-001",
        "invoice_date": "2026-03-01",
        "approved_by": "usr_finance_mgr_01",
        "journal_entry_draft": {
            "lines": [
                {"account_code": "601005", "debit": 1000.0, "credit": 0.0, "memo": "مصاريف صيانة"},
                {"account_code": "105001", "debit": 150.0, "credit": 0.0, "memo": "ضريبة مدخلات"},
                {"account_code": "201001", "debit": 0.0, "credit": 1150.0, "memo": "مستحقات المورد"}
            ]
        }
    }

    result = connector.post_journal_entry(approved_payload)

    assert result["status"] == "POSTED_TO_ODOO"
    assert result["odoo_move_id"] == 9901
    assert result["payload_sent"]["ref"] == "INV-2026-001"
    assert len(result["payload_sent"]["line_ids"]) == 3
