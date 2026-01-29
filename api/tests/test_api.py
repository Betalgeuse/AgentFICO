"""Tests for FastAPI endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
def anyio_backend():
    """Specify the async backend for anyio."""
    return "asyncio"


@pytest.fixture
def mock_etherscan_response():
    """Mock response for Etherscan API."""
    return {
        "address": "0x1111111111111111111111111111111111111111",
        "total_txs": 100,
        "successful_txs": 95,
        "failed_txs": 5,
        "pending_txs": 0,
        "success_rate": 95.0,
        "score": 95,
        "period_days": 30,
        "analyzed_at": "2026-01-29T12:00:00Z",
    }


@pytest.mark.anyio
async def test_health_check():
    """Test health check endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.anyio
async def test_root():
    """Test root endpoint."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AgentFICO API"
    assert "docs" in data


@pytest.mark.anyio
async def test_get_score(mock_etherscan_response):
    """Test score retrieval endpoint."""
    with patch(
        "src.data_sources.etherscan.EtherscanClient.get_agent_tx_success_score",
        new_callable=AsyncMock,
    ) as mock_eth:
        mock_eth.return_value = mock_etherscan_response
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/v1/score/0x1111111111111111111111111111111111111111"
            )
        assert response.status_code == 200
        data = response.json()

        # Check required fields
        assert "overall" in data
        assert "riskLevel" in data  # camelCase
        assert "txSuccess" in data
        assert "x402Profitability" in data
        assert "erc8004Stability" in data
        assert "confidence" in data
        assert "timestamp" in data

        # Check value ranges
        assert 0 <= data["overall"] <= 1000
        assert 1 <= data["riskLevel"] <= 5
        assert 0 <= data["txSuccess"] <= 100
        assert 0 <= data["confidence"] <= 100


@pytest.mark.anyio
async def test_get_score_with_days_param(mock_etherscan_response):
    """Test score retrieval with custom days parameter."""
    with patch(
        "src.data_sources.etherscan.EtherscanClient.get_agent_tx_success_score",
        new_callable=AsyncMock,
    ) as mock_eth:
        mock_eth.return_value = mock_etherscan_response
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/v1/score/0x1111111111111111111111111111111111111111?days=60"
            )
        assert response.status_code == 200


@pytest.mark.anyio
async def test_invalid_address():
    """Test error handling for invalid address."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/score/invalid")
    assert response.status_code == 400
    data = response.json()
    assert "invalid_address" in str(data)


@pytest.mark.anyio
async def test_invalid_address_short():
    """Test error handling for short address."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/v1/score/0x123")
    assert response.status_code == 400


@pytest.mark.anyio
async def test_get_score_history(mock_etherscan_response):
    """Test score history endpoint."""
    with patch(
        "src.data_sources.etherscan.EtherscanClient.get_agent_tx_success_score",
        new_callable=AsyncMock,
    ) as mock_eth:
        mock_eth.return_value = mock_etherscan_response
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/v1/score/0x1111111111111111111111111111111111111111/history"
            )
        assert response.status_code == 200
        data = response.json()

        assert "agentAddress" in data
        assert "history" in data
        assert "totalCount" in data
        assert isinstance(data["history"], list)
        assert data["totalCount"] >= 1


@pytest.mark.anyio
async def test_refresh_score(mock_etherscan_response):
    """Test score refresh endpoint."""
    with patch(
        "src.data_sources.etherscan.EtherscanClient.get_agent_tx_success_score",
        new_callable=AsyncMock,
    ) as mock_eth:
        mock_eth.return_value = mock_etherscan_response
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v1/score/0x1111111111111111111111111111111111111111/refresh"
            )
        assert response.status_code == 200
        data = response.json()

        assert "overall" in data
        assert "riskLevel" in data


@pytest.mark.anyio
async def test_days_param_validation():
    """Test days parameter validation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # days < 1 should fail
        response = await client.get(
            "/v1/score/0x1111111111111111111111111111111111111111?days=0"
        )
        assert response.status_code == 422

        # days > 365 should fail
        response = await client.get(
            "/v1/score/0x1111111111111111111111111111111111111111?days=400"
        )
        assert response.status_code == 422
