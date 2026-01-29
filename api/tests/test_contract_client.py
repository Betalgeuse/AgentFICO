"""Tests for ContractClient and contract API endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.contract_client import ContractClient


@pytest.fixture
def anyio_backend():
    """Specify the async backend for anyio."""
    return "asyncio"


@pytest.fixture
def mock_score_data():
    """Mock score data from contract."""
    return {
        "overall": 750,
        "txSuccess": 85,
        "x402Profitability": 70,
        "erc8004Stability": 80,
        "confidence": 90,
        "riskLevel": "low",
        "timestamp": 1706500000,
        "ipfsBreakdown": "QmTest123",
    }


@pytest.fixture
def mock_risk_data():
    """Mock risk assessment data from contract."""
    return {
        "riskLevel": 25,
        "defaultProbability": 10,
        "expectedLoss": 1000,
        "positiveFactors": ["High transaction success rate"],
        "riskFactors": [],
    }


class TestContractClientUnit:
    """Unit tests for ContractClient."""

    def test_init_without_private_key(self):
        """Test client initialization without private key."""
        with patch("src.services.contract_client.Web3") as mock_web3:
            mock_w3 = MagicMock()
            mock_web3.return_value = mock_w3
            mock_web3.HTTPProvider.return_value = MagicMock()
            mock_web3.to_checksum_address.return_value = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
            mock_w3.eth.contract.return_value = MagicMock()

            client = ContractClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
            )

            assert client.private_key is None
            assert client.account is None

    def test_init_with_private_key(self):
        """Test client initialization with private key."""
        with patch("src.services.contract_client.Web3") as mock_web3:
            mock_w3 = MagicMock()
            mock_web3.return_value = mock_w3
            mock_web3.HTTPProvider.return_value = MagicMock()
            mock_web3.to_checksum_address.return_value = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
            mock_w3.eth.contract.return_value = MagicMock()
            mock_account = MagicMock()
            mock_w3.eth.account.from_key.return_value = mock_account

            # Use a mock private key for testing (not a real key)
            mock_private_key = "0x" + "1" * 64  # Clearly fake test key
            client = ContractClient(
                rpc_url="http://127.0.0.1:8545",
                contract_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
                private_key=mock_private_key,
            )

            assert client.private_key is not None
            assert client.account is not None


class TestContractAPIEndpoints:
    """Tests for contract API endpoints."""

    @pytest.mark.anyio
    async def test_get_contract_stats_not_connected(self):
        """Test contract stats when not connected."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = False
            mock_client.contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/v1/contract/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["is_connected"] is False
            assert data["total_agents"] == 0
            assert data["contract_address"] == "0x5FbDB2315678afecb367f032d93F642f64180aa3"

    @pytest.mark.anyio
    async def test_get_contract_stats_connected(self):
        """Test contract stats when connected."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_client.contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"
            mock_client.get_total_agents = AsyncMock(return_value=5)
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get("/v1/contract/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["is_connected"] is True
            assert data["total_agents"] == 5

    @pytest.mark.anyio
    async def test_get_contract_score_not_connected(self):
        """Test get score when not connected."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = False
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/contract/score/0x1111111111111111111111111111111111111111"
                )

            assert response.status_code == 503
            assert "unavailable" in response.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_get_contract_score_success(self, mock_score_data):
        """Test successful score retrieval."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_client.get_score = AsyncMock(return_value=mock_score_data)
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/contract/score/0x1111111111111111111111111111111111111111"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["overall"] == 750
            assert data["txSuccess"] == 85
            assert data["riskLevel"] == "low"

    @pytest.mark.anyio
    async def test_get_contract_score_not_found(self):
        """Test score retrieval for unregistered agent."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_client.get_score = AsyncMock(
                side_effect=ValueError("Agent not registered")
            )
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/contract/score/0x1111111111111111111111111111111111111111"
                )

            assert response.status_code == 404

    @pytest.mark.anyio
    async def test_update_contract_score_success(self):
        """Test successful score update."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_client.update_score = AsyncMock(return_value="0xabc123...")
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/v1/contract/score/0x1111111111111111111111111111111111111111",
                    json={
                        "tx_success": 85,
                        "x402_profitability": 70,
                        "erc8004_stability": 80,
                        "confidence": 90,
                        "risk_level": "low",
                        "ipfs_breakdown": "QmTest123",
                    },
                )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "tx_hash" in data

    @pytest.mark.anyio
    async def test_update_contract_score_invalid_risk_level(self):
        """Test score update with invalid risk level."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.post(
                    "/v1/contract/score/0x1111111111111111111111111111111111111111",
                    json={
                        "tx_success": 85,
                        "x402_profitability": 70,
                        "erc8004_stability": 80,
                        "confidence": 90,
                        "risk_level": "invalid",  # Invalid
                    },
                )

            assert response.status_code == 422  # Validation error

    @pytest.mark.anyio
    async def test_assess_contract_risk_success(self, mock_risk_data):
        """Test successful risk assessment."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_client.assess_risk = AsyncMock(return_value=mock_risk_data)
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/contract/risk/0x1111111111111111111111111111111111111111",
                    params={"amount_usdc": 10000, "protocol_type": "lending"},
                )

            assert response.status_code == 200
            data = response.json()
            assert data["riskLevel"] == 25
            assert data["defaultProbability"] == 10
            assert "positiveFactors" in data
            assert "riskFactors" in data

    @pytest.mark.anyio
    async def test_assess_contract_risk_invalid_protocol(self):
        """Test risk assessment with invalid protocol type."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/contract/risk/0x1111111111111111111111111111111111111111",
                    params={"amount_usdc": 10000, "protocol_type": "invalid"},
                )

            assert response.status_code == 422  # Validation error

    @pytest.mark.anyio
    async def test_check_registered_success(self):
        """Test checking agent registration status."""
        with patch(
            "src.routes.contract.get_contract_client"
        ) as mock_get_client:
            mock_client = MagicMock()
            mock_client.is_connected.return_value = True
            mock_client.is_registered = AsyncMock(return_value=True)
            mock_get_client.return_value = mock_client

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/v1/contract/registered/0x1111111111111111111111111111111111111111"
                )

            assert response.status_code == 200
            data = response.json()
            assert data["is_registered"] is True
            assert "agent_address" in data
