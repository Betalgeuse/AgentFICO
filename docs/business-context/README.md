# AgentFICO

> **AI 에이전트를 위한 신용점수 인프라**

---

## Quick Summary

| Item | Value |
|------|-------|
| **Validation Score** | 96/100 ✅ PASS |
| **One-liner** | ERC-8004 기반 AI 에이전트 신용점수 API |
| **ACV** | $6,250 (Phase 1) → $15K (Phase 2) |
| **TAM** | $12B+ (2026) |
| **GTM** | Product-Led Sales |
| **$1M ARR Timeline** | M12 |

---

## Documents

| Step | Document | Status |
|------|----------|--------|
| 1 | [ICP Analysis](./agent-trust-infrastructure-icp-analysis.md) | ✅ |
| 1.5 | [GTM Strategy](./agent-trust-infrastructure-gtm-strategy.md) | ✅ |
| 2 | [MVP Spec](./agent-trust-infrastructure-mvp-spec.md) | ✅ |
| 2.5 | [Unit Economics](./agent-trust-infrastructure-unit-economics.md) | ✅ |
| 3 | [Validation](./agent-trust-infrastructure-validation.md) | ✅ |
| Final | [Summary](./agent-trust-infrastructure-summary.md) | ✅ |

---

## Key Resources

### ERC-8004 Agent Scaffolding Tool
- **Repository**: https://github.com/Eversmile12/create-8004-agent
- **NPM Package**: `npx create-8004-agent`
- **Description**: CLI tool to scaffold ERC-8004 compliant AI agents with A2A, MCP, and x402 payment support
- **Key Features**:
  - On-chain agent registration as NFTs (Identity Registry)
  - Reputation Registry for trust signals
  - Validation Registry with stake-secured verification
  - A2A (Agent-to-Agent) protocol server
  - MCP (Model Context Protocol) server
  - x402 USDC micropayments (Base, Polygon)
- **Supported Chains**: ETH Sepolia, Base, Polygon, Monad, Solana Devnet
- **Identity Registry (ETH Sepolia)**: `0x8004A818BFB912233c491871b3d84c89A494BD9e`
- **Use Case**: AgentFICO 에이전트 온보딩 및 등록 프로세스에 활용 가능
- **Related Links**:
  - [ERC-8004 Specification](https://eips.ethereum.org/EIPS/eip-8004)
  - [8004scan Explorer](https://www.8004scan.io/)
  - [A2A Protocol](https://a2a-protocol.org/)
  - [x402 Protocol](https://x402.org/)

---

## Next Steps

1. ERC-8004 커뮤니티 진입
2. 2주 MVP 개발 시작
3. 베타 테스터 모집
4. **create-8004-agent** 패키지 활용하여 에이전트 등록 flow 구현

---

*Pipeline: biz-idea-b2b v2.0 | Date: 2026-01-28*
