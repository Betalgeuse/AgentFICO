"""Backtest runner for AgentFICO score validation.

This module provides tools to validate the scoring formula by running
backtests against sample agent data and analyzing weight sensitivity.
"""

import statistics
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from .sample_agents import SAMPLE_AGENTS


@dataclass
class BacktestResult:
    """Individual agent backtest result."""

    agent_id: str
    address: str
    expected_tier: str
    actual_tier: str
    overall_score: int
    tx_success: int
    x402_profitability: int
    erc8004_stability: int
    is_correct: bool  # expected == actual

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "agent_id": self.agent_id,
            "address": self.address,
            "expected_tier": self.expected_tier,
            "actual_tier": self.actual_tier,
            "overall_score": self.overall_score,
            "tx_success": self.tx_success,
            "x402_profitability": self.x402_profitability,
            "erc8004_stability": self.erc8004_stability,
            "is_correct": self.is_correct,
        }


@dataclass
class BacktestSummary:
    """Backtest summary statistics."""

    total_agents: int
    correct_predictions: int
    accuracy: float
    score_distribution: Dict[str, int]  # tier별 개수
    avg_score: float
    min_score: int
    max_score: int
    score_std: float
    results: List[BacktestResult] = field(default_factory=list)

    # 가중치 민감도
    weight_analysis: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert summary to dictionary."""
        return {
            "total_agents": self.total_agents,
            "correct_predictions": self.correct_predictions,
            "accuracy": self.accuracy,
            "score_distribution": self.score_distribution,
            "avg_score": self.avg_score,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "score_std": self.score_std,
            "results": [r.to_dict() for r in self.results],
            "weight_analysis": self.weight_analysis,
        }


class BacktestRunner:
    """Score formula backtest runner.

    Validates the AgentFICO scoring formula by running backtests
    against sample agents and analyzing weight sensitivity.

    Example:
        >>> runner = BacktestRunner()
        >>> summary = runner.run_backtest()
        >>> print(f"Accuracy: {summary.accuracy:.1%}")
    """

    # Default weights matching ScoreCalculator
    DEFAULT_WEIGHTS: Dict[str, float] = {
        "tx_success": 0.40,
        "x402_profitability": 0.40,
        "erc8004_stability": 0.20,
    }

    # Tier thresholds (overall score)
    TIER_THRESHOLDS: Dict[str, int] = {
        "EXCELLENT": 850,
        "GOOD": 750,
        "AVERAGE": 650,
        "BELOW_AVERAGE": 550,
        "POOR": 0,
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize the backtest runner.

        Args:
            weights: Optional custom weights (must sum to 1.0)

        Raises:
            ValueError: If weights do not sum to 1.0
        """
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    def run_backtest(
        self,
        agents: Optional[Dict[str, Any]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> BacktestSummary:
        """Run backtest against sample agents.

        Args:
            agents: Agent dictionary (default: SAMPLE_AGENTS)
            weights: Weights to use (default: 40-40-20)

        Returns:
            BacktestSummary with all results
        """
        if agents is None:
            agents = SAMPLE_AGENTS

        if weights is None:
            weights = self.weights

        results: List[BacktestResult] = []
        scores: List[int] = []

        for agent_id, agent_data in agents.items():
            mock_scores = agent_data["mock_scores"]

            # Calculate overall score
            overall = self._calculate_overall(mock_scores, weights)
            actual_tier = self._get_tier(overall)
            expected_tier = agent_data["expected_tier"]

            result = BacktestResult(
                agent_id=agent_id,
                address=agent_data["address"],
                expected_tier=expected_tier,
                actual_tier=actual_tier,
                overall_score=overall,
                tx_success=mock_scores["tx_success"],
                x402_profitability=mock_scores["x402_profitability"],
                erc8004_stability=mock_scores["erc8004_stability"],
                is_correct=(expected_tier == actual_tier),
            )
            results.append(result)
            scores.append(overall)

        # Calculate distribution
        tier_counts = Counter(r.actual_tier for r in results)
        correct_count = sum(1 for r in results if r.is_correct)

        return BacktestSummary(
            total_agents=len(results),
            correct_predictions=correct_count,
            accuracy=correct_count / len(results) if results else 0,
            score_distribution=dict(tier_counts),
            avg_score=statistics.mean(scores) if scores else 0,
            min_score=min(scores) if scores else 0,
            max_score=max(scores) if scores else 0,
            score_std=statistics.stdev(scores) if len(scores) > 1 else 0,
            results=results,
        )

    def analyze_weight_sensitivity(
        self,
        agents: Optional[Dict[str, Any]] = None,
        weight_variations: Optional[List[Dict[str, float]]] = None,
    ) -> Dict[str, Any]:
        """Analyze score changes with different weights.

        Args:
            agents: Agent dictionary
            weight_variations: List of weight configurations to test

        Returns:
            Analysis result with recommendations
        """
        if weight_variations is None:
            weight_variations = [
                # 기본 (40-40-20)
                {
                    "tx_success": 0.40,
                    "x402_profitability": 0.40,
                    "erc8004_stability": 0.20,
                },
                # tx 강조 (50-30-20)
                {
                    "tx_success": 0.50,
                    "x402_profitability": 0.30,
                    "erc8004_stability": 0.20,
                },
                # x402 강조 (30-50-20)
                {
                    "tx_success": 0.30,
                    "x402_profitability": 0.50,
                    "erc8004_stability": 0.20,
                },
                # 균등 (33-33-34)
                {
                    "tx_success": 0.33,
                    "x402_profitability": 0.33,
                    "erc8004_stability": 0.34,
                },
            ]

        results = []
        for weights in weight_variations:
            summary = self.run_backtest(agents, weights)
            results.append(
                {
                    "weights": weights,
                    "accuracy": summary.accuracy,
                    "avg_score": summary.avg_score,
                    "score_std": summary.score_std,
                    "distribution": summary.score_distribution,
                }
            )

        best_result = max(results, key=lambda x: x["accuracy"])

        return {
            "variations": results,
            "best_accuracy": best_result["accuracy"],
            "best_weights": best_result["weights"],
            "recommendation": self._generate_recommendation(results),
        }

    def _calculate_overall(
        self,
        scores: Dict[str, int],
        weights: Dict[str, float],
    ) -> int:
        """Calculate weighted average (0-1000).

        Args:
            scores: Component scores (0-100)
            weights: Weight dictionary

        Returns:
            Overall score (0-1000)
        """
        weighted_sum = (
            scores["tx_success"] * weights["tx_success"]
            + scores["x402_profitability"] * weights["x402_profitability"]
            + scores["erc8004_stability"] * weights["erc8004_stability"]
        )
        return int(weighted_sum * 10)

    def _get_tier(self, score: int) -> str:
        """Convert score to tier.

        Args:
            score: Overall score (0-1000)

        Returns:
            Tier name
        """
        if score >= 850:
            return "EXCELLENT"
        elif score >= 750:
            return "GOOD"
        elif score >= 650:
            return "AVERAGE"
        elif score >= 550:
            return "BELOW_AVERAGE"
        else:
            return "POOR"

    def _generate_recommendation(self, results: List[Dict[str, Any]]) -> str:
        """Generate weight recommendation.

        Args:
            results: List of test results

        Returns:
            Recommendation string
        """
        best = max(results, key=lambda x: x["accuracy"])

        if best["accuracy"] >= 0.8:
            return f"현재 가중치 적합. 정확도: {best['accuracy']:.1%}"
        elif best["accuracy"] >= 0.6:
            w = best["weights"]
            return (
                f"가중치 조정 권장. 최적: "
                f"tx={w['tx_success']:.0%}, "
                f"x402={w['x402_profitability']:.0%}, "
                f"erc8004={w['erc8004_stability']:.0%} "
                f"(정확도: {best['accuracy']:.1%})"
            )
        else:
            return f"가중치 재검토 필요. 최고 정확도: {best['accuracy']:.1%}"

    def generate_report(self) -> str:
        """Generate markdown backtest report.

        Returns:
            Markdown formatted report
        """
        summary = self.run_backtest()
        sensitivity = self.analyze_weight_sensitivity()

        report = f"""# AgentFICO 백테스트 리포트

## 요약
- 총 에이전트: {summary.total_agents}
- 예측 정확도: {summary.accuracy:.1%}
- 평균 점수: {summary.avg_score:.0f}
- 점수 범위: {summary.min_score} - {summary.max_score}
- 표준편차: {summary.score_std:.1f}

## 점수 분포
| Tier | Count |
|------|-------|
{self._format_distribution(summary.score_distribution)}

## 개별 결과
| Agent ID | Expected | Actual | Score | Match |
|----------|----------|--------|-------|-------|
{self._format_results(summary.results)}

## 가중치 민감도 분석
{self._format_sensitivity(sensitivity)}

## 결론
{sensitivity['recommendation']}
"""
        return report

    def _format_distribution(self, dist: Dict[str, int]) -> str:
        """Format tier distribution as markdown table rows."""
        lines = []
        for tier in ["EXCELLENT", "GOOD", "AVERAGE", "BELOW_AVERAGE", "POOR"]:
            count = dist.get(tier, 0)
            lines.append(f"| {tier} | {count} |")
        return "\n".join(lines)

    def _format_results(self, results: List[BacktestResult]) -> str:
        """Format individual results as markdown table rows."""
        lines = []
        for r in results:
            match = "✓" if r.is_correct else "✗"
            lines.append(
                f"| {r.agent_id} | {r.expected_tier} | {r.actual_tier} | "
                f"{r.overall_score} | {match} |"
            )
        return "\n".join(lines)

    def _format_sensitivity(self, sensitivity: Dict[str, Any]) -> str:
        """Format sensitivity analysis as markdown list."""
        lines = []
        for var in sensitivity["variations"]:
            w = var["weights"]
            lines.append(
                f"- tx={w['tx_success']:.0%}, "
                f"x402={w['x402_profitability']:.0%}, "
                f"erc8004={w['erc8004_stability']:.0%} "
                f"→ 정확도 {var['accuracy']:.1%}, 평균 {var['avg_score']:.0f}"
            )
        return "\n".join(lines)
