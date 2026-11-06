"""
ERP Connectivity Layer - Base Abstract ERP Connector
Defines the standardized interface required for pushing posted journal entries
and fetching Chart of Accounts from any ERP system (Odoo, SAP, Oracle, Dynamics).
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseERPConnector(ABC):
    """
    Abstract Base Class for all ERP Integration Connectors.
    """

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticates with the target ERP system credentials/tokens."""
        pass

    @abstractmethod
    def fetch_chart_of_accounts(self, company_id: str = "1") -> List[Dict[str, Any]]:
        """Retrieves active GL accounts from the ERP system to synchronize local COA."""
        pass

    @abstractmethod
    def post_journal_entry(self, approved_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pushes an approved journal entry draft into the ERP system's general ledger.
        Must return the ERP's unique transaction reference ID.
        """
        pass
