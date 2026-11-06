"""
AI Abstraction Layer - Base Provider Adapter
Enforces provider-agnostic interface for Document OCR Extraction & GL Account Suggestion.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BaseAIAdapter(ABC):
    """
    Abstract Base Class defining the contract for all AI Model Providers 
    (e.g., GeminiAdapter, OpenAIAdapter, ClaudeAdapter).
    """

    @abstractmethod
    def extract_invoice_data(self, file_path_or_bytes: Any, language: str = "ar/en") -> Dict[str, Any]:
        """
        Extracts structured financial data from invoice images/PDFs.
        
        Must return a standardized dictionary containing:
        - supplier_name, vat_number, invoice_number, invoice_date
        - line_items (list of items, quantities, unit prices)
        - net_amount, vat_amount, gross_amount
        - confidence_score
        """
        pass

    @abstractmethod
    def suggest_gl_account(
        self, 
        vendor_name: str, 
        line_item_description: str, 
        chart_of_accounts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyzes line item description and suggests the best matching GL Account code from the company COA.
        
        Must return:
        - suggested_account_code
        - confidence_score
        - explanation_ar / explanation_en
        """
        pass
