"""
Deterministic Financial Engine - Validation Module
Handles mathematical, accounting rules, and tax compliance checks.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple

# Tolerance for floating point/decimal rounding differences (e.g. 0.0001)
CURRENCY_TOLERANCE = Decimal('0.0001')


def validate_journal_entry_balance(lines: List[Dict[str, Any]]) -> Tuple[bool, str, Decimal]:
    """
    Validates if Total Debits equal Total Credits for a journal entry draft.
    
    :param lines: List of dictionary lines containing 'debit' and 'credit' amounts.
    :return: Tuple of (is_valid: bool, message: str, variance: Decimal)
    """
    total_debit = Decimal('0.0000')
    total_credit = Decimal('0.0000')

    for index, line in enumerate(lines, start=1):
        debit = Decimal(str(line.get('debit', 0)))
        credit = Decimal(str(line.get('credit', 0)))

        if debit < 0 or credit < 0:
            return False, f"Line {index}: Negative amounts are not allowed.", Decimal('0.0000')

        total_debit += debit
        total_credit += credit

    variance = abs(total_debit - total_credit)

    if variance <= CURRENCY_TOLERANCE:
        return True, "Journal Entry is perfectly balanced.", Decimal('0.0000')
    else:
        return (
            False,
            f"Unbalanced Entry! Total Debits: {total_debit:.4f}, Total Credits: {total_credit:.4f}, Variance: {variance:.4f}",
            variance
        )


def validate_vat_calculation(
    net_amount: float,
    vat_rate: float,
    extracted_vat: float,
    extracted_gross: float
) -> Tuple[bool, str]:
    """
    Deterministically validates ZATCA VAT calculation (Net * Rate = VAT) and Gross Total.
    """
    net = Decimal(str(net_amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    rate = Decimal(str(vat_rate)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    ext_vat = Decimal(str(extracted_vat)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    ext_gross = Decimal(str(extracted_gross)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    expected_vat = (net * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    expected_gross = net + expected_vat

    vat_diff = abs(expected_vat - ext_vat)
    gross_diff = abs(expected_gross - ext_gross)

    if vat_diff > Decimal('0.01'):
        return False, f"VAT mismatch! Calculated: {expected_vat}, Invoice extracted: {ext_vat}"
    
    if gross_diff > Decimal('0.01'):
        return False, f"Gross total mismatch! Calculated: {expected_gross}, Invoice extracted: {ext_gross}"

    return True, "VAT and Gross calculations validated successfully."
