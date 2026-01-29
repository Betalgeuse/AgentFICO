"""Dependency injection for API endpoints."""

import os
from functools import lru_cache

from dotenv import load_dotenv

from .calculator.score_calculator import ScoreCalculator
from .data_sources.etherscan import EtherscanClient
from .data_sources.x402_nodata import X402NoDataSource
from .data_sources.erc8004_nodata import ERC8004NoDataSource

# Load .env files (check multiple locations)
import pathlib
_api_dir = pathlib.Path(__file__).parent.parent
_root_dir = _api_dir.parent

load_dotenv()
load_dotenv(_api_dir / ".env.local", override=True)
load_dotenv(_root_dir / "contracts" / ".env", override=True)  # contracts/.env has BASESCAN_API_KEY


@lru_cache
def get_etherscan_client() -> EtherscanClient:
    """Get Etherscan client singleton."""
    # V2 API uses same key for all chains (Etherscan, Basescan, etc.)
    api_key = os.getenv("ETHERSCAN_API_KEY") or os.getenv("BASESCAN_API_KEY", "")
    chain = os.getenv("ETHERSCAN_CHAIN", "ethereum")
    return EtherscanClient(api_key, chain=chain)


@lru_cache
def get_x402_source() -> X402NoDataSource:
    """Get x402 data source.
    
    Returns NoData source - x402 protocol not yet finalized.
    Will return real data once protocol is available.
    """
    return X402NoDataSource()


@lru_cache
def get_erc8004_source() -> ERC8004NoDataSource:
    """Get ERC-8004 data source.
    
    Returns NoData source - ERC-8004 registry not widely available.
    Will return real data once registry is deployed and agents register.
    """
    return ERC8004NoDataSource()


@lru_cache
def get_score_calculator() -> ScoreCalculator:
    """Get score calculator singleton.
    
    Current scoring:
    - txSuccess: Real data from Etherscan (40%)
    - x402Profitability: 0 (no data) - will be added when protocol is ready
    - erc8004Stability: 0 (no data) - will be added when agents register
    
    Effective score = txSuccess only until other data sources are available.
    """
    return ScoreCalculator(
        etherscan_client=get_etherscan_client(),
        x402_source=get_x402_source(),
        erc8004_source=get_erc8004_source(),
    )
