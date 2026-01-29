"""AgentFICO Data Sources."""
from .x402 import (
    X402DataSource,
    X402MockDataSource,
    X402OnchainDataSource,
    normalize_profitability_score,
)

# Note: ERC8004 imports temporarily commented out due to import path issues
# from .erc8004 import (
#     ERC8004DataSource,
#     ERC8004MockDataSource,
#     ERC8004OnchainDataSource,
# )

__all__ = [
    # x402 Protocol
    "X402DataSource",
    "X402MockDataSource",
    "X402OnchainDataSource",
    "normalize_profitability_score",
    # ERC-8004 (temporarily disabled)
    # "ERC8004DataSource",
    # "ERC8004MockDataSource",
    # "ERC8004OnchainDataSource",
]
