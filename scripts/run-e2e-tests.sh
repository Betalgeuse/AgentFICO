#!/bin/bash

# AgentFICO E2E Test Runner
# 전체 시스템 E2E 테스트 자동화

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "================================================"
echo "AgentFICO E2E Test Suite"
echo "================================================"

# Foundry 경로 추가
export PATH="$HOME/.foundry/bin:$PATH"

# 1. Anvil 시작 (백그라운드)
echo "[1/5] Starting Anvil local node..."
cd "$PROJECT_DIR/contracts"

# 기존 Anvil 프로세스 종료
pkill -f "anvil" 2>/dev/null || true
sleep 1

~/.foundry/bin/anvil --chain-id 31337 --accounts 10 --balance 10000 --port 8545 --host 0.0.0.0 &
ANVIL_PID=$!
sleep 3

# 종료 시 Anvil 정리
cleanup() {
    echo ""
    echo "Cleaning up..."
    kill $ANVIL_PID 2>/dev/null || true
}
trap cleanup EXIT

# 2. 컨트랙트 배포
echo "[2/5] Deploying contracts..."
PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
~/.foundry/bin/forge script script/Deploy.s.sol:DeployAgentFICOScore \
  --rpc-url http://127.0.0.1:8545 \
  --private-key $PRIVATE_KEY \
  --broadcast \
  --quiet

echo "Contract deployed!"

# 3. 환경 변수 설정
export RPC_URL="http://127.0.0.1:8545"
export CONTRACT_ADDRESS="0x5FbDB2315678afecb367f032d93F642f64180aa3"
export OWNER_PRIVATE_KEY="0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# 4. 컨트랙트 테스트 실행
echo "[3/5] Running contract tests..."
cd "$PROJECT_DIR/contracts"
~/.foundry/bin/forge test --summary

# 5. API 단위 테스트 실행
echo "[4/5] Running API unit tests..."
cd "$PROJECT_DIR/api"
python3 -m pytest tests/test_score_calculator.py tests/test_backtest.py -v --tb=short -q

# 6. 통합 테스트 실행
echo "[5/5] Running integration tests..."
python3 -m pytest tests/integration/ -v --tb=short

echo ""
echo "================================================"
echo "✅ All E2E tests passed!"
echo "================================================"
