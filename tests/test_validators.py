"""
Unit Tests for Deterministic Financial Engine Validators
Ensures 100% mathematical accuracy for journal entries and VAT checks.
"""

from decimal import Decimal
from src.financial_engine.validators import (
    validate_journal_entry_balance,
    validate_vat_calculation
)


def test_balanced_journal_entry():
    """Test that a balanced debit/credit entry passes validation."""
    lines = [
        {"account_code": "601000", "debit": 1150.00, "credit": 0.00},
        {"account_code": "201000", "debit": 0.00, "credit": 1000.00},
        {"account_code": "205000", "debit": 0.00, "credit": 150.00}
    ]
    is_valid, message, variance = validate_journal_entry_balance(lines)
    assert is_valid is True
    assert variance == Decimal('0.0000')


def test_unbalanced_journal_entry():
    """Test that an unbalanced entry fails validation and flags variance."""
    lines = [
        {"account_code": "601000", "debit": 1000.00, "credit": 0.00},
        {"account_code": "201000", "debit": 0.00, "credit": 900.00}
    ]
    is_valid, message, variance = validate_journal_entry_balance(lines)
    assert is_valid is False
    assert variance == Decimal('100.0000')


def test_valid_zatca_vat_calculation():
    """Test standard 15% ZATCA VAT calculation."""
    # Net: 1000.00 SAR, VAT Rate: 15% (0.15), Extracted VAT: 150.00 SAR, Gross: 1150.00 SAR
    is_valid, message = validate_vat_calculation(
        net_amount=1000.00,
        vat_rate=0.15,
        extracted_vat=150.00,
        extracted_gross=1150.00
    )
    assert is_valid is True


def test_invalid_zatca_vat_calculation():
    """Test VAT calculation mismatch detection."""
    # Extracted VAT is incorrectly set to 180.00 SAR instead of 150.00 SAR
    is_valid, message = validate_vat_calculation(
        net_amount=1000.00,
        vat_rate=0.15,
        extracted_vat=180.00,
        extracted_gross=1180.00
    )
    assert is_valid is False
    assert "VAT mismatch" in message
