# AgentFICO

> **AI 에이전트를 위한 신용 평가 인프라** - FICO for AI Agents

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Base Sepolia](https://img.shields.io/badge/Network-Base%20Sepolia-blue)](https://sepolia.basescan.org/address/0xdF7699A597662330E553C0f48CEb16ace8b339C6)
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-green)](https://agentfico.luerre.ai)

<p align="center">
  <img src="./img.png" alt="AgentFICO Trust Engine" width="600">
</p>

## Overview

AgentFICO는 AI 에이전트의 **신뢰도를 측정하고 온체인에 저장**하는 인프라입니다. 마치 FICO가 개인의 신용 점수를 평가하듯, AgentFICO는 에이전트의 온체인 활동을 분석하여 신뢰 점수를 산출합니다.

### Continuous Growth Flywheel

1. **Trusted Marketplace & Adoption** - 높은 FICO 점수를 가진 에이전트가 플랫폼 신뢰도를 높임
2. **New Agent Entry & Monetization** - 새로운 에이전트들이 진입하고 가스비/수수료로 수익 창출
3. **Data Enrichment & Model Training** - 더 많은 데이터로 점수 정확도 향상

## Live Demo

| 서비스 | URL | 상태 |
|--------|-----|------|
| **Dashboard** | [agentfico.luerre.ai](https://agentfico.luerre.ai) | ✅ Live |
| **Contract** | [0xdF7699...c6](https://sepolia.basescan.org/address/0xdF7699A597662330E553C0f48CEb16ace8b339C6) | ✅ Verified |
| **Webhook** | [agentfico-webhook.onrender.com](https://agentfico-webhook.onrender.com) | ✅ Live |

## Quick Start

### Score Calculation

```bash
# 에이전트 점수 조회
curl http://localhost:8000/v1/score/0x742d35Cc6634C0532925a3b844Bc9e7595f0Ab3d
```

**Response:**
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0Ab3d",
  "score": {
    "overall": 721,
    "txSuccess": 85,
    "x402Profitability": 0,
    "erc8004Stability": 0
  },
  "riskLevel": "LOW",
  "antiGamingApplied": true
}
```

### On-Chain Query

```bash
# Foundry cast로 점수 조회
cast call 0xdF7699A597662330E553C0f48CEb16ace8b339C6 \
  "getScoreOnly(address)(uint256)" \
  0x742d35Cc6634C0532925a3b844Bc9e7595f0Ab3d \
  --rpc-url https://sepolia.base.org
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AgentFICO Ecosystem                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  Dashboard  │    │   API       │    │  Contract   │          │
│  │  (Vercel)   │───▶│  (FastAPI)  │───▶│  (Base)     │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                            │                   │                 │
│                            ▼                   ▼                 │
│                     ┌─────────────┐    ┌─────────────┐          │
│                     │  Etherscan  │    │  Telegram   │          │
│                     │  API        │    │  Webhook    │          │
│                     └─────────────┘    └─────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Repositories

| Repo | 역할 | 링크 |
|------|------|------|
| **AgentFICO** | 점수 계산 인프라 (이 레포) | [GitHub](https://github.com/Betalgeuse/AgentFICO) |
| **AgentFICO-Agents** | 점수 활용 에이전트들 | [GitHub](https://github.com/Betalgeuse/AgentFICO-Agents) |
| **AgentFICO-Config** | Anti-Gaming 계수 (Private) | Private |

## Score Formula

```
Overall Score = (txSuccess × 0.4 + x402Profitability × 0.4 + erc8004Stability × 0.2) × 10
```

| 요소 | 가중치 | 설명 |
|------|--------|------|
| **txSuccess** | 40% | 트랜잭션 성공률 |
| **x402Profitability** | 40% | x402 프로토콜 수익률 |
| **erc8004Stability** | 20% | ERC-8004 등록 안정성 |

### Risk Levels

| 점수 | 레벨 | 설명 |
|------|------|------|
| 800+ | 🟢 VERY_LOW | 매우 신뢰할 수 있음 |
| 700-799 | 🟢 LOW | 신뢰할 수 있음 |
| 600-699 | 🟡 MEDIUM | 주의 필요 |
| 500-599 | 🟠 HIGH | 위험 |
| <500 | 🔴 VERY_HIGH | 매우 위험 |

## Smart Contract

**Network:** Base Sepolia  
**Proxy:** `0xdF7699A597662330E553C0f48CEb16ace8b339C6`  
**Pattern:** UUPS Upgradeable

### Key Functions

```solidity
// 점수 조회
function getScore(address agent) external returns (AgentScore memory)
function getScoreOnly(address agent) external returns (uint256)

// 리스크 평가
function assessRisk(address agent) external view returns (uint8)

// 점수 업데이트 요청 (유료, 1시간 쿨다운)
function requestScoreUpdate() external payable
```

### Events

```solidity
event ScoreUpdated(address indexed agent, uint256 overall, uint8 riskLevel, ...);
event ScoreQueried(address indexed agent, address indexed queriedBy, uint256 overall);
```

## Project Structure

```
AgentFICO/
├── api/                    # Python FastAPI 서버
│   ├── src/
│   │   ├── data_sources/   # Etherscan, x402, ERC-8004
│   │   ├── services/       # Score Calculator, Contract Client
│   │   └── routers/        # API 엔드포인트
│   └── requirements.txt
│
├── contracts/              # Solidity (Foundry)
│   ├── src/
│   │   └── AgentFICOScoreV2.sol
│   ├── script/             # 배포 스크립트
│   └── test/               # 100개 테스트
│
├── frontend/               # React + Vite + TailwindCSS
│
├── webhook/                # Telegram 알림 서비스
│
└── docs/
    ├── ARCHITECTURE_DIAGRAM.md
    ├── DEPLOYMENT_STATUS.md
    └── adr/                # Architecture Decision Records
```

## Development

### Prerequisites

- Python 3.9+
- Node.js 18+
- [Foundry](https://getfoundry.sh/)

### API Server

```bash
cd api
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### Smart Contracts

```bash
cd contracts
forge build
forge test
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Anti-Gaming System

AgentFICO는 점수 조작을 방지하기 위한 Anti-Gaming 시스템을 갖추고 있습니다.

| 모듈 | 기능 |
|------|------|
| **Time Decay** | 최근 활동에 더 높은 가중치 |
| **Anomaly Detection** | 비정상 패턴 탐지 및 페널티 |
| **Consistency Bonus** | 꾸준한 활동에 보너스 |
| **TX Quality** | 트랜잭션 품질 평가 |

계수는 Private Repository에서 관리되어 게이밍을 방지합니다.

## Protocol Support

| 프로토콜 | 용도 | 상태 |
|----------|------|------|
| **ERC-8004** | 온체인 에이전트 ID | ✅ |
| **x402** | Agent-to-Agent 결제 | ⚠️ Planned |
| **A2A** | Agent-to-Agent 통신 | ⚠️ Planned |

## Related Projects

- [AgentFICO-Agents](https://github.com/Betalgeuse/AgentFICO-Agents) - 점수 활용 에이전트들
- [Lucid Agents](https://github.com/daydreamsai/lucid-agents) - 에이전트 프레임워크

## License

MIT License - see [LICENSE](./LICENSE)

---

<p align="center">
  Built with ❤️ for the AI Agent Ecosystem
</p>
