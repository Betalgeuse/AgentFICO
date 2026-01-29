"""ERC-8004 Agent Registry Models.

This module defines the data structures for AI agents registered under
the ERC-8004 standard (currently a proposed standard, not yet finalized).
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import List, Optional


class VerificationLevel(IntEnum):
    """Verification level for registered agents.

    Higher levels indicate more thorough verification by trusted third parties.
    
    Levels:
        UNVERIFIED (0): No verification performed
        BASIC (1): Basic identity verification
        STANDARD (2): Standard verification with basic audit
        ADVANCED (3): Advanced verification with code review
        PREMIUM (4): Premium verification with full security audit
        ENTERPRISE (5): Enterprise-grade verification with continuous monitoring
    """

    UNVERIFIED = 0
    BASIC = 1
    STANDARD = 2
    ADVANCED = 3
    PREMIUM = 4
    ENTERPRISE = 5


@dataclass
class AgentMetadata:
    """ERC-8004 Agent Metadata.

    Represents the metadata of an AI agent registered in the ERC-8004 registry.
    This includes identity information, verification status, and capabilities.

    Attributes:
        agent_address: The Ethereum address of the agent.
        name: Human-readable name of the agent.
        owner: The address of the agent's owner/deployer.
        registered_at: Timestamp when the agent was registered.
        verification_level: The agent's verification level (0-5).
        capabilities: List of capability tags (e.g., "trading", "data_analysis").
        description: Optional description of the agent's purpose.
        website_url: Optional URL to the agent's website or documentation.
        github_url: Optional URL to the agent's source code repository.
        audit_report_url: Optional URL to security audit report.
    """

    agent_address: str
    name: str
    owner: str
    registered_at: datetime
    verification_level: VerificationLevel
    capabilities: List[str] = field(default_factory=list)
    description: Optional[str] = None
    website_url: Optional[str] = None
    github_url: Optional[str] = None
    audit_report_url: Optional[str] = None

    def has_capability(self, capability: str) -> bool:
        """Check if the agent has a specific capability.

        Args:
            capability: The capability to check for.

        Returns:
            True if the agent has the capability, False otherwise.
        """
        return capability.lower() in [c.lower() for c in self.capabilities]

    def metadata_completeness(self) -> int:
        """Calculate the completeness of the agent's metadata.

        Returns:
            A percentage (0-100) indicating how complete the metadata is.
        """
        total_fields = 10  # Total number of optional/required fields
        filled_fields = 0

        # Required fields (always count)
        filled_fields += 4  # agent_address, name, owner, registered_at are required

        # Optional fields
        if self.description:
            filled_fields += 1
        if self.website_url:
            filled_fields += 1
        if self.github_url:
            filled_fields += 1
        if self.audit_report_url:
            filled_fields += 1
        if self.capabilities:
            filled_fields += 1
        if self.verification_level > VerificationLevel.UNVERIFIED:
            filled_fields += 1

        return int((filled_fields / total_fields) * 100)
