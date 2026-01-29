"""Dependency injection for API endpoints."""

import os
from functools import lru_cache

from dotenv import load_dotenv

from .calculator.score_calculator import ScoreCalculator
from .data_sources.erc8004 import ERC8004MockDataSource
from .data_sources.etherscan import EtherscanClient
from .data_sources.x402 import X402MockDataSource

# Load .env files (check multiple locations)
load_dotenv()
load_dotenv(".env.local", override=True)
load_dotenv("../contracts/.env", override=True)  # contracts/.env has BASESCAN_API_KEY


@lru_cache
def get_etherscan_client() -> EtherscanClient:
    """Get Etherscan client singleton."""
    # V2 API uses same key for all chains (Etherscan, Basescan, etc.)
    api_key = os.getenv("ETHERSCAN_API_KEY") or os.getenv("BASESCAN_API_KEY", "")
    chain = os.getenv("ETHERSCAN_CHAIN", "ethereum")
    return EtherscanClient(api_key, chain=chain)


@lru_cache
def get_x402_source() -> X402MockDataSource:
    """Get x402 data source (currently mock)."""
    return X402MockDataSource()


@lru_cache
def get_erc8004_source() -> ERC8004MockDataSource:
    """Get ERC-8004 data source (currently mock)."""
    return ERC8004MockDataSource()


@lru_cache
def get_score_calculator() -> ScoreCalculator:
    """Get score calculator singleton."""
    return ScoreCalculator(
        etherscan_client=get_etherscan_client(),
        x402_source=get_x402_source(),
        erc8004_source=get_erc8004_source(),
    )
