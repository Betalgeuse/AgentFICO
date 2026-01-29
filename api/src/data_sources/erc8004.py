"""ERC-8004 Data Source Interface and Implementations.

This module provides interfaces and implementations for accessing ERC-8004
agent registry data. Since the ERC-8004 standard is not yet finalized,
a mock implementation is provided for development and testing.

Classes:
    ERC8004DataSource: Abstract base class defining the interface.
    ERC8004MockDataSource: Mock implementation with predefined test data.
    ERC8004OnchainDataSource: Placeholder for future on-chain implementation.
"""
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

from api.src.models.agent_registry import AgentMetadata, VerificationLevel


class ERC8004DataSource(ABC):
    """Abstract interface for ERC-8004 registry data sources.

    This interface defines the methods required to interact with an ERC-8004
    compatible agent registry. Implementations can be mock data, on-chain
    contract calls, or subgraph queries.
    """

    @abstractmethod
    async def get_agent_metadata(
        self, agent_address: str
    ) -> Optional[AgentMetadata]:
        """Retrieve metadata for a registered agent.

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            AgentMetadata if the agent is registered, None otherwise.
        """
        pass

    @abstractmethod
    async def is_registered(self, agent_address: str) -> bool:
        """Check if an agent is registered in the registry.

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            True if the agent is registered, False otherwise.
        """
        pass

    @abstractmethod
    async def calculate_stability_score(self, agent_address: str) -> dict:
        """Calculate the stability score for an agent.

        The stability score evaluates the agent's reliability based on:
        - Registration status (20 points)
        - Verification level (30 points)
        - Metadata completeness (20 points)
        - Activity duration (20 points)
        - Reputation score (10 points)

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            A dictionary containing:
                - address: The agent's address
                - is_registered: Whether the agent is registered
                - verification_level: The verification level (0-5)
                - metadata_completeness: Percentage of metadata filled (0-100)
                - activity_days: Number of days since registration
                - reputation_score: Community reputation score (0-5)
                - score: Final stability score (0-100)
                - factors: Breakdown of score components
        """
        pass


class ERC8004MockDataSource(ERC8004DataSource):
    """Mock implementation of ERC-8004 data source.

    This implementation provides predefined test data for development
    and testing purposes. It simulates various agent profiles with
    different verification levels and activity patterns.
    """

    def __init__(self, seed: int = 42):
        """Initialize the mock data source.

        Args:
            seed: Random seed for consistent mock data generation.
        """
        self.seed = seed
        self._mock_agents: Dict[str, dict] = {
            # Excellent agent - high verification, long activity, complete metadata
            "0x1111111111111111111111111111111111111111": {
                "name": "TradingBot Alpha",
                "description": "High-frequency trading bot with proven track record",
                "owner": "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "verification_level": VerificationLevel.PREMIUM,
                "activity_days": 365,
                "metadata_completeness": 100,
                "reputation_score": 4.8,
                "capabilities": ["trading", "defi", "arbitrage"],
                "website_url": "https://tradingbot-alpha.io",
                "github_url": "https://github.com/tradingbot-alpha",
                "audit_report_url": "https://audits.io/tradingbot-alpha",
            },
            # Average agent - moderate verification, decent activity
            "0x2222222222222222222222222222222222222222": {
                "name": "DataAgent Beta",
                "description": "Data analysis and oracle services",
                "owner": "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "verification_level": VerificationLevel.STANDARD,
                "activity_days": 90,
                "metadata_completeness": 70,
                "reputation_score": 3.5,
                "capabilities": ["data_analysis", "oracle"],
                "website_url": "https://dataagent-beta.io",
                "github_url": None,
                "audit_report_url": None,
            },
            # Poor agent - unverified, new, incomplete metadata
            "0x3333333333333333333333333333333333333333": {
                "name": "NewAgent Gamma",
                "description": None,
                "owner": "0xcccccccccccccccccccccccccccccccccccccccc",
                "verification_level": VerificationLevel.UNVERIFIED,
                "activity_days": 7,
                "metadata_completeness": 30,
                "reputation_score": 1.0,
                "capabilities": [],
                "website_url": None,
                "github_url": None,
                "audit_report_url": None,
            },
            # Good agent - advanced verification, moderate activity
            "0x4444444444444444444444444444444444444444": {
                "name": "PaymentBot Delta",
                "description": "Automated payment processing agent",
                "owner": "0xdddddddddddddddddddddddddddddddddddddddd",
                "verification_level": VerificationLevel.ADVANCED,
                "activity_days": 180,
                "metadata_completeness": 85,
                "reputation_score": 4.2,
                "capabilities": ["payment", "escrow"],
                "website_url": "https://paymentbot-delta.io",
                "github_url": "https://github.com/paymentbot-delta",
                "audit_report_url": None,
            },
        }

    def _generate_deterministic_data(self, agent_address: str) -> dict:
        """Generate deterministic mock data for unknown agents.

        Uses a hash of the address and seed to generate consistent
        but varied data for any address not in the predefined list.

        Args:
            agent_address: The Ethereum address to generate data for.

        Returns:
            A dictionary with mock agent data.
        """
        # Create a deterministic hash from address and seed
        hash_input = f"{agent_address.lower()}{self.seed}"
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()

        # Use hash bytes to generate values
        verification_level = VerificationLevel(hash_bytes[0] % 6)
        activity_days = (hash_bytes[1] * hash_bytes[2]) % 730  # 0-730 days
        metadata_completeness = 30 + (hash_bytes[3] % 71)  # 30-100%
        reputation_score = round(1.0 + (hash_bytes[4] % 41) / 10, 1)  # 1.0-5.0

        return {
            "name": f"Agent-{agent_address[2:8]}",
            "description": f"Auto-generated agent {agent_address[:10]}...",
            "owner": f"0x{'0' * 38}{agent_address[2:4]}",
            "verification_level": verification_level,
            "activity_days": activity_days,
            "metadata_completeness": metadata_completeness,
            "reputation_score": reputation_score,
            "capabilities": ["general"],
            "website_url": None,
            "github_url": None,
            "audit_report_url": None,
        }

    def _get_agent_data(self, agent_address: str) -> Optional[dict]:
        """Get agent data from predefined or generated sources.

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            Agent data dictionary or None if not registered.
        """
        # Normalize address to lowercase
        normalized = agent_address.lower()

        # Check predefined agents first
        for addr, data in self._mock_agents.items():
            if addr.lower() == normalized:
                return data

        # For unknown addresses, check if it looks like a valid address
        if not normalized.startswith("0x") or len(normalized) != 42:
            return None

        # Generate deterministic data for unknown addresses
        # Addresses starting with 0x00 are considered unregistered
        if normalized.startswith("0x00"):
            return None

        return self._generate_deterministic_data(agent_address)

    async def get_agent_metadata(
        self, agent_address: str
    ) -> Optional[AgentMetadata]:
        """Retrieve metadata for a registered agent.

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            AgentMetadata if the agent is registered, None otherwise.
        """
        data = self._get_agent_data(agent_address)
        if data is None:
            return None

        # Calculate registration date based on activity days
        registered_at = datetime.now(timezone.utc) - timedelta(
            days=data["activity_days"]
        )

        return AgentMetadata(
            agent_address=agent_address,
            name=data["name"],
            description=data.get("description"),
            owner=data["owner"],
            registered_at=registered_at,
            verification_level=data["verification_level"],
            capabilities=data.get("capabilities", []),
            website_url=data.get("website_url"),
            github_url=data.get("github_url"),
            audit_report_url=data.get("audit_report_url"),
        )

    async def is_registered(self, agent_address: str) -> bool:
        """Check if an agent is registered in the registry.

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            True if the agent is registered, False otherwise.
        """
        return self._get_agent_data(agent_address) is not None

    async def calculate_stability_score(self, agent_address: str) -> dict:
        """Calculate the stability score for an agent.

        Score breakdown (total 100 points):
        - Registration: 20 points (registered = 20, unregistered = 0)
        - Verification: 30 points (level × 6, max 30)
        - Metadata: 20 points (completeness% × 0.2, max 20)
        - Activity: 20 points (min(days/365, 1) × 20, max 20)
        - Reputation: 10 points (reputation/5 × 10, max 10)

        Args:
            agent_address: The Ethereum address of the agent.

        Returns:
            A dictionary with score breakdown and factors.
        """
        data = self._get_agent_data(agent_address)

        if data is None:
            # Unregistered agent
            return {
                "address": agent_address,
                "is_registered": False,
                "verification_level": 0,
                "metadata_completeness": 0,
                "activity_days": 0,
                "reputation_score": 0.0,
                "score": 0,
                "factors": {
                    "registration": 0,
                    "verification": 0,
                    "metadata": 0,
                    "activity": 0,
                    "reputation": 0,
                },
            }

        # Extract values
        verification_level = int(data["verification_level"])
        metadata_completeness = data["metadata_completeness"]
        activity_days = data["activity_days"]
        reputation_score = data["reputation_score"]

        # Calculate factor scores
        registration_score = 20  # Registered = 20 points
        verification_score = min(verification_level * 6, 30)  # Max 30 points
        metadata_score = int(metadata_completeness * 0.2)  # Max 20 points
        activity_score = int(min(activity_days / 365, 1.0) * 20)  # Max 20 points
        reputation_factor = int((reputation_score / 5.0) * 10)  # Max 10 points

        # Calculate total score
        total_score = (
            registration_score
            + verification_score
            + metadata_score
            + activity_score
            + reputation_factor
        )

        return {
            "address": agent_address,
            "is_registered": True,
            "verification_level": verification_level,
            "metadata_completeness": metadata_completeness,
            "activity_days": activity_days,
            "reputation_score": reputation_score,
            "score": total_score,
            "factors": {
                "registration": registration_score,
                "verification": verification_score,
                "metadata": metadata_score,
                "activity": activity_score,
                "reputation": reputation_factor,
            },
        }


class ERC8004OnchainDataSource(ERC8004DataSource):
    """On-chain implementation of ERC-8004 data source.

    This is a placeholder for the future on-chain implementation.
    It will connect to the actual ERC-8004 registry smart contract
    once the standard is finalized.
    """

    def __init__(self, rpc_url: str, registry_address: str):
        """Initialize the on-chain data source.

        Args:
            rpc_url: The RPC URL for the Ethereum node.
            registry_address: The address of the ERC-8004 registry contract.
        """
        self.rpc_url = rpc_url
        self.registry_address = registry_address

    async def get_agent_metadata(
        self, agent_address: str
    ) -> Optional[AgentMetadata]:
        """Retrieve metadata from the on-chain registry.

        Raises:
            NotImplementedError: ERC-8004 standard is not yet finalized.
        """
        raise NotImplementedError(
            "ERC-8004 standard is not yet finalized. "
            "Use ERC8004MockDataSource for development."
        )

    async def is_registered(self, agent_address: str) -> bool:
        """Check if an agent is registered on-chain.

        Raises:
            NotImplementedError: ERC-8004 standard is not yet finalized.
        """
        raise NotImplementedError(
            "ERC-8004 standard is not yet finalized. "
            "Use ERC8004MockDataSource for development."
        )

    async def calculate_stability_score(self, agent_address: str) -> dict:
        """Calculate stability score from on-chain data.

        Raises:
            NotImplementedError: ERC-8004 standard is not yet finalized.
        """
        raise NotImplementedError(
            "ERC-8004 standard is not yet finalized. "
            "Use ERC8004MockDataSource for development."
        )
