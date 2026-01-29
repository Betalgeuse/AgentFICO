"""AgentFICO Score Calculator Engine.

This module provides the core scoring logic for AgentFICO, integrating
three data sources to calculate a comprehensive agent credit score:
- txSuccess (Etherscan): Transaction success rate
- x402Profitability: Payment profitability metrics
- erc8004Stability: Registry stability score

The default weighting is:
- txSuccess: 40%
- x402Profitability: 40%
- erc8004Stability: 20%
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import IntEnum
from typing import Optional
import logging

from ..data_sources.etherscan import EtherscanClient
from ..data_sources.x402 import X402DataSource
from ..data_sources.erc8004 import ERC8004DataSource

# Anti-Gaming imports (optional, graceful fallback if not available)
try:
    from ..services.anti_gaming import (
        apply_time_decay,
        detect_anomaly,
        calculate_consistency_bonus,
        assess_transaction_quality,
        is_feature_enabled,
    )
    ANTI_GAMING_AVAILABLE = True
except ImportError:
    ANTI_GAMING_AVAILABLE = False

logger = logging.getLogger(__name__)


class RiskLevel(IntEnum):
    """Risk level classification (1: lowest risk ~ 5: highest risk).

    Risk levels are determined by the overall AgentFICO score:
    - EXCELLENT (1): 850+ - Very low risk, highly reliable agent
    - GOOD (2): 750-849 - Low risk, reliable agent
    - AVERAGE (3): 650-749 - Moderate risk, average reliability
    - BELOW_AVERAGE (4): 550-649 - Higher risk, below average reliability
    - POOR (5): <550 - High risk, unreliable agent
    """

    EXCELLENT = 1  # 850+
    GOOD = 2  # 750-849
    AVERAGE = 3  # 650-749
    BELOW_AVERAGE = 4  # 550-649
    POOR = 5  # <550


@dataclass
class AgentFICOScore:
    """AgentFICO score result containing all scoring components.

    Attributes:
        agent_address: Ethereum address of the agent
        overall: Overall score (0-1000)
        tx_success: Transaction success score (0-100)
        x402_profitability: Payment profitability score (0-100)
        erc8004_stability: Registry stability score (0-100)
        risk_level: Risk classification (1-5)
        confidence: Confidence in the score (0-100)
        timestamp: When the score was calculated
        breakdown: Optional detailed breakdown of score components
    """

    agent_address: str
    overall: int  # 0-1000
    tx_success: int  # 0-100
    x402_profitability: int  # 0-100
    erc8004_stability: int  # 0-100
    risk_level: RiskLevel
    confidence: int  # 0-100
    timestamp: datetime

    # Optional detailed information
    breakdown: Optional[dict] = None

    def to_dict(self) -> dict:
        """Convert score to dictionary for JSON serialization.

        Returns:
            Dictionary representation with camelCase keys for API response.
        """
        return {
            "agentAddress": self.agent_address,
            "overall": self.overall,
            "txSuccess": self.tx_success,
            "x402Profitability": self.x402_profitability,
            "erc8004Stability": self.erc8004_stability,
            "riskLevel": self.risk_level.value,
            "riskLevelName": self.risk_level.name.lower(),
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "breakdown": self.breakdown,
        }


class ScoreCalculator:
    """AgentFICO Score Calculator Engine.

    Calculates the overall AgentFICO score by combining three data sources
    with configurable weights. The default weights are:
    - txSuccess: 40%
    - x402Profitability: 40%
    - erc8004Stability: 20%

    The overall score ranges from 0-1000, derived from weighted averages
    of individual component scores (0-100 each).

    Example:
        >>> calculator = ScoreCalculator(etherscan, x402, erc8004)
        >>> score = await calculator.calculate_score("0x123...")
        >>> print(f"Overall: {score.overall}, Risk: {score.risk_level.name}")
    """

    # Default weights (can be adjusted after validation)
    DEFAULT_WEIGHTS = {
        "tx_success": 0.40,
        "x402_profitability": 0.40,
        "erc8004_stability": 0.20,
    }

    def __init__(
        self,
        etherscan_client: EtherscanClient,
        x402_source: X402DataSource,
        erc8004_source: ERC8004DataSource,
        weights: Optional[dict] = None,
    ):
        """Initialize the score calculator.

        Args:
            etherscan_client: Etherscan API client for transaction data
            x402_source: x402 data source for profitability metrics
            erc8004_source: ERC-8004 data source for stability score
            weights: Optional custom weights (must sum to 1.0)

        Raises:
            ValueError: If weights do not sum to 1.0
        """
        self.etherscan = etherscan_client
        self.x402 = x402_source
        self.erc8004 = erc8004_source
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()

        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    async def calculate_score(
        self,
        agent_address: str,
        days: int = 30,
    ) -> AgentFICOScore:
        """Calculate the AgentFICO score for an agent.

        Fetches data from all three sources and calculates weighted
        average to produce the overall score.

        Args:
            agent_address: Ethereum address of the agent (0x...)
            days: Analysis period in days (default: 30)

        Returns:
            AgentFICOScore object with all score components
        """
        # 1. Collect scores from each data source
        tx_result = await self.etherscan.get_agent_tx_success_score(
            agent_address, days
        )
        x402_result = await self.x402.calculate_profitability(agent_address, days)
        erc8004_result = await self.erc8004.calculate_stability_score(agent_address)

        # 2. Extract individual scores (0-100)
        tx_score = tx_result.get("score", 0)
        x402_score = x402_result.get("score", 0)
        erc8004_score = erc8004_result.get("score", 0)

        # 3. Calculate weighted average → overall (0-1000)
        weighted_sum = (
            tx_score * self.weights["tx_success"]
            + x402_score * self.weights["x402_profitability"]
            + erc8004_score * self.weights["erc8004_stability"]
        )
        overall = int(weighted_sum * 10)  # 0-100 → 0-1000

        # 3.5 Apply Anti-Gaming adjustments (if available)
        anti_gaming_adjustments = {}
        if ANTI_GAMING_AVAILABLE:
            overall, anti_gaming_adjustments = await self._apply_anti_gaming(
                agent_address,
                overall,
                tx_result,
            )

        # 4. Determine risk level
        risk_level = self._calculate_risk_level(overall)

        # 5. Calculate confidence
        confidence = self._calculate_confidence(tx_result, x402_result, erc8004_result)

        # 6. Build result
        return AgentFICOScore(
            agent_address=agent_address,
            overall=overall,
            tx_success=tx_score,
            x402_profitability=x402_score,
            erc8004_stability=erc8004_score,
            risk_level=risk_level,
            confidence=confidence,
            timestamp=datetime.now(timezone.utc),
            breakdown={
                "weights": self.weights,
                "sources": {
                    "txSuccess": tx_result,
                    "x402Profitability": x402_result,
                    "erc8004Stability": erc8004_result,
                },
            },
        )

    def _calculate_risk_level(self, overall: int) -> RiskLevel:
        """Determine risk level based on overall score.

        Args:
            overall: Overall score (0-1000)

        Returns:
            RiskLevel enum value
        """
        if overall >= 850:
            return RiskLevel.EXCELLENT
        elif overall >= 750:
            return RiskLevel.GOOD
        elif overall >= 650:
            return RiskLevel.AVERAGE
        elif overall >= 550:
            return RiskLevel.BELOW_AVERAGE
        else:
            return RiskLevel.POOR

    def _calculate_confidence(
        self,
        tx_result: dict,
        x402_result: dict,
        erc8004_result: dict,
    ) -> int:
        """Calculate confidence score based on data quality.

        Confidence factors:
        - Transaction count: More transactions = higher confidence (up to +30)
        - Registration status: Registered agent = +20
        - Base confidence: 50

        Args:
            tx_result: Transaction success result
            x402_result: Profitability result
            erc8004_result: Stability result

        Returns:
            Confidence score (0-100)
        """
        confidence = 50  # Base confidence

        # Transaction count factor (+30 max)
        tx_count = tx_result.get("total_txs", 0)
        if tx_count >= 100:
            confidence += 30
        elif tx_count >= 50:
            confidence += 20
        elif tx_count >= 10:
            confidence += 10

        # Registration status (+20)
        if erc8004_result.get("is_registered", False):
            confidence += 20

        return min(confidence, 100)

    def calculate_score_sync(
        self,
        tx_score: int,
        x402_score: int,
        erc8004_score: int,
    ) -> int:
        """Calculate overall score synchronously (for testing/simulation).

        This method calculates only the weighted average without
        fetching data from sources, useful for testing and simulation.

        Args:
            tx_score: Transaction success score (0-100)
            x402_score: Profitability score (0-100)
            erc8004_score: Stability score (0-100)

        Returns:
            Overall score (0-1000)
        """
        weighted_sum = (
            tx_score * self.weights["tx_success"]
            + x402_score * self.weights["x402_profitability"]
            + erc8004_score * self.weights["erc8004_stability"]
        )
        return int(weighted_sum * 10)

    def get_risk_level_for_score(self, overall: int) -> RiskLevel:
        """Get risk level for a given overall score.

        Public method to access risk level calculation.

        Args:
            overall: Overall score (0-1000)

        Returns:
            RiskLevel enum value
        """
        return self._calculate_risk_level(overall)

    async def _apply_anti_gaming(
        self,
        agent_address: str,
        base_score: int,
        tx_result: dict,
    ) -> tuple[int, dict]:
        """Apply Anti-Gaming adjustments to the base score.

        This method applies various anti-gaming measures:
        - Time decay: Recent activity weighted higher
        - Anomaly detection: Flag suspicious behavior
        - Consistency bonus: Reward long-term good performance
        - TX quality: Weight transactions by quality

        Args:
            agent_address: Agent's Ethereum address
            base_score: Base score before adjustments
            tx_result: Transaction data from Etherscan

        Returns:
            Tuple of (adjusted_score, adjustment_details)
        """
        if not ANTI_GAMING_AVAILABLE:
            return base_score, {}

        adjustments = {
            "base_score": base_score,
            "applied": [],
        }
        adjusted_score = float(base_score)

        try:
            # 1. Anomaly Detection (can reduce score)
            if is_feature_enabled("anomaly"):
                # For now, use simplified metrics
                current_metrics = {
                    "tx_count": tx_result.get("total_txs", 0),
                    "success_rate": tx_result.get("success_rate", 0),
                }
                # Historical would come from DB in production
                historical_metrics = []
                
                anomaly_result = detect_anomaly(
                    agent_address,
                    current_metrics,
                    historical_metrics
                )
                
                if anomaly_result.get("is_anomaly"):
                    penalty_factor = anomaly_result.get("penalty_factor", 1.0)
                    adjusted_score *= penalty_factor
                    adjustments["applied"].append({
                        "type": "anomaly_penalty",
                        "factor": penalty_factor,
                        "flags": anomaly_result.get("flags", [])
                    })

            # 2. Consistency Bonus (can increase score)
            if is_feature_enabled("consistency"):
                # Historical performance would come from DB
                performance_history = []
                
                consistency_result = calculate_consistency_bonus(performance_history)
                bonus = consistency_result.get("bonus_points", 0)
                
                if bonus > 0:
                    adjusted_score += bonus
                    adjustments["applied"].append({
                        "type": "consistency_bonus",
                        "bonus": bonus,
                        "tier": consistency_result.get("achieved_tier")
                    })

            # Ensure score stays in valid range
            final_score = int(max(0, min(1000, adjusted_score)))
            adjustments["final_score"] = final_score
            adjustments["total_adjustment"] = final_score - base_score

            logger.debug(
                f"Anti-gaming applied for {agent_address}: "
                f"{base_score} -> {final_score}"
            )

            return final_score, adjustments

        except Exception as e:
            logger.warning(f"Anti-gaming adjustment failed: {e}")
            return base_score, {"error": str(e)}
