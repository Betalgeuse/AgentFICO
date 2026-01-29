"""AgentFICO Data Sources."""
from .x402 import (
    X402DataSource,
    X402MockDataSource,
    X402OnchainDataSource,
    normalize_profitability_score,
)
from .x402_nodata import X402NoDataSource

from .erc8004 import (
    ERC8004DataSource,
    ERC8004MockDataSource,
    ERC8004OnchainDataSource,
)
from .erc8004_nodata import ERC8004NoDataSource

__all__ = [
    # x402 Protocol
    "X402DataSource",
    "X402MockDataSource",
    "X402OnchainDataSource",
    "X402NoDataSource",
    "normalize_profitability_score",
    # ERC-8004
    "ERC8004DataSource",
    "ERC8004MockDataSource",
    "ERC8004OnchainDataSource",
    "ERC8004NoDataSource",
]
