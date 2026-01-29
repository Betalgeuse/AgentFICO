"""Etherscan API client for transaction data collection."""

import asyncio
import time
from datetime import datetime, timezone
from typing import List, Optional

import httpx

from ..models.transaction import Transaction, TransactionStatus


class EtherscanError(Exception):
    """Base exception for Etherscan API errors."""

    pass


class EtherscanRateLimitError(EtherscanError):
    """Raised when rate limit is exceeded."""

    pass


class EtherscanAPIError(EtherscanError):
    """Raised when API returns an error."""

    pass


class EtherscanClient:
    """Etherscan API client with rate limiting (5 calls/sec).

    This client provides methods to fetch transaction data from Etherscan
    and calculate success rates for AI agent scoring.

    Attributes:
        BASE_URL: Etherscan API base URL
        RATE_LIMIT: Maximum calls per second (5 for free tier)
        RATE_WINDOW: Time window for rate limiting in seconds

    Example:
        >>> client = EtherscanClient(api_key="YOUR_API_KEY")
        >>> score = await client.get_agent_tx_success_score("0x123...")
        >>> print(f"Success rate: {score['success_rate']:.2f}%")
    """

    BASE_URL = "https://api.etherscan.io/api"
    RATE_LIMIT = 5  # calls per second
    RATE_WINDOW = 1.0  # seconds

    def __init__(self, api_key: str, timeout: float = 30.0):
        """Initialize Etherscan client.

        Args:
            api_key: Etherscan API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.timeout = timeout
        self._last_call_times: List[float] = []
        self._lock = asyncio.Lock()

    async def _rate_limit(self) -> None:
        """Enforce rate limiting using sliding window.

        Ensures no more than RATE_LIMIT calls are made within RATE_WINDOW seconds.
        Automatically waits if limit would be exceeded.
        """
        async with self._lock:
            current_time = time.monotonic()

            # Remove timestamps outside the sliding window
            self._last_call_times = [
                t
                for t in self._last_call_times
                if current_time - t < self.RATE_WINDOW
            ]

            # If at limit, wait until oldest call expires
            if len(self._last_call_times) >= self.RATE_LIMIT:
                oldest_call = min(self._last_call_times)
                wait_time = self.RATE_WINDOW - (current_time - oldest_call)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    # Recalculate after sleep
                    current_time = time.monotonic()
                    self._last_call_times = [
                        t
                        for t in self._last_call_times
                        if current_time - t < self.RATE_WINDOW
                    ]

            # Record this call
            self._last_call_times.append(time.monotonic())

    async def _make_request(self, params: dict) -> dict:
        """Make an API request with rate limiting.

        Args:
            params: API parameters

        Returns:
            API response data

        Raises:
            EtherscanAPIError: If API returns an error
            EtherscanRateLimitError: If rate limit is exceeded on API side
        """
        await self._rate_limit()

        params["apikey"] = self.api_key

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

        # Handle API errors
        if data.get("status") == "0":
            message = data.get("message", "Unknown error")
            result = data.get("result", "")

            if "rate limit" in message.lower() or "rate limit" in str(result).lower():
                raise EtherscanRateLimitError(f"Rate limit exceeded: {message}")

            # "No transactions found" is not an error
            if "No transactions found" in str(result):
                return {"result": []}

            raise EtherscanAPIError(f"API error: {message} - {result}")

        return data

    def _parse_transaction(self, tx_data: dict, is_internal: bool = False) -> Transaction:
        """Parse raw transaction data into Transaction object.

        Args:
            tx_data: Raw transaction data from API
            is_internal: Whether this is an internal transaction

        Returns:
            Parsed Transaction object
        """
        # Determine status
        if is_internal:
            # Internal transactions: isError field
            is_error = tx_data.get("isError", "0")
            status = TransactionStatus.FAILED if is_error == "1" else TransactionStatus.SUCCESS
        else:
            # Normal transactions: txreceipt_status field
            receipt_status = tx_data.get("txreceipt_status", "")
            if receipt_status == "1":
                status = TransactionStatus.SUCCESS
            elif receipt_status == "0":
                status = TransactionStatus.FAILED
            else:
                # Empty status means pending or pre-Byzantium
                status = TransactionStatus.PENDING

        # Extract method ID from input data
        input_data = tx_data.get("input", "")
        method_id = input_data[:10] if len(input_data) >= 10 else None
        if method_id == "0x":
            method_id = None

        return Transaction(
            hash=tx_data.get("hash", ""),
            from_address=tx_data.get("from", ""),
            to_address=tx_data.get("to", "") or "",
            value=int(tx_data.get("value", "0")),
            gas_used=int(tx_data.get("gasUsed", "0")),
            gas_price=int(tx_data.get("gasPrice", "0")),
            status=status,
            timestamp=int(tx_data.get("timeStamp", "0")),
            block_number=int(tx_data.get("blockNumber", "0")),
            method_id=method_id,
        )

    async def get_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        page: int = 1,
        offset: int = 100,
        sort: str = "desc",
    ) -> List[Transaction]:
        """Fetch normal transactions for an address.

        Args:
            address: Ethereum address (0x...)
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            offset: Number of transactions per page (max 10000)
            sort: Sort order ('asc' or 'desc')

        Returns:
            List of Transaction objects

        Raises:
            EtherscanAPIError: If API returns an error
        """
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": min(offset, 10000),  # API max
            "sort": sort,
        }

        data = await self._make_request(params)
        result = data.get("result", [])

        if not isinstance(result, list):
            return []

        return [self._parse_transaction(tx) for tx in result]

    async def get_internal_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        page: int = 1,
        offset: int = 100,
        sort: str = "desc",
    ) -> List[Transaction]:
        """Fetch internal transactions for an address.

        Internal transactions are created by contract executions.

        Args:
            address: Ethereum address (0x...)
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            offset: Number of transactions per page (max 10000)
            sort: Sort order ('asc' or 'desc')

        Returns:
            List of Transaction objects

        Raises:
            EtherscanAPIError: If API returns an error
        """
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": min(offset, 10000),
            "sort": sort,
        }

        data = await self._make_request(params)
        result = data.get("result", [])

        if not isinstance(result, list):
            return []

        return [self._parse_transaction(tx, is_internal=True) for tx in result]

    async def get_all_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        include_internal: bool = True,
    ) -> List[Transaction]:
        """Fetch all transactions (normal + internal) for an address.

        Args:
            address: Ethereum address (0x...)
            start_block: Starting block number
            end_block: Ending block number
            include_internal: Whether to include internal transactions

        Returns:
            Combined list of Transaction objects, sorted by timestamp
        """
        # Fetch normal transactions
        normal_txs = await self.get_transactions(
            address=address,
            start_block=start_block,
            end_block=end_block,
            offset=10000,
        )

        if not include_internal:
            return normal_txs

        # Fetch internal transactions
        internal_txs = await self.get_internal_transactions(
            address=address,
            start_block=start_block,
            end_block=end_block,
            offset=10000,
        )

        # Combine and sort by timestamp (newest first)
        all_txs = normal_txs + internal_txs
        all_txs.sort(key=lambda tx: tx.timestamp, reverse=True)

        return all_txs

    def calculate_success_rate(self, transactions: List[Transaction]) -> float:
        """Calculate transaction success rate.

        Args:
            transactions: List of Transaction objects

        Returns:
            Success rate as percentage (0-100)
        """
        if not transactions:
            return 0.0

        # Only count non-pending transactions
        completed_txs = [
            tx for tx in transactions if tx.status != TransactionStatus.PENDING
        ]

        if not completed_txs:
            return 0.0

        success_count = sum(
            1 for tx in completed_txs if tx.status == TransactionStatus.SUCCESS
        )

        return (success_count / len(completed_txs)) * 100

    def _normalize_score(self, success_rate: float) -> int:
        """Normalize success rate to a score (0-100).

        Uses a curve that rewards high success rates:
        - 100% success -> 100 score
        - 95% success -> 95 score
        - 90% success -> 85 score
        - Below 80% -> significant penalty

        Args:
            success_rate: Success rate percentage (0-100)

        Returns:
            Normalized score (0-100)
        """
        if success_rate >= 99:
            return 100
        elif success_rate >= 95:
            return int(95 + (success_rate - 95) * 1.0)
        elif success_rate >= 90:
            return int(85 + (success_rate - 90) * 2.0)
        elif success_rate >= 80:
            return int(65 + (success_rate - 80) * 2.0)
        elif success_rate >= 50:
            return int(30 + (success_rate - 50) * 1.17)
        else:
            return int(success_rate * 0.6)

    async def get_agent_tx_success_score(
        self,
        address: str,
        days: int = 30,
        include_internal: bool = True,
    ) -> dict:
        """Calculate agent's txSuccess score.

        Fetches transactions from the last N days and calculates
        success rate and normalized score.

        Args:
            address: Ethereum address (0x...)
            days: Number of days to analyze (default: 30)
            include_internal: Whether to include internal transactions

        Returns:
            Dictionary with score details:
            {
                "address": "0x...",
                "total_txs": 150,
                "successful_txs": 142,
                "failed_txs": 8,
                "pending_txs": 0,
                "success_rate": 94.67,  # 0-100
                "score": 95,  # 0-100 normalized
                "period_days": 30,
                "analyzed_at": "2026-01-29T12:00:00Z"
            }
        """
        # Fetch all transactions
        all_txs = await self.get_all_transactions(
            address=address,
            include_internal=include_internal,
        )

        # Filter by time period
        cutoff_timestamp = int(
            (datetime.now(timezone.utc).timestamp()) - (days * 24 * 60 * 60)
        )
        recent_txs = [tx for tx in all_txs if tx.timestamp >= cutoff_timestamp]

        # Count by status
        successful_txs = sum(
            1 for tx in recent_txs if tx.status == TransactionStatus.SUCCESS
        )
        failed_txs = sum(
            1 for tx in recent_txs if tx.status == TransactionStatus.FAILED
        )
        pending_txs = sum(
            1 for tx in recent_txs if tx.status == TransactionStatus.PENDING
        )

        # Calculate rates
        success_rate = self.calculate_success_rate(recent_txs)
        score = self._normalize_score(success_rate)

        return {
            "address": address.lower(),
            "total_txs": len(recent_txs),
            "successful_txs": successful_txs,
            "failed_txs": failed_txs,
            "pending_txs": pending_txs,
            "success_rate": round(success_rate, 2),
            "score": score,
            "period_days": days,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
