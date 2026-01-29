"""Tests for AgentFICO Score Calculator."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from src.calculator.score_calculator import (
    AgentFICOScore,
    RiskLevel,
    ScoreCalculator,
)


class TestRiskLevel:
    """Tests for RiskLevel enum."""

    def test_risk_level_values(self):
        """Verify risk level integer values."""
        assert RiskLevel.EXCELLENT == 1
        assert RiskLevel.GOOD == 2
        assert RiskLevel.AVERAGE == 3
        assert RiskLevel.BELOW_AVERAGE == 4
        assert RiskLevel.POOR == 5

    def test_risk_level_names(self):
        """Verify risk level names."""
        assert RiskLevel.EXCELLENT.name == "EXCELLENT"
        assert RiskLevel.POOR.name == "POOR"


class TestAgentFICOScore:
    """Tests for AgentFICOScore dataclass."""

    def test_score_creation(self):
        """Test basic score creation."""
        score = AgentFICOScore(
            agent_address="0x1234567890abcdef1234567890abcdef12345678",
            overall=780,
            tx_success=80,
            x402_profitability=70,
            erc8004_stability=90,
            risk_level=RiskLevel.GOOD,
            confidence=75,
            timestamp=datetime(2026, 1, 29, 12, 0, 0, tzinfo=timezone.utc),
        )

        assert score.overall == 780
        assert score.risk_level == RiskLevel.GOOD
        assert score.confidence == 75

    def test_to_dict(self):
        """Test dictionary conversion for API response."""
        timestamp = datetime(2026, 1, 29, 12, 0, 0, tzinfo=timezone.utc)
        score = AgentFICOScore(
            agent_address="0x1234567890abcdef1234567890abcdef12345678",
            overall=780,
            tx_success=80,
            x402_profitability=70,
            erc8004_stability=90,
            risk_level=RiskLevel.GOOD,
            confidence=75,
            timestamp=timestamp,
            breakdown={"test": "data"},
        )

        result = score.to_dict()

        assert result["agentAddress"] == "0x1234567890abcdef1234567890abcdef12345678"
        assert result["overall"] == 780
        assert result["txSuccess"] == 80
        assert result["x402Profitability"] == 70
        assert result["erc8004Stability"] == 90
        assert result["riskLevel"] == 2
        assert result["riskLevelName"] == "good"
        assert result["confidence"] == 75
        assert result["timestamp"] == "2026-01-29T12:00:00+00:00"
        assert result["breakdown"] == {"test": "data"}


class TestScoreCalculatorWeights:
    """Tests for weight validation."""

    def test_default_weights(self):
        """Verify default weights sum to 1.0."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        total = sum(calculator.weights.values())
        assert abs(total - 1.0) < 0.001
        assert calculator.weights["tx_success"] == 0.40
        assert calculator.weights["x402_profitability"] == 0.40
        assert calculator.weights["erc8004_stability"] == 0.20

    def test_custom_weights_valid(self):
        """Test custom weights that sum to 1.0."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        custom_weights = {
            "tx_success": 0.50,
            "x402_profitability": 0.30,
            "erc8004_stability": 0.20,
        }

        calculator = ScoreCalculator(
            mock_etherscan, mock_x402, mock_erc8004, weights=custom_weights
        )

        assert calculator.weights["tx_success"] == 0.50
        assert calculator.weights["x402_profitability"] == 0.30

    def test_weights_sum_validation_error(self):
        """Weights that don't sum to 1.0 should raise ValueError."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        invalid_weights = {
            "tx_success": 0.50,
            "x402_profitability": 0.50,
            "erc8004_stability": 0.50,  # Sum = 1.5
        }

        with pytest.raises(ValueError) as exc_info:
            ScoreCalculator(
                mock_etherscan, mock_x402, mock_erc8004, weights=invalid_weights
            )

        assert "Weights must sum to 1.0" in str(exc_info.value)
        assert "1.5" in str(exc_info.value)


class TestScoreCalculation:
    """Tests for score calculation logic."""

    @pytest.fixture
    def calculator(self):
        """Create a calculator with mock data sources."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        return ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

    def test_overall_calculation_basic(self, calculator):
        """Test 40-40-20 weighted average calculation."""
        # tx=80, x402=70, erc8004=90
        # (80*0.4 + 70*0.4 + 90*0.2) * 10 = (32+28+18) * 10 = 780
        result = calculator.calculate_score_sync(80, 70, 90)
        assert result == 780

    def test_overall_calculation_equal_scores(self, calculator):
        """Test with all equal scores."""
        # All 75: (75*0.4 + 75*0.4 + 75*0.2) * 10 = 75 * 10 = 750
        result = calculator.calculate_score_sync(75, 75, 75)
        assert result == 750

    def test_overall_calculation_max_scores(self, calculator):
        """Test with maximum scores."""
        # All 100: (100*0.4 + 100*0.4 + 100*0.2) * 10 = 100 * 10 = 1000
        result = calculator.calculate_score_sync(100, 100, 100)
        assert result == 1000

    def test_overall_calculation_min_scores(self, calculator):
        """Test with minimum scores."""
        # All 0: 0
        result = calculator.calculate_score_sync(0, 0, 0)
        assert result == 0

    def test_overall_calculation_weighted_difference(self, calculator):
        """Test that weights affect the result correctly."""
        # High tx (40%), low x402 (40%), medium erc8004 (20%)
        # (100*0.4 + 0*0.4 + 50*0.2) * 10 = (40+0+10) * 10 = 500
        result = calculator.calculate_score_sync(100, 0, 50)
        assert result == 500

    def test_edge_case_boundary_scores(self, calculator):
        """Test boundary values."""
        # tx=85, x402=85, erc8004=85 → 850 (EXCELLENT boundary)
        result = calculator.calculate_score_sync(85, 85, 85)
        assert result == 850

        # tx=75, x402=75, erc8004=75 → 750 (GOOD boundary)
        result = calculator.calculate_score_sync(75, 75, 75)
        assert result == 750


class TestRiskLevelCalculation:
    """Tests for risk level determination."""

    @pytest.fixture
    def calculator(self):
        """Create a calculator with mock data sources."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        return ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

    def test_risk_level_excellent(self, calculator):
        """850+ = EXCELLENT (risk level 1)."""
        # 90*0.4 + 90*0.4 + 90*0.2 = 90 → 900
        score = calculator.calculate_score_sync(90, 90, 90)
        assert score == 900
        assert score >= 850

        risk = calculator.get_risk_level_for_score(score)
        assert risk == RiskLevel.EXCELLENT

    def test_risk_level_excellent_boundary(self, calculator):
        """Test exact 850 boundary."""
        risk = calculator.get_risk_level_for_score(850)
        assert risk == RiskLevel.EXCELLENT

    def test_risk_level_good(self, calculator):
        """750-849 = GOOD (risk level 2)."""
        risk = calculator.get_risk_level_for_score(800)
        assert risk == RiskLevel.GOOD

        risk = calculator.get_risk_level_for_score(750)
        assert risk == RiskLevel.GOOD

        risk = calculator.get_risk_level_for_score(849)
        assert risk == RiskLevel.GOOD

    def test_risk_level_average(self, calculator):
        """650-749 = AVERAGE (risk level 3)."""
        risk = calculator.get_risk_level_for_score(700)
        assert risk == RiskLevel.AVERAGE

        risk = calculator.get_risk_level_for_score(650)
        assert risk == RiskLevel.AVERAGE

        risk = calculator.get_risk_level_for_score(749)
        assert risk == RiskLevel.AVERAGE

    def test_risk_level_below_average(self, calculator):
        """550-649 = BELOW_AVERAGE (risk level 4)."""
        risk = calculator.get_risk_level_for_score(600)
        assert risk == RiskLevel.BELOW_AVERAGE

        risk = calculator.get_risk_level_for_score(550)
        assert risk == RiskLevel.BELOW_AVERAGE

        risk = calculator.get_risk_level_for_score(649)
        assert risk == RiskLevel.BELOW_AVERAGE

    def test_risk_level_poor(self, calculator):
        """<550 = POOR (risk level 5)."""
        # 40*0.4 + 40*0.4 + 40*0.2 = 40 → 400
        score = calculator.calculate_score_sync(40, 40, 40)
        assert score == 400
        assert score < 550

        risk = calculator.get_risk_level_for_score(score)
        assert risk == RiskLevel.POOR

    def test_risk_level_poor_boundary(self, calculator):
        """Test 549 boundary."""
        risk = calculator.get_risk_level_for_score(549)
        assert risk == RiskLevel.POOR

    def test_risk_level_zero(self, calculator):
        """Test zero score."""
        risk = calculator.get_risk_level_for_score(0)
        assert risk == RiskLevel.POOR


class TestConfidenceCalculation:
    """Tests for confidence score calculation."""

    @pytest.fixture
    def calculator(self):
        """Create a calculator with mock data sources."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        return ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

    def test_confidence_base(self, calculator):
        """Base confidence is 50."""
        confidence = calculator._calculate_confidence(
            {"total_txs": 0},
            {},
            {"is_registered": False},
        )
        assert confidence == 50

    def test_confidence_with_transactions(self, calculator):
        """Transaction count affects confidence."""
        # 10+ transactions = +10
        confidence = calculator._calculate_confidence(
            {"total_txs": 10},
            {},
            {"is_registered": False},
        )
        assert confidence == 60

        # 50+ transactions = +20
        confidence = calculator._calculate_confidence(
            {"total_txs": 50},
            {},
            {"is_registered": False},
        )
        assert confidence == 70

        # 100+ transactions = +30
        confidence = calculator._calculate_confidence(
            {"total_txs": 100},
            {},
            {"is_registered": False},
        )
        assert confidence == 80

    def test_confidence_with_registration(self, calculator):
        """Registration adds +20 confidence."""
        confidence = calculator._calculate_confidence(
            {"total_txs": 0},
            {},
            {"is_registered": True},
        )
        assert confidence == 70  # 50 base + 20 registration

    def test_confidence_max(self, calculator):
        """Confidence is capped at 100."""
        # 50 base + 30 (100+ txs) + 20 (registered) = 100
        confidence = calculator._calculate_confidence(
            {"total_txs": 100},
            {},
            {"is_registered": True},
        )
        assert confidence == 100

    def test_confidence_max_capped(self, calculator):
        """Confidence should not exceed 100."""
        # Even with more transactions, confidence is capped
        confidence = calculator._calculate_confidence(
            {"total_txs": 1000},
            {},
            {"is_registered": True},
        )
        assert confidence == 100


class TestAsyncCalculation:
    """Tests for async score calculation."""

    @pytest.fixture
    def mock_data_sources(self):
        """Create mock data sources with async methods."""
        mock_etherscan = MagicMock()
        mock_etherscan.get_agent_tx_success_score = AsyncMock(
            return_value={
                "address": "0x1234",
                "score": 85,
                "total_txs": 50,
                "success_rate": 94.5,
            }
        )

        mock_x402 = MagicMock()
        mock_x402.calculate_profitability = AsyncMock(
            return_value={
                "address": "0x1234",
                "score": 75,
                "roi_percent": 50.0,
            }
        )

        mock_erc8004 = MagicMock()
        mock_erc8004.calculate_stability_score = AsyncMock(
            return_value={
                "address": "0x1234",
                "score": 80,
                "is_registered": True,
            }
        )

        return mock_etherscan, mock_x402, mock_erc8004

    @pytest.mark.asyncio
    async def test_calculate_score_integration(self, mock_data_sources):
        """Test full async score calculation."""
        mock_etherscan, mock_x402, mock_erc8004 = mock_data_sources

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        score = await calculator.calculate_score("0x1234567890abcdef")

        # Verify calculations
        # (85*0.4 + 75*0.4 + 80*0.2) * 10 = (34 + 30 + 16) * 10 = 800
        assert score.overall == 800
        assert score.tx_success == 85
        assert score.x402_profitability == 75
        assert score.erc8004_stability == 80
        assert score.risk_level == RiskLevel.GOOD
        assert score.confidence == 90  # 50 + 20 (50 txs) + 20 (registered)

    @pytest.mark.asyncio
    async def test_calculate_score_with_breakdown(self, mock_data_sources):
        """Test that breakdown is included in result."""
        mock_etherscan, mock_x402, mock_erc8004 = mock_data_sources

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        score = await calculator.calculate_score("0x1234")

        assert score.breakdown is not None
        assert "weights" in score.breakdown
        assert "sources" in score.breakdown
        assert score.breakdown["weights"]["tx_success"] == 0.40

    @pytest.mark.asyncio
    async def test_calculate_score_with_custom_days(self, mock_data_sources):
        """Test score calculation with custom analysis period."""
        mock_etherscan, mock_x402, mock_erc8004 = mock_data_sources

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        await calculator.calculate_score("0x1234", days=60)

        # Verify days parameter was passed
        mock_etherscan.get_agent_tx_success_score.assert_called_once_with(
            "0x1234", 60
        )
        mock_x402.calculate_profitability.assert_called_once_with("0x1234", 60)

    @pytest.mark.asyncio
    async def test_calculate_score_timestamp(self, mock_data_sources):
        """Test that timestamp is set correctly."""
        mock_etherscan, mock_x402, mock_erc8004 = mock_data_sources

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        before = datetime.now(timezone.utc)
        score = await calculator.calculate_score("0x1234")
        after = datetime.now(timezone.utc)

        assert before <= score.timestamp <= after


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_score_results(self):
        """Test handling of empty/missing score data."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        # When score key is missing, should default to 0
        mock_etherscan.get_agent_tx_success_score = AsyncMock(return_value={})
        mock_x402.calculate_profitability = AsyncMock(return_value={})
        mock_erc8004.calculate_stability_score = AsyncMock(return_value={})

    def test_weights_precision(self):
        """Test weights with floating point precision."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        # Weights that should sum to 1.0 but might have floating point issues
        weights = {
            "tx_success": 0.33,
            "x402_profitability": 0.33,
            "erc8004_stability": 0.34,
        }

        # Should not raise error (within tolerance)
        calculator = ScoreCalculator(
            mock_etherscan, mock_x402, mock_erc8004, weights=weights
        )
        assert calculator is not None

    def test_integer_truncation(self):
        """Test that score is properly truncated to integer."""
        mock_etherscan = MagicMock()
        mock_x402 = MagicMock()
        mock_erc8004 = MagicMock()

        calculator = ScoreCalculator(mock_etherscan, mock_x402, mock_erc8004)

        # 77*0.4 + 77*0.4 + 77*0.2 = 77 → 770
        result = calculator.calculate_score_sync(77, 77, 77)
        assert isinstance(result, int)
        assert result == 770

        # 33*0.4 + 33*0.4 + 33*0.2 = 33 → 330
        result = calculator.calculate_score_sync(33, 33, 33)
        assert result == 330
