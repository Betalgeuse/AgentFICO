"""Transaction model for blockchain transactions."""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class TransactionStatus(Enum):
    """Transaction execution status."""

    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class Transaction:
    """Represents a blockchain transaction.

    Attributes:
        hash: Transaction hash (0x...)
        from_address: Sender address
        to_address: Recipient address
        value: Transaction value in wei
        gas_used: Actual gas consumed
        gas_price: Gas price in wei
        status: Transaction execution status
        timestamp: Unix timestamp of block
        block_number: Block number containing this transaction
        method_id: Contract method ID (first 4 bytes of input data)
    """

    hash: str
    from_address: str
    to_address: str
    value: int  # wei
    gas_used: int
    gas_price: int
    status: TransactionStatus
    timestamp: int
    block_number: int
    method_id: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize addresses."""
        self.from_address = self.from_address.lower()
        if self.to_address:
            self.to_address = self.to_address.lower()
        self.hash = self.hash.lower()

    @property
    def gas_cost_wei(self) -> int:
        """Calculate total gas cost in wei."""
        return self.gas_used * self.gas_price

    @property
    def gas_cost_gwei(self) -> float:
        """Calculate total gas cost in Gwei."""
        return self.gas_cost_wei / 1e9

    @property
    def value_eth(self) -> float:
        """Convert value from wei to ETH."""
        return self.value / 1e18

    def is_contract_interaction(self) -> bool:
        """Check if this is a contract interaction (has method_id)."""
        return self.method_id is not None and self.method_id != "0x"
