"""
x402 Protocol Payment Models

x402 is a payment protocol based on HTTP 402 Payment Required status code
for AI agent transactions.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import datetime


class PaymentType(Enum):
    """Payment direction type"""
    INCOMING = "incoming"  # Revenue (수익)
    OUTGOING = "outgoing"  # Expense (지출)


@dataclass
class X402Payment:
    """
    x402 Protocol Payment Record
    
    Represents a single payment transaction in the x402 protocol.
    Can be either incoming (revenue) or outgoing (expense).
    
    Attributes:
        tx_hash: Transaction hash on the blockchain
        agent_address: Ethereum address of the agent
        counterparty: Address of the other party in the transaction
        amount_usdc: Payment amount in USDC
        payment_type: Whether this is incoming or outgoing payment
        timestamp: When the payment occurred
        service_type: Type of service (e.g., "api_call", "compute", "data")
    """
    tx_hash: str
    agent_address: str
    counterparty: str
    amount_usdc: float
    payment_type: PaymentType
    timestamp: datetime
    service_type: Optional[str] = None  # "api_call", "compute", "data"
    
    def is_income(self) -> bool:
        """Check if this payment is income (revenue)"""
        return self.payment_type == PaymentType.INCOMING
    
    def is_expense(self) -> bool:
        """Check if this payment is expense (outgoing)"""
        return self.payment_type == PaymentType.OUTGOING
