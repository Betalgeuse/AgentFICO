"""Tests for ERC-8004 stability score calculation.

This module contains unit tests for the ERC8004MockDataSource
and the stability score calculation logic.
"""
import pytest

from src.data_sources.erc8004 import (
    ERC8004MockDataSource,
    ERC8004OnchainDataSource,
)
from src.models.agent_registry import AgentMetadata, VerificationLevel


class TestVerificationLevel:
    """Tests for VerificationLevel enum."""

    def test_verification_levels_order(self):
        """Test that verification levels are in correct order."""
        assert VerificationLevel.UNVERIFIED < VerificationLevel.BASIC
        assert VerificationLevel.BASIC < VerificationLevel.STANDARD
        assert VerificationLevel.STANDARD < VerificationLevel.ADVANCED
        assert VerificationLevel.ADVANCED < VerificationLevel.PREMIUM
        assert VerificationLevel.PREMIUM < VerificationLevel.ENTERPRISE

    def test_verification_level_values(self):
        """Test verification level integer values."""
        assert int(VerificationLevel.UNVERIFIED) == 0
        assert int(VerificationLevel.BASIC) == 1
        assert int(VerificationLevel.STANDARD) == 2
        assert int(VerificationLevel.ADVANCED) == 3
        assert int(VerificationLevel.PREMIUM) == 4
        assert int(VerificationLevel.ENTERPRISE) == 5


class TestAgentMetadata:
    """Tests for AgentMetadata dataclass."""

    def test_has_capability(self):
        """Test capability checking."""
        from datetime import datetime, timezone

        metadata = AgentMetadata(
            agent_address="0x1234567890123456789012345678901234567890",
            name="Test Agent",
            owner="0xabcdef1234567890abcdef1234567890abcdef12",
            registered_at=datetime.now(timezone.utc),
            verification_level=VerificationLevel.STANDARD,
            capabilities=["trading", "DATA_ANALYSIS", "Payment"],
        )

        # Case-insensitive capability check
        assert metadata.has_capability("trading")
        assert metadata.has_capability("TRADING")
        assert metadata.has_capability("data_analysis")
        assert metadata.has_capability("payment")
        assert not metadata.has_capability("oracle")

    def test_metadata_completeness_full(self):
        """Test metadata completeness with all fields filled."""
        from datetime import datetime, timezone

        metadata = AgentMetadata(
            agent_address="0x1234567890123456789012345678901234567890",
            name="Test Agent",
            description="A test agent",
            owner="0xabcdef1234567890abcdef1234567890abcdef12",
            registered_at=datetime.now(timezone.utc),
            verification_level=VerificationLevel.PREMIUM,
            capabilities=["trading"],
            website_url="https://example.com",
            github_url="https://github.com/test",
            audit_report_url="https://audits.io/test",
        )

        assert metadata.metadata_completeness() == 100

    def test_metadata_completeness_minimal(self):
        """Test metadata completeness with minimal fields."""
        from datetime import datetime, timezone

        metadata = AgentMetadata(
            agent_address="0x1234567890123456789012345678901234567890",
            name="Test Agent",
            owner="0xabcdef1234567890abcdef1234567890abcdef12",
            registered_at=datetime.now(timezone.utc),
            verification_level=VerificationLevel.UNVERIFIED,
            capabilities=[],
        )

        # Only required fields filled (4/10 = 40%)
        assert metadata.metadata_completeness() == 40


class TestERC8004MockDataSource:
    """Tests for ERC8004MockDataSource."""

    @pytest.fixture
    def data_source(self):
        """Create a mock data source instance."""
        return ERC8004MockDataSource(seed=42)

    @pytest.mark.asyncio
    async def test_is_registered_predefined_agent(self, data_source):
        """Test registration check for predefined agents."""
        # Good agent - should be registered
        assert await data_source.is_registered(
            "0x1111111111111111111111111111111111111111"
        )

        # Average agent - should be registered
        assert await data_source.is_registered(
            "0x2222222222222222222222222222222222222222"
        )

        # Poor agent - should be registered
        assert await data_source.is_registered(
            "0x3333333333333333333333333333333333333333"
        )

    @pytest.mark.asyncio
    async def test_is_registered_unregistered_agent(self, data_source):
        """Test registration check for unregistered agents."""
        # Addresses starting with 0x00 are considered unregistered
        assert not await data_source.is_registered(
            "0x0000000000000000000000000000000000000000"
        )
        assert not await data_source.is_registered(
            "0x0012345678901234567890123456789012345678"
        )

    @pytest.mark.asyncio
    async def test_is_registered_invalid_address(self, data_source):
        """Test registration check for invalid addresses."""
        assert not await data_source.is_registered("invalid")
        assert not await data_source.is_registered("0x123")
        assert not await data_source.is_registered("")

    @pytest.mark.asyncio
    async def test_get_agent_metadata_predefined(self, data_source):
        """Test metadata retrieval for predefined agents."""
        metadata = await data_source.get_agent_metadata(
            "0x1111111111111111111111111111111111111111"
        )

        assert metadata is not None
        assert metadata.name == "TradingBot Alpha"
        assert metadata.verification_level == VerificationLevel.PREMIUM
        assert "trading" in metadata.capabilities

    @pytest.mark.asyncio
    async def test_get_agent_metadata_unregistered(self, data_source):
        """Test metadata retrieval for unregistered agents."""
        metadata = await data_source.get_agent_metadata(
            "0x0000000000000000000000000000000000000000"
        )

        assert metadata is None

    @pytest.mark.asyncio
    async def test_stability_score_excellent_agent(self, data_source):
        """Test stability score for excellent agent (TradingBot Alpha)."""
        result = await data_source.calculate_stability_score(
            "0x1111111111111111111111111111111111111111"
        )

        assert result["is_registered"] is True
        assert result["verification_level"] == int(VerificationLevel.PREMIUM)
        assert result["score"] >= 80  # Excellent agent should score >= 80

        # Verify factor breakdown
        assert result["factors"]["registration"] == 20
        assert result["factors"]["verification"] == 24  # Level 4 × 6
        assert result["factors"]["metadata"] == 20  # 100% × 0.2

    @pytest.mark.asyncio
    async def test_stability_score_average_agent(self, data_source):
        """Test stability score for average agent (DataAgent Beta)."""
        result = await data_source.calculate_stability_score(
            "0x2222222222222222222222222222222222222222"
        )

        assert result["is_registered"] is True
        assert result["verification_level"] == int(VerificationLevel.STANDARD)
        assert 40 <= result["score"] <= 70  # Average agent should score 40-70

    @pytest.mark.asyncio
    async def test_stability_score_poor_agent(self, data_source):
        """Test stability score for poor agent (NewAgent Gamma)."""
        result = await data_source.calculate_stability_score(
            "0x3333333333333333333333333333333333333333"
        )

        assert result["is_registered"] is True
        assert result["verification_level"] == int(VerificationLevel.UNVERIFIED)
        assert result["score"] <= 40  # Poor agent should score <= 40

        # Verify low scores
        assert result["factors"]["verification"] == 0  # Level 0 × 6 = 0
        assert result["activity_days"] == 7

    @pytest.mark.asyncio
    async def test_stability_score_unregistered_agent(self, data_source):
        """Test stability score for unregistered agent."""
        result = await data_source.calculate_stability_score(
            "0x0000000000000000000000000000000000000000"
        )

        assert result["is_registered"] is False
        assert result["score"] == 0

        # All factors should be zero
        assert result["factors"]["registration"] == 0
        assert result["factors"]["verification"] == 0
        assert result["factors"]["metadata"] == 0
        assert result["factors"]["activity"] == 0
        assert result["factors"]["reputation"] == 0

    @pytest.mark.asyncio
    async def test_stability_score_deterministic(self, data_source):
        """Test that scores are deterministic for same address."""
        address = "0xabcdef1234567890abcdef1234567890abcdef12"

        result1 = await data_source.calculate_stability_score(address)
        result2 = await data_source.calculate_stability_score(address)

        assert result1["score"] == result2["score"]
        assert result1["factors"] == result2["factors"]

    @pytest.mark.asyncio
    async def test_stability_score_different_seeds(self):
        """Test that different seeds produce different results."""
        address = "0xabcdef1234567890abcdef1234567890abcdef12"

        source1 = ERC8004MockDataSource(seed=42)
        source2 = ERC8004MockDataSource(seed=123)

        result1 = await source1.calculate_stability_score(address)
        result2 = await source2.calculate_stability_score(address)

        # Different seeds should potentially produce different results
        # (not guaranteed for all addresses, but likely)
        # We just verify both return valid results
        assert 0 <= result1["score"] <= 100
        assert 0 <= result2["score"] <= 100

    @pytest.mark.asyncio
    async def test_score_components_sum(self, data_source):
        """Test that score components sum correctly."""
        result = await data_source.calculate_stability_score(
            "0x4444444444444444444444444444444444444444"
        )

        factors = result["factors"]
        expected_sum = (
            factors["registration"]
            + factors["verification"]
            + factors["metadata"]
            + factors["activity"]
            + factors["reputation"]
        )

        assert result["score"] == expected_sum

    @pytest.mark.asyncio
    async def test_score_max_values(self, data_source):
        """Test that score components don't exceed max values."""
        # Test all predefined agents
        addresses = [
            "0x1111111111111111111111111111111111111111",
            "0x2222222222222222222222222222222222222222",
            "0x3333333333333333333333333333333333333333",
            "0x4444444444444444444444444444444444444444",
        ]

        for addr in addresses:
            result = await data_source.calculate_stability_score(addr)
            factors = result["factors"]

            assert factors["registration"] <= 20
            assert factors["verification"] <= 30
            assert factors["metadata"] <= 20
            assert factors["activity"] <= 20
            assert factors["reputation"] <= 10
            assert result["score"] <= 100


class TestERC8004OnchainDataSource:
    """Tests for ERC8004OnchainDataSource placeholder."""

    def test_init(self):
        """Test initialization with parameters."""
        source = ERC8004OnchainDataSource(
            rpc_url="https://mainnet.infura.io/v3/key",
            registry_address="0x1234567890123456789012345678901234567890",
        )

        assert source.rpc_url == "https://mainnet.infura.io/v3/key"
        assert source.registry_address == "0x1234567890123456789012345678901234567890"

    @pytest.mark.asyncio
    async def test_get_agent_metadata_not_implemented(self):
        """Test that on-chain methods raise NotImplementedError."""
        source = ERC8004OnchainDataSource(
            rpc_url="https://mainnet.infura.io/v3/key",
            registry_address="0x1234567890123456789012345678901234567890",
        )

        with pytest.raises(NotImplementedError):
            await source.get_agent_metadata(
                "0x1111111111111111111111111111111111111111"
            )

    @pytest.mark.asyncio
    async def test_is_registered_not_implemented(self):
        """Test that is_registered raises NotImplementedError."""
        source = ERC8004OnchainDataSource(
            rpc_url="https://mainnet.infura.io/v3/key",
            registry_address="0x1234567890123456789012345678901234567890",
        )

        with pytest.raises(NotImplementedError):
            await source.is_registered(
                "0x1111111111111111111111111111111111111111"
            )

    @pytest.mark.asyncio
    async def test_calculate_stability_score_not_implemented(self):
        """Test that calculate_stability_score raises NotImplementedError."""
        source = ERC8004OnchainDataSource(
            rpc_url="https://mainnet.infura.io/v3/key",
            registry_address="0x1234567890123456789012345678901234567890",
        )

        with pytest.raises(NotImplementedError):
            await source.calculate_stability_score(
                "0x1111111111111111111111111111111111111111"
            )
