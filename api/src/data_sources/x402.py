"""
x402 Protocol Data Source

Provides interfaces and implementations for fetching x402 protocol
payment data and calculating profitability metrics.

Since the x402 standard is not finalized yet, we provide:
1. Abstract interface (X402DataSource)
2. Mock implementation for development/testing (X402MockDataSource)
3. Placeholder for future on-chain implementation (X402OnchainDataSource)
"""

from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta
import random
import hashlib

from ..models.payment import X402Payment, PaymentType


def normalize_profitability_score(roi_percent: float) -> int:
    """
    Normalize ROI percentage to a 0-100 profitability score.
    
    ROI Mapping:
    - ROI >= 100%: 100 points
    - ROI 50-100%: 75-100 points
    - ROI 0-50%: 50-75 points
    - ROI -50-0%: 25-50 points
    - ROI < -50%: 0-25 points
    
    Args:
        roi_percent: Return on investment as a percentage
                    (e.g., 87.5 means 87.5% ROI)
    
    Returns:
        Normalized score between 0 and 100
    """
    if roi_percent >= 100:
        return 100
    elif roi_percent >= 50:
        # Linear interpolation: 50% -> 75, 100% -> 100
        return int(75 + (roi_percent - 50) * 0.5)
    elif roi_percent >= 0:
        # Linear interpolation: 0% -> 50, 50% -> 75
        return int(50 + roi_percent * 0.5)
    elif roi_percent >= -50:
        # Linear interpolation: -50% -> 25, 0% -> 50
        return int(25 + (roi_percent + 50) * 0.5)
    else:
        # Linear interpolation: -100% -> 0, -50% -> 25
        # Clamp at 0 for ROI < -100%
        score = int(25 + (roi_percent + 50) * 0.5)
        return max(0, score)


class X402DataSource(ABC):
    """
    Abstract base class for x402 data sources.
    
    Defines the interface that all x402 data source implementations
    must follow, whether mock, on-chain, or other sources.
    """
    
    @abstractmethod
    async def get_payments(
        self,
        agent_address: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[X402Payment]:
        """
        Retrieve x402 payment records for an agent.
        
        Args:
            agent_address: Ethereum address of the agent
            start_date: Start of the date range
            end_date: End of the date range
        
        Returns:
            List of X402Payment records
        """
        pass
    
    @abstractmethod
    async def calculate_profitability(
        self,
        agent_address: str,
        days: int = 30
    ) -> dict:
        """
        Calculate profitability metrics for an agent.
        
        Args:
            agent_address: Ethereum address of the agent
            days: Number of days to analyze (default: 30)
        
        Returns:
            Dictionary containing:
            {
                "address": "0x...",
                "total_income": 1500.00,      # USDC
                "total_expense": 800.00,       # USDC
                "net_profit": 700.00,          # USDC
                "roi_percent": 87.5,           # (profit / expense) * 100
                "score": 75,                   # 0-100 normalized profitability score
                "transaction_count": 45,
                "period_days": 30
            }
        """
        pass


class X402MockDataSource(X402DataSource):
    """
    Mock data source for development and testing.
    
    Generates consistent mock data based on agent address,
    ensuring the same address always produces the same results.
    
    Attributes:
        seed: Base seed for random number generation
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize mock data source.
        
        Args:
            seed: Base seed for deterministic random generation
        """
        self.seed = seed
    
    def _get_address_seed(self, agent_address: str) -> int:
        """
        Generate a consistent seed from agent address.
        
        Uses MD5 hash to ensure the same address always produces
        the same seed, making mock data deterministic.
        """
        # Use MD5 hash for consistent address-based seed
        address_hash = hashlib.md5(agent_address.lower().encode()).hexdigest()
        return int(address_hash[:8], 16) + self.seed
    
    async def get_payments(
        self,
        agent_address: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[X402Payment]:
        """
        Generate mock payment data for an agent.
        
        Creates a deterministic set of payments based on the agent address,
        with a mix of incoming and outgoing transactions.
        """
        # Set seed based on address for consistent results
        address_seed = self._get_address_seed(agent_address)
        rng = random.Random(address_seed)
        
        payments: List[X402Payment] = []
        
        # Calculate number of days in range
        days_range = (end_date - start_date).days
        if days_range <= 0:
            return payments
        
        # Generate between 10-50 transactions per period
        num_transactions = rng.randint(10, 50)
        
        service_types = ["api_call", "compute", "data", "storage", "inference"]
        
        for i in range(num_transactions):
            # Random timestamp within range
            random_days = rng.uniform(0, days_range)
            tx_timestamp = start_date + timedelta(days=random_days)
            
            # Generate transaction hash
            tx_hash = f"0x{hashlib.sha256(f'{agent_address}{i}{self.seed}'.encode()).hexdigest()}"
            
            # Generate counterparty address
            counterparty = f"0x{hashlib.sha256(f'counterparty{i}{address_seed}'.encode()).hexdigest()[:40]}"
            
            # Determine payment type (60% incoming, 40% outgoing for profitable agents)
            is_incoming = rng.random() < 0.6
            payment_type = PaymentType.INCOMING if is_incoming else PaymentType.OUTGOING
            
            # Amount varies by type
            if is_incoming:
                # Income: typically larger amounts
                amount = round(rng.uniform(10, 200), 2)
            else:
                # Expense: typically smaller amounts
                amount = round(rng.uniform(5, 100), 2)
            
            payment = X402Payment(
                tx_hash=tx_hash,
                agent_address=agent_address.lower(),
                counterparty=counterparty,
                amount_usdc=amount,
                payment_type=payment_type,
                timestamp=tx_timestamp,
                service_type=rng.choice(service_types)
            )
            payments.append(payment)
        
        # Sort by timestamp
        payments.sort(key=lambda p: p.timestamp)
        
        return payments
    
    async def calculate_profitability(
        self,
        agent_address: str,
        days: int = 30
    ) -> dict:
        """
        Calculate mock profitability metrics.
        
        Uses get_payments to generate consistent data, then calculates
        profitability metrics from that data.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        payments = await self.get_payments(agent_address, start_date, end_date)
        
        # Calculate totals
        total_income = sum(p.amount_usdc for p in payments if p.is_income())
        total_expense = sum(p.amount_usdc for p in payments if p.is_expense())
        net_profit = total_income - total_expense
        
        # Calculate ROI (return on investment)
        # ROI = (profit / expense) * 100
        if total_expense > 0:
            roi_percent = (net_profit / total_expense) * 100
        else:
            # If no expenses, ROI is infinite - cap at 100% for scoring
            roi_percent = 100.0 if total_income > 0 else 0.0
        
        # Normalize ROI to 0-100 score
        score = normalize_profitability_score(roi_percent)
        
        return {
            "address": agent_address.lower(),
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_profit": round(net_profit, 2),
            "roi_percent": round(roi_percent, 2),
            "score": score,
            "transaction_count": len(payments),
            "period_days": days
        }


class X402OnchainDataSource(X402DataSource):
    """
    On-chain data source for production use.
    
    Placeholder for future implementation once the x402 protocol
    standard is finalized. Will integrate with actual blockchain
    contracts to fetch real payment data.
    
    Attributes:
        rpc_url: Ethereum RPC endpoint URL
        contract_address: x402 protocol contract address
    """
    
    def __init__(self, rpc_url: str, contract_address: str):
        """
        Initialize on-chain data source.
        
        Args:
            rpc_url: Ethereum RPC endpoint URL
            contract_address: Address of the x402 protocol contract
        """
        self.rpc_url = rpc_url
        self.contract_address = contract_address
    
    async def get_payments(
        self,
        agent_address: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[X402Payment]:
        """
        Fetch payment data from blockchain.
        
        Not implemented - waiting for x402 protocol standard to be finalized.
        """
        raise NotImplementedError(
            "x402 on-chain data source not implemented. "
            "Waiting for x402 protocol standard to be finalized."
        )
    
    async def calculate_profitability(
        self,
        agent_address: str,
        days: int = 30
    ) -> dict:
        """
        Calculate profitability from on-chain data.
        
        Not implemented - waiting for x402 protocol standard to be finalized.
        """
        raise NotImplementedError(
            "x402 on-chain data source not implemented. "
            "Waiting for x402 protocol standard to be finalized."
        )
