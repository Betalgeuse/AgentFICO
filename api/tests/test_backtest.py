"""Tests for the backtest framework."""

import pytest

from src.backtest.backtest_runner import BacktestRunner, BacktestResult, BacktestSummary
from src.backtest.sample_agents import (
    SAMPLE_AGENTS,
    get_agents_by_tier,
    create_custom_agent,
)


class TestSampleAgents:
    """Tests for sample_agents module."""

    def test_sample_agents_exist(self):
        """Verify sample agents dictionary is populated."""
        assert len(SAMPLE_AGENTS) >= 5
        assert "excellent_trader" in SAMPLE_AGENTS
        assert "risky_agent" in SAMPLE_AGENTS

    def test_sample_agent_structure(self):
        """Verify each agent has required fields."""
        required_fields = ["address", "description", "expected_tier", "mock_scores"]
        required_scores = ["tx_success", "x402_profitability", "erc8004_stability"]

        for agent_id, agent_data in SAMPLE_AGENTS.items():
            for field in required_fields:
                assert field in agent_data, f"{agent_id} missing field: {field}"

            for score in required_scores:
                assert score in agent_data["mock_scores"], (
                    f"{agent_id} missing score: {score}"
                )

    def test_score_ranges(self):
        """Verify all scores are within valid range (0-100)."""
        for agent_id, agent_data in SAMPLE_AGENTS.items():
            for score_name, score_value in agent_data["mock_scores"].items():
                assert 0 <= score_value <= 100, (
                    f"{agent_id}.{score_name} = {score_value} out of range"
                )

    def test_get_agents_by_tier(self):
        """Test filtering agents by tier."""
        excellent = get_agents_by_tier("EXCELLENT")
        assert len(excellent) >= 1
        for agent_data in excellent.values():
            assert agent_data["expected_tier"] == "EXCELLENT"

        poor = get_agents_by_tier("POOR")
        assert len(poor) >= 1
        for agent_data in poor.values():
            assert agent_data["expected_tier"] == "POOR"

    def test_create_custom_agent(self):
        """Test custom agent creation."""
        agent = create_custom_agent(
            address="0xABCDEF1234567890ABCDEF1234567890ABCDEF12",
            tx_success=90,
            x402_profitability=85,
            erc8004_stability=80,
            description="Test agent",
        )

        assert agent["address"] == "0xABCDEF1234567890ABCDEF1234567890ABCDEF12"
        assert agent["mock_scores"]["tx_success"] == 90
        assert agent["expected_tier"] == "EXCELLENT"  # High scores → EXCELLENT


class TestBacktestRunner:
    """Tests for BacktestRunner class."""

    def test_runner_initialization(self):
        """Test runner initializes with default weights."""
        runner = BacktestRunner()
        assert runner.weights["tx_success"] == 0.40
        assert runner.weights["x402_profitability"] == 0.40
        assert runner.weights["erc8004_stability"] == 0.20

    def test_runner_custom_weights(self):
        """Test runner accepts custom weights."""
        weights = {
            "tx_success": 0.50,
            "x402_profitability": 0.30,
            "erc8004_stability": 0.20,
        }
        runner = BacktestRunner(weights=weights)
        assert runner.weights["tx_success"] == 0.50

    def test_runner_invalid_weights(self):
        """Test runner rejects weights that don't sum to 1.0."""
        weights = {
            "tx_success": 0.50,
            "x402_profitability": 0.50,
            "erc8004_stability": 0.20,
        }
        with pytest.raises(ValueError):
            BacktestRunner(weights=weights)

    def test_run_backtest(self):
        """Test backtest execution."""
        runner = BacktestRunner()
        summary = runner.run_backtest()

        assert summary.total_agents == len(SAMPLE_AGENTS)
        assert 0 <= summary.accuracy <= 1
        assert summary.min_score <= summary.avg_score <= summary.max_score
        assert len(summary.results) == summary.total_agents

    def test_backtest_accuracy(self):
        """Test that backtest achieves minimum accuracy."""
        runner = BacktestRunner()
        summary = runner.run_backtest()

        # 최소 70% 정확도 기대
        assert summary.accuracy >= 0.7, (
            f"Accuracy {summary.accuracy:.1%} below 70% threshold"
        )

    def test_score_distribution_diversity(self):
        """Test that scores are distributed across tiers."""
        runner = BacktestRunner()
        summary = runner.run_backtest()

        # 점수 분포가 다양해야 함 (최소 3개 티어)
        assert len(summary.score_distribution) >= 3, (
            f"Only {len(summary.score_distribution)} tiers represented"
        )

    def test_backtest_result_structure(self):
        """Test BacktestResult has correct attributes."""
        runner = BacktestRunner()
        summary = runner.run_backtest()

        result = summary.results[0]
        assert hasattr(result, "agent_id")
        assert hasattr(result, "address")
        assert hasattr(result, "expected_tier")
        assert hasattr(result, "actual_tier")
        assert hasattr(result, "overall_score")
        assert hasattr(result, "is_correct")

    def test_overall_score_calculation(self):
        """Test that overall score is calculated correctly."""
        runner = BacktestRunner()

        # Test with known values
        scores = {
            "tx_success": 100,
            "x402_profitability": 100,
            "erc8004_stability": 100,
        }
        overall = runner._calculate_overall(scores, runner.weights)
        assert overall == 1000  # Max score

        scores = {
            "tx_success": 0,
            "x402_profitability": 0,
            "erc8004_stability": 0,
        }
        overall = runner._calculate_overall(scores, runner.weights)
        assert overall == 0  # Min score

    def test_tier_assignment(self):
        """Test tier assignment thresholds."""
        runner = BacktestRunner()

        assert runner._get_tier(1000) == "EXCELLENT"
        assert runner._get_tier(850) == "EXCELLENT"
        assert runner._get_tier(849) == "GOOD"
        assert runner._get_tier(750) == "GOOD"
        assert runner._get_tier(749) == "AVERAGE"
        assert runner._get_tier(650) == "AVERAGE"
        assert runner._get_tier(649) == "BELOW_AVERAGE"
        assert runner._get_tier(550) == "BELOW_AVERAGE"
        assert runner._get_tier(549) == "POOR"
        assert runner._get_tier(0) == "POOR"


class TestWeightSensitivity:
    """Tests for weight sensitivity analysis."""

    def test_weight_sensitivity(self):
        """Test weight sensitivity analysis."""
        runner = BacktestRunner()
        result = runner.analyze_weight_sensitivity()

        assert "variations" in result
        assert len(result["variations"]) >= 3
        assert "best_accuracy" in result
        assert "best_weights" in result
        assert "recommendation" in result

    def test_weight_variation_structure(self):
        """Test that each variation has required fields."""
        runner = BacktestRunner()
        result = runner.analyze_weight_sensitivity()

        for var in result["variations"]:
            assert "weights" in var
            assert "accuracy" in var
            assert "avg_score" in var
            assert "distribution" in var

    def test_custom_weight_variations(self):
        """Test with custom weight variations."""
        runner = BacktestRunner()
        custom_variations = [
            {"tx_success": 0.60, "x402_profitability": 0.30, "erc8004_stability": 0.10},
            {"tx_success": 0.20, "x402_profitability": 0.60, "erc8004_stability": 0.20},
        ]
        result = runner.analyze_weight_sensitivity(weight_variations=custom_variations)

        assert len(result["variations"]) == 2


class TestReportGeneration:
    """Tests for report generation."""

    def test_generate_report(self):
        """Test markdown report generation."""
        runner = BacktestRunner()
        report = runner.generate_report()

        assert "# AgentFICO 백테스트 리포트" in report
        assert "## 요약" in report
        assert "## 점수 분포" in report
        assert "## 가중치 민감도 분석" in report
        assert "## 결론" in report

    def test_report_contains_data(self):
        """Test report contains actual data."""
        runner = BacktestRunner()
        report = runner.generate_report()

        # 숫자 포함 확인
        assert "총 에이전트:" in report
        assert "예측 정확도:" in report
        assert "평균 점수:" in report


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_agents(self):
        """Test with empty agent dictionary."""
        runner = BacktestRunner()
        summary = runner.run_backtest(agents={})

        assert summary.total_agents == 0
        assert summary.accuracy == 0
        assert summary.avg_score == 0

    def test_single_agent(self):
        """Test with single agent."""
        runner = BacktestRunner()
        single_agent = {"test": SAMPLE_AGENTS["excellent_trader"]}
        summary = runner.run_backtest(agents=single_agent)

        assert summary.total_agents == 1
        assert summary.score_std == 0  # No std with single value

    def test_extreme_scores(self):
        """Test with extreme score values."""
        runner = BacktestRunner()

        # All max scores
        max_agent = {
            "max": {
                "address": "0x0000000000000000000000000000000000000001",
                "description": "Max scores",
                "expected_tier": "EXCELLENT",
                "mock_scores": {
                    "tx_success": 100,
                    "x402_profitability": 100,
                    "erc8004_stability": 100,
                },
            }
        }
        summary = runner.run_backtest(agents=max_agent)
        assert summary.results[0].overall_score == 1000

        # All min scores
        min_agent = {
            "min": {
                "address": "0x0000000000000000000000000000000000000002",
                "description": "Min scores",
                "expected_tier": "POOR",
                "mock_scores": {
                    "tx_success": 0,
                    "x402_profitability": 0,
                    "erc8004_stability": 0,
                },
            }
        }
        summary = runner.run_backtest(agents=min_agent)
        assert summary.results[0].overall_score == 0


class TestResultSerialization:
    """Tests for result serialization."""

    def test_backtest_result_to_dict(self):
        """Test BacktestResult to_dict method."""
        result = BacktestResult(
            agent_id="test",
            address="0x1234",
            expected_tier="GOOD",
            actual_tier="GOOD",
            overall_score=800,
            tx_success=85,
            x402_profitability=80,
            erc8004_stability=75,
            is_correct=True,
        )
        d = result.to_dict()

        assert d["agent_id"] == "test"
        assert d["overall_score"] == 800
        assert d["is_correct"] is True

    def test_backtest_summary_to_dict(self):
        """Test BacktestSummary to_dict method."""
        runner = BacktestRunner()
        summary = runner.run_backtest()
        d = summary.to_dict()

        assert "total_agents" in d
        assert "accuracy" in d
        assert "results" in d
        assert isinstance(d["results"], list)
