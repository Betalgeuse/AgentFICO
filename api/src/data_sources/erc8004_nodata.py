"""
ERC-8004 NoData Source - Returns zero when no real registry data is available.

Since ERC-8004 standard is not yet finalized and most agents are not
registered, this source returns zeros instead of generating fake data.

This is more honest than mock data - it clearly indicates "not registered"
rather than generating misleading fake scores.
"""

from typing import Optional

from .erc8004 import ERC8004DataSource
from ..models.agent_registry import AgentMetadata


class ERC8004NoDataSource(ERC8004DataSource):
    """
    NoData source that returns zeros for ERC-8004 metrics.
    
    Use this in production when:
    - ERC-8004 standard is not finalized
    - Agent is not actually registered
    - We want honest "not registered" instead of fake data
    """
    
    async def get_agent_metadata(
        self, agent_address: str
    ) -> Optional[AgentMetadata]:
        """Return None - agent not registered in any real registry."""
        return None
    
    async def is_registered(self, agent_address: str) -> bool:
        """Return False - no real registry to check."""
        return False
    
    async def calculate_stability_score(self, agent_address: str) -> dict:
        """
        Return zero stability score - not registered.
        
        Returns:
            Dictionary with all values at 0, clearly indicating not registered.
        """
        return {
            "address": agent_address.lower(),
            "is_registered": False,
            "verification_level": 0,
            "metadata_completeness": 0,
            "activity_days": 0,
            "reputation_score": 0.0,
            "score": 0,  # 0 = not registered
            "factors": {
                "registration": 0,
                "verification": 0,
                "metadata": 0,
                "activity": 0,
                "reputation": 0,
            },
            "data_source": "nodata",
            "reason": "ERC-8004 registry not available - agent not registered"
        }
