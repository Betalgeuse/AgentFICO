"""Backtest framework for AgentFICO score validation.

This module provides tools to validate the scoring formula
using sample agent data with various performance profiles.
"""

from .backtest_runner import BacktestRunner, BacktestResult, BacktestSummary
from .sample_agents import SAMPLE_AGENTS

__all__ = [
    "BacktestRunner",
    "BacktestResult",
    "BacktestSummary",
    "SAMPLE_AGENTS",
]
