"""
Tests for x402 Protocol Data Source

Tests mock data source functionality, profitability calculation,
and score normalization.
"""

import pytest
from datetime import datetime, timedelta

from src.data_sources.x402 import (
    X402MockDataSource,
    X402OnchainDataSource,
    normalize_profitability_score,
)
from src.models.payment import X402Payment, PaymentType


class TestNormalizeProfitabilityScore:
    """Tests for the normalize_profitability_score function"""
    
    def test_roi_above_100_returns_100(self):
        """ROI >= 100% should return max score of 100"""
        assert normalize_profitability_score(100) == 100
        assert normalize_profitability_score(150) == 100
        assert normalize_profitability_score(200) == 100
    
    def test_roi_75_returns_87(self):
        """ROI 75% should return score of ~87 (midpoint of 75-100 range)"""
        # 50% -> 75, 100% -> 100
        # 75% is midpoint, so should be ~87.5
        score = normalize_profitability_score(75)
        assert score == 87  # 75 + (75-50)*0.5 = 87.5 -> 87
    
    def test_roi_50_returns_75(self):
        """ROI 50% should return score of 75"""
        assert normalize_profitability_score(50) == 75
    
    def test_roi_25_returns_62(self):
        """ROI 25% should return score of ~62"""
        score = normalize_profitability_score(25)
        assert score == 62  # 50 + 25*0.5 = 62.5 -> 62
    
    def test_roi_0_returns_50(self):
        """ROI 0% should return score of 50"""
        assert normalize_profitability_score(0) == 50
    
    def test_roi_negative_25_returns_37(self):
        """ROI -25% should return score of ~37"""
        score = normalize_profitability_score(-25)
        assert score == 37  # 25 + (-25+50)*0.5 = 37.5 -> 37
    
    def test_roi_negative_50_returns_25(self):
        """ROI -50% should return score of 25"""
        assert normalize_profitability_score(-50) == 25
    
    def test_roi_negative_75_returns_12(self):
        """ROI -75% should return score of ~12"""
        score = normalize_profitability_score(-75)
        assert score == 12  # 25 + (-75+50)*0.5 = 12.5 -> 12
    
    def test_roi_negative_100_or_less_returns_0(self):
        """ROI -100% or less should return 0"""
        assert normalize_profitability_score(-100) == 0
        assert normalize_profitability_score(-150) == 0


class TestX402Payment:
    """Tests for the X402Payment model"""
    
    def test_payment_is_income(self):
        """Test is_income() returns True for incoming payments"""
        payment = X402Payment(
            tx_hash="0x123",
            agent_address="0xagent",
            counterparty="0xcounter",
            amount_usdc=100.0,
            payment_type=PaymentType.INCOMING,
            timestamp=datetime.now()
        )
        assert payment.is_income() is True
        assert payment.is_expense() is False
    
    def test_payment_is_expense(self):
        """Test is_expense() returns True for outgoing payments"""
        payment = X402Payment(
            tx_hash="0x123",
            agent_address="0xagent",
            counterparty="0xcounter",
            amount_usdc=50.0,
            payment_type=PaymentType.OUTGOING,
            timestamp=datetime.now()
        )
        assert payment.is_expense() is True
        assert payment.is_income() is False
    
    def test_payment_service_type_optional(self):
        """Test service_type is optional"""
        payment = X402Payment(
            tx_hash="0x123",
            agent_address="0xagent",
            counterparty="0xcounter",
            amount_usdc=100.0,
            payment_type=PaymentType.INCOMING,
            timestamp=datetime.now()
        )
        assert payment.service_type is None
        
        payment_with_service = X402Payment(
            tx_hash="0x456",
            agent_address="0xagent",
            counterparty="0xcounter",
            amount_usdc=100.0,
            payment_type=PaymentType.INCOMING,
            timestamp=datetime.now(),
            service_type="api_call"
        )
        assert payment_with_service.service_type == "api_call"


class TestX402MockDataSource:
    """Tests for the X402MockDataSource"""
    
    @pytest.mark.asyncio
    async def test_mock_profitability_returns_valid_structure(self):
        """Test that calculate_profitability returns expected keys"""
        source = X402MockDataSource(seed=42)
        result = await source.calculate_profitability("0x123abc456def789", days=30)
        
        assert "address" in result
        assert "total_income" in result
        assert "total_expense" in result
        assert "net_profit" in result
        assert "roi_percent" in result
        assert "score" in result
        assert "transaction_count" in result
        assert "period_days" in result
    
    @pytest.mark.asyncio
    async def test_mock_profitability_score_in_range(self):
        """Test that score is within 0-100 range"""
        source = X402MockDataSource(seed=42)
        result = await source.calculate_profitability("0x123abc456def789", days=30)
        
        assert "score" in result
        assert 0 <= result["score"] <= 100
    
    @pytest.mark.asyncio
    async def test_mock_profitability_consistent_results(self):
        """Test that same address produces same results (deterministic)"""
        source = X402MockDataSource(seed=42)
        address = "0xabcdef1234567890abcdef1234567890abcdef12"
        
        result1 = await source.calculate_profitability(address, days=30)
        result2 = await source.calculate_profitability(address, days=30)
        
        assert result1["score"] == result2["score"]
        assert result1["total_income"] == result2["total_income"]
        assert result1["total_expense"] == result2["total_expense"]
        assert result1["transaction_count"] == result2["transaction_count"]
    
    @pytest.mark.asyncio
    async def test_mock_profitability_different_addresses_different_results(self):
        """Test that different addresses produce different results"""
        source = X402MockDataSource(seed=42)
        
        result1 = await source.calculate_profitability("0x1111111111111111111111111111111111111111", days=30)
        result2 = await source.calculate_profitability("0x2222222222222222222222222222222222222222", days=30)
        
        # Different addresses should have different scores/transactions
        # (highly unlikely to be exactly the same)
        assert (
            result1["score"] != result2["score"] or
            result1["total_income"] != result2["total_income"] or
            result1["transaction_count"] != result2["transaction_count"]
        )
    
    @pytest.mark.asyncio
    async def test_mock_get_payments_returns_list(self):
        """Test that get_payments returns a list of payments"""
        source = X402MockDataSource(seed=42)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        payments = await source.get_payments(
            "0xabcdef1234567890abcdef1234567890abcdef12",
            start_date,
            end_date
        )
        
        assert isinstance(payments, list)
        assert len(payments) > 0
        assert all(isinstance(p, X402Payment) for p in payments)
    
    @pytest.mark.asyncio
    async def test_mock_get_payments_sorted_by_timestamp(self):
        """Test that payments are sorted by timestamp"""
        source = X402MockDataSource(seed=42)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        payments = await source.get_payments(
            "0xabcdef1234567890abcdef1234567890abcdef12",
            start_date,
            end_date
        )
        
        for i in range(len(payments) - 1):
            assert payments[i].timestamp <= payments[i + 1].timestamp
    
    @pytest.mark.asyncio
    async def test_mock_get_payments_empty_range(self):
        """Test that empty date range returns empty list"""
        source = X402MockDataSource(seed=42)
        now = datetime.utcnow()
        
        payments = await source.get_payments(
            "0xabcdef1234567890abcdef1234567890abcdef12",
            now,
            now - timedelta(days=1)  # end before start
        )
        
        assert payments == []
    
    @pytest.mark.asyncio
    async def test_mock_profitability_net_profit_calculation(self):
        """Test that net_profit equals income minus expense"""
        source = X402MockDataSource(seed=42)
        result = await source.calculate_profitability("0xabcdef1234567890", days=30)
        
        expected_net_profit = result["total_income"] - result["total_expense"]
        assert abs(result["net_profit"] - expected_net_profit) < 0.01
    
    @pytest.mark.asyncio
    async def test_mock_profitability_period_days_matches_input(self):
        """Test that period_days in result matches input days"""
        source = X402MockDataSource(seed=42)
        
        result_30 = await source.calculate_profitability("0xtest", days=30)
        assert result_30["period_days"] == 30
        
        result_7 = await source.calculate_profitability("0xtest", days=7)
        assert result_7["period_days"] == 7


class TestX402OnchainDataSource:
    """Tests for the X402OnchainDataSource placeholder"""
    
    @pytest.mark.asyncio
    async def test_onchain_get_payments_raises_not_implemented(self):
        """Test that get_payments raises NotImplementedError"""
        source = X402OnchainDataSource(
            rpc_url="https://mainnet.infura.io/v3/xxx",
            contract_address="0xcontract"
        )
        
        with pytest.raises(NotImplementedError):
            await source.get_payments(
                "0xagent",
                datetime.now() - timedelta(days=30),
                datetime.now()
            )
    
    @pytest.mark.asyncio
    async def test_onchain_calculate_profitability_raises_not_implemented(self):
        """Test that calculate_profitability raises NotImplementedError"""
        source = X402OnchainDataSource(
            rpc_url="https://mainnet.infura.io/v3/xxx",
            contract_address="0xcontract"
        )
        
        with pytest.raises(NotImplementedError):
            await source.calculate_profitability("0xagent", days=30)
