"""Tests for Etherscan API client."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.data_sources.etherscan import (
    EtherscanAPIError,
    EtherscanClient,
    EtherscanRateLimitError,
)
from src.models.transaction import Transaction, TransactionStatus


class TestTransaction:
    """Tests for Transaction model."""

    def test_transaction_creation(self):
        """Test basic transaction creation."""
        tx = Transaction(
            hash="0xABC123",
            from_address="0xSender",
            to_address="0xReceiver",
            value=1000000000000000000,  # 1 ETH
            gas_used=21000,
            gas_price=20000000000,  # 20 Gwei
            status=TransactionStatus.SUCCESS,
            timestamp=1706536800,
            block_number=19000000,
        )

        # Check addresses are lowercased
        assert tx.hash == "0xabc123"
        assert tx.from_address == "0xsender"
        assert tx.to_address == "0xreceiver"

    def test_transaction_gas_cost(self):
        """Test gas cost calculations."""
        tx = Transaction(
            hash="0x123",
            from_address="0xsender",
            to_address="0xreceiver",
            value=0,
            gas_used=21000,
            gas_price=20000000000,  # 20 Gwei
            status=TransactionStatus.SUCCESS,
            timestamp=1706536800,
            block_number=19000000,
        )

        assert tx.gas_cost_wei == 21000 * 20000000000
        assert tx.gas_cost_gwei == 420000.0  # 21000 * 20 Gwei

    def test_transaction_value_eth(self):
        """Test ETH value conversion."""
        tx = Transaction(
            hash="0x123",
            from_address="0xsender",
            to_address="0xreceiver",
            value=1500000000000000000,  # 1.5 ETH
            gas_used=21000,
            gas_price=20000000000,
            status=TransactionStatus.SUCCESS,
            timestamp=1706536800,
            block_number=19000000,
        )

        assert tx.value_eth == 1.5

    def test_is_contract_interaction(self):
        """Test contract interaction detection."""
        # Simple transfer (no method ID)
        simple_tx = Transaction(
            hash="0x123",
            from_address="0xsender",
            to_address="0xreceiver",
            value=1000000000000000000,
            gas_used=21000,
            gas_price=20000000000,
            status=TransactionStatus.SUCCESS,
            timestamp=1706536800,
            block_number=19000000,
            method_id=None,
        )
        assert not simple_tx.is_contract_interaction()

        # Contract call with method ID
        contract_tx = Transaction(
            hash="0x456",
            from_address="0xsender",
            to_address="0xcontract",
            value=0,
            gas_used=100000,
            gas_price=20000000000,
            status=TransactionStatus.SUCCESS,
            timestamp=1706536800,
            block_number=19000000,
            method_id="0xa9059cbb",  # ERC20 transfer
        )
        assert contract_tx.is_contract_interaction()


class TestEtherscanClientRateLimiting:
    """Tests for rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limit_allows_burst(self):
        """Test that rate limiter allows 5 calls instantly."""
        client = EtherscanClient(api_key="test_key")

        start_time = time.monotonic()

        # Make 5 calls (should all be immediate)
        for _ in range(5):
            await client._rate_limit()

        elapsed = time.monotonic() - start_time

        # All 5 calls should complete in under 0.1 seconds
        assert elapsed < 0.1

    @pytest.mark.asyncio
    async def test_rate_limit_delays_after_burst(self):
        """Test that rate limiter delays after 5 calls."""
        client = EtherscanClient(api_key="test_key")

        # Make 5 calls first
        for _ in range(5):
            await client._rate_limit()

        start_time = time.monotonic()

        # 6th call should wait
        await client._rate_limit()

        elapsed = time.monotonic() - start_time

        # Should have waited approximately 1 second
        assert elapsed >= 0.9


class TestEtherscanClientTransactionParsing:
    """Tests for transaction parsing."""

    def test_parse_normal_transaction_success(self):
        """Test parsing successful normal transaction."""
        client = EtherscanClient(api_key="test_key")

        tx_data = {
            "hash": "0xabc123",
            "from": "0xSender",
            "to": "0xReceiver",
            "value": "1000000000000000000",
            "gasUsed": "21000",
            "gasPrice": "20000000000",
            "timeStamp": "1706536800",
            "blockNumber": "19000000",
            "txreceipt_status": "1",
            "input": "0x",
        }

        tx = client._parse_transaction(tx_data)

        assert tx.status == TransactionStatus.SUCCESS
        assert tx.value == 1000000000000000000
        assert tx.gas_used == 21000
        assert tx.method_id is None

    def test_parse_normal_transaction_failed(self):
        """Test parsing failed normal transaction."""
        client = EtherscanClient(api_key="test_key")

        tx_data = {
            "hash": "0xfailed",
            "from": "0xSender",
            "to": "0xReceiver",
            "value": "0",
            "gasUsed": "50000",
            "gasPrice": "20000000000",
            "timeStamp": "1706536800",
            "blockNumber": "19000000",
            "txreceipt_status": "0",
            "input": "0xa9059cbb",
        }

        tx = client._parse_transaction(tx_data)

        assert tx.status == TransactionStatus.FAILED

    def test_parse_internal_transaction_success(self):
        """Test parsing successful internal transaction."""
        client = EtherscanClient(api_key="test_key")

        tx_data = {
            "hash": "0xinternal",
            "from": "0xContract",
            "to": "0xReceiver",
            "value": "500000000000000000",
            "gasUsed": "30000",
            "gasPrice": "20000000000",
            "timeStamp": "1706536800",
            "blockNumber": "19000000",
            "isError": "0",
            "input": "0x",
        }

        tx = client._parse_transaction(tx_data, is_internal=True)

        assert tx.status == TransactionStatus.SUCCESS

    def test_parse_internal_transaction_failed(self):
        """Test parsing failed internal transaction."""
        client = EtherscanClient(api_key="test_key")

        tx_data = {
            "hash": "0xfailedinternal",
            "from": "0xContract",
            "to": "0xReceiver",
            "value": "0",
            "gasUsed": "30000",
            "gasPrice": "20000000000",
            "timeStamp": "1706536800",
            "blockNumber": "19000000",
            "isError": "1",
            "input": "0x",
        }

        tx = client._parse_transaction(tx_data, is_internal=True)

        assert tx.status == TransactionStatus.FAILED

    def test_parse_transaction_with_method_id(self):
        """Test parsing transaction with contract method ID."""
        client = EtherscanClient(api_key="test_key")

        tx_data = {
            "hash": "0xcontract",
            "from": "0xSender",
            "to": "0xContract",
            "value": "0",
            "gasUsed": "100000",
            "gasPrice": "20000000000",
            "timeStamp": "1706536800",
            "blockNumber": "19000000",
            "txreceipt_status": "1",
            "input": "0xa9059cbb000000000000000000000000receiver",
        }

        tx = client._parse_transaction(tx_data)

        assert tx.method_id == "0xa9059cbb"
        assert tx.is_contract_interaction()


class TestEtherscanClientSuccessRate:
    """Tests for success rate calculation."""

    def test_calculate_success_rate_all_success(self):
        """Test success rate with all successful transactions."""
        client = EtherscanClient(api_key="test_key")

        transactions = [
            Transaction(
                hash=f"0x{i}",
                from_address="0xsender",
                to_address="0xreceiver",
                value=0,
                gas_used=21000,
                gas_price=20000000000,
                status=TransactionStatus.SUCCESS,
                timestamp=1706536800,
                block_number=19000000,
            )
            for i in range(10)
        ]

        rate = client.calculate_success_rate(transactions)
        assert rate == 100.0

    def test_calculate_success_rate_mixed(self):
        """Test success rate with mixed transactions."""
        client = EtherscanClient(api_key="test_key")

        transactions = []
        # 8 successful
        for i in range(8):
            transactions.append(
                Transaction(
                    hash=f"0xsuccess{i}",
                    from_address="0xsender",
                    to_address="0xreceiver",
                    value=0,
                    gas_used=21000,
                    gas_price=20000000000,
                    status=TransactionStatus.SUCCESS,
                    timestamp=1706536800,
                    block_number=19000000,
                )
            )
        # 2 failed
        for i in range(2):
            transactions.append(
                Transaction(
                    hash=f"0xfailed{i}",
                    from_address="0xsender",
                    to_address="0xreceiver",
                    value=0,
                    gas_used=21000,
                    gas_price=20000000000,
                    status=TransactionStatus.FAILED,
                    timestamp=1706536800,
                    block_number=19000000,
                )
            )

        rate = client.calculate_success_rate(transactions)
        assert rate == 80.0

    def test_calculate_success_rate_empty(self):
        """Test success rate with no transactions."""
        client = EtherscanClient(api_key="test_key")
        rate = client.calculate_success_rate([])
        assert rate == 0.0

    def test_calculate_success_rate_ignores_pending(self):
        """Test that pending transactions are excluded from calculation."""
        client = EtherscanClient(api_key="test_key")

        transactions = [
            Transaction(
                hash="0xsuccess",
                from_address="0xsender",
                to_address="0xreceiver",
                value=0,
                gas_used=21000,
                gas_price=20000000000,
                status=TransactionStatus.SUCCESS,
                timestamp=1706536800,
                block_number=19000000,
            ),
            Transaction(
                hash="0xpending",
                from_address="0xsender",
                to_address="0xreceiver",
                value=0,
                gas_used=0,
                gas_price=20000000000,
                status=TransactionStatus.PENDING,
                timestamp=1706536800,
                block_number=19000000,
            ),
        ]

        rate = client.calculate_success_rate(transactions)
        # Only 1 completed transaction (success), so 100%
        assert rate == 100.0


class TestEtherscanClientScoreNormalization:
    """Tests for score normalization."""

    def test_normalize_score_perfect(self):
        """Test score normalization for perfect success rate."""
        client = EtherscanClient(api_key="test_key")
        assert client._normalize_score(100.0) == 100

    def test_normalize_score_high(self):
        """Test score normalization for high success rate."""
        client = EtherscanClient(api_key="test_key")
        assert client._normalize_score(99.0) == 100
        assert client._normalize_score(95.0) == 95
        assert client._normalize_score(97.0) == 97

    def test_normalize_score_medium(self):
        """Test score normalization for medium success rate."""
        client = EtherscanClient(api_key="test_key")
        assert client._normalize_score(90.0) == 85
        assert client._normalize_score(80.0) == 65

    def test_normalize_score_low(self):
        """Test score normalization for low success rate."""
        client = EtherscanClient(api_key="test_key")
        assert client._normalize_score(50.0) == 30
        assert client._normalize_score(0.0) == 0


class TestEtherscanClientAPIRequests:
    """Tests for API request handling."""

    @pytest.mark.asyncio
    async def test_get_transactions_success(self):
        """Test successful transaction fetch."""
        client = EtherscanClient(api_key="test_key")

        mock_response = {
            "status": "1",
            "message": "OK",
            "result": [
                {
                    "hash": "0xtest",
                    "from": "0xsender",
                    "to": "0xreceiver",
                    "value": "1000000000000000000",
                    "gasUsed": "21000",
                    "gasPrice": "20000000000",
                    "timeStamp": "1706536800",
                    "blockNumber": "19000000",
                    "txreceipt_status": "1",
                    "input": "0x",
                }
            ],
        }

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_response

            transactions = await client.get_transactions("0xtest_address")

            assert len(transactions) == 1
            assert transactions[0].hash == "0xtest"
            assert transactions[0].status == TransactionStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_get_transactions_no_results(self):
        """Test transaction fetch with no results."""
        client = EtherscanClient(api_key="test_key")

        mock_response = {"status": "1", "message": "OK", "result": []}

        with patch.object(client, "_make_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_response

            transactions = await client.get_transactions("0xnew_address")

            assert len(transactions) == 0

    @pytest.mark.asyncio
    async def test_get_agent_tx_success_score(self):
        """Test full score calculation flow."""
        client = EtherscanClient(api_key="test_key")

        # Mock transactions: 9 success, 1 failed = 90%
        mock_txs = []
        for i in range(9):
            mock_txs.append(
                Transaction(
                    hash=f"0xsuccess{i}",
                    from_address="0xsender",
                    to_address="0xreceiver",
                    value=0,
                    gas_used=21000,
                    gas_price=20000000000,
                    status=TransactionStatus.SUCCESS,
                    timestamp=int(time.time()) - 100,  # Recent
                    block_number=19000000,
                )
            )
        mock_txs.append(
            Transaction(
                hash="0xfailed",
                from_address="0xsender",
                to_address="0xreceiver",
                value=0,
                gas_used=21000,
                gas_price=20000000000,
                status=TransactionStatus.FAILED,
                timestamp=int(time.time()) - 100,  # Recent
                block_number=19000000,
            )
        )

        with patch.object(
            client, "get_all_transactions", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_txs

            result = await client.get_agent_tx_success_score("0xtest_agent")

            assert result["total_txs"] == 10
            assert result["successful_txs"] == 9
            assert result["failed_txs"] == 1
            assert result["success_rate"] == 90.0
            assert result["score"] == 85  # 90% maps to 85 in normalization
            assert result["period_days"] == 30
            assert "analyzed_at" in result


class TestEtherscanClientErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test handling of API errors."""
        client = EtherscanClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "0",
            "message": "NOTOK",
            "result": "Invalid API Key",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(EtherscanAPIError) as exc_info:
                await client._make_request({"module": "account", "action": "txlist"})

            assert "Invalid API Key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Test handling of rate limit errors from API."""
        client = EtherscanClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "0",
            "message": "NOTOK",
            "result": "Max rate limit reached",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(EtherscanRateLimitError):
                await client._make_request({"module": "account", "action": "txlist"})

    @pytest.mark.asyncio
    async def test_no_transactions_found_not_error(self):
        """Test that 'No transactions found' is handled gracefully."""
        client = EtherscanClient(api_key="test_key")

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "0",
            "message": "No transactions found",
            "result": "No transactions found",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.get.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client._make_request(
                {"module": "account", "action": "txlist"}
            )

            assert result["result"] == []
