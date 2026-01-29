#!/bin/bash

# AgentFICO Local Deployment Script
# Deploys AgentFICOScore.sol to Anvil local node

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTRACTS_DIR="$(dirname "$SCRIPT_DIR")"

cd "$CONTRACTS_DIR"

# Anvil default account (Account #0)
# 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
export PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
RPC_URL="http://127.0.0.1:8545"

echo "========================================"
echo "AgentFICO Local Deployment"
echo "========================================"
echo "Network: Anvil (Chain ID: 31337)"
echo "RPC URL: $RPC_URL"
echo ""

# Check if Anvil is running
if ! curl -s -X POST --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' -H "Content-Type: application/json" $RPC_URL > /dev/null 2>&1; then
    echo "Error: Anvil is not running at $RPC_URL"
    echo "Please start Anvil first: ./scripts/start-anvil.sh"
    exit 1
fi

echo "Anvil is running. Deploying AgentFICOScore..."
echo ""

# Deploy using forge script
forge script script/Deploy.s.sol:DeployAgentFICOScore \
  --rpc-url $RPC_URL \
  --broadcast \
  -vvv

echo ""
echo "========================================"
echo "Deployment complete!"
echo "========================================"
echo "Check broadcast/ directory for deployment details"
