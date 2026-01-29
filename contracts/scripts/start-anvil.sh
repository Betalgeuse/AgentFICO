#!/bin/bash

# AgentFICO Local Test Node (Anvil)
# Chain ID: 31337
# Instant mining mode (no --block-time flag = mine on tx)

echo "Starting Anvil local node..."
echo "Chain ID: 31337"
echo "RPC URL: http://127.0.0.1:8545"
echo ""

anvil \
  --chain-id 31337 \
  --accounts 10 \
  --balance 10000 \
  --port 8545 \
  --host 0.0.0.0

# Anvil 기본 계정 (테스트용)
# Mnemonic: "test test test test test test test test test test test junk"
# Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
# (Private key displayed by anvil on startup)
