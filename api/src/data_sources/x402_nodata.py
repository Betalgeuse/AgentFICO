"""
x402 NoData Source - Returns zero when no real data is available.

Since the x402 protocol standard is not yet finalized and there's no
real on-chain data to fetch, this source returns zeros instead of fake data.

This is more honest than mock data - it clearly indicates "no data available"
rather than generating misleading fake scores.
"""

from datetime import datetime
from typing import List

from .x402 import X402DataSource
from ..models.payment import X402Payment


class X402NoDataSource(X402DataSource):
    """
    NoData source that returns zeros for x402 metrics.
    
    Use this in production when:
    - x402 protocol is not finalized
    - No real payment data exists
    - We want honest "no data" instead of fake data
    """
    
    async def get_payments(
        self,
        agent_address: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[X402Payment]:
        """Return empty list - no real x402 payment data available."""
        return []
    
    async def calculate_profitability(
        self,
        agent_address: str,
        days: int = 30
    ) -> dict:
        """
        Return zero profitability - no real x402 data available.
        
        Returns:
            Dictionary with all values at 0, clearly indicating no data.
        """
        return {
            "address": agent_address.lower(),
            "total_income": 0.0,
            "total_expense": 0.0,
            "net_profit": 0.0,
            "roi_percent": 0.0,
            "score": 0,  # 0 = no data
            "transaction_count": 0,
            "period_days": days,
            "data_source": "nodata",
            "reason": "x402 protocol not yet finalized - no real data available"
        }
