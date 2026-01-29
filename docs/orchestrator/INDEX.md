# AgentFICO - Orchestrator Tasks Index

> **🎯 Mission: AI 에이전트를 위한 신용 점수 인프라**

---

## 🔗 Ecosystem

```
┌─────────────────────────────────────────────────────────────────┐
│                         AgentFICO                                │
│                    (신용 점수 인프라) ← 이 레포                  │
├─────────────────────────────────────────────────────────────────┤
│  • Score Calculation Engine                                      │
│  • AgentFICOScore.sol (Base Sepolia)                            │
│  • REST API + Dashboard                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │ API / Contract
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AgentFICO-Agents                             │
│                   (점수 활용 에이전트)                           │
├─────────────────────────────────────────────────────────────────┤
│  • Portfolio Scout, Risk Monitor                                 │
│  • Strategy Replicator                                           │
│  • 🔄 Feedback Loop → 점수 공식 검증                            │
└─────────────────────────────────────────────────────────────────┘
```

**Related Repo:** [AgentFICO-Agents](../../../../AgentFICO-Agents/docs/orchestrator/INDEX.md)

---

## Milestones

### Phase 1: MVP 기술 검증 ✅

| ID | Title | 상태 | 설명 |
|:---|:---|:---|:---|
| [M1](milestones/M1.md) | Score Calculation | ✅ 완료 | 점수 계산 엔진, 백테스트 통과 |
| [M2](milestones/M2.md) | Local Testing | ✅ 완료 | Anvil 로컬 통합 테스트 (200+) |

### Phase 2: 실제 검증 + 테스트넷 배포 🚀

| ID | Title | 상태 | 진행도 | 설명 |
|:---|:---|:---|:---:|:---|
| [M3](milestones/M3.md) | Real Agent Scoring | ✅ 완료 | 100% | 7개 에이전트 점수 검증 (avg 721) |
| [M4](milestones/M4.md) | Testnet Deploy | 📋 계획 | 67% | Base Sepolia 배포 (M3 검증 완료) |
| [M5](milestones/M5.md) | Feedback API | 📋 계획 | 0% | AgentFICO-Agents 피드백 수신 |

### Phase 3: 사용자 노출 + GTM

| ID | Title | 상태 | 진행도 | 설명 |
|:---|:---|:---|:---:|:---|
| [M6](milestones/M6.md) | Dashboard | ✅ 완료 | 100% | M3 실제 점수 연동 완료 |
| [M7](milestones/M7.md) | GTM Launch | 📋 계획 | 0% | ERC-8004 커뮤니티 론칭 |

### Phase 4: 확장 (TBD)

| ID | Title | 상태 | 설명 |
|:---|:---|:---|:---|
| M8 | DeFi Integration | 📋 계획 | Aave, Uniswap 연동 |
| M9 | Compliance Module | 📋 계획 | 규제 준수 리포트 |

---

## 📊 Current Progress

```
Phase 1 ████████████████████ 100%  ✅ 완료
Phase 2 ████████████░░░░░░░░  56%  🚀 진행 중 ← 현재
Phase 3 ██████████████████░░  90%  ✅ 거의 완료
Phase 4 ░░░░░░░░░░░░░░░░░░░░   0%  📋 계획
```

### ✅ 완료

**M1: Score Calculation Engine**
- ✅ 점수 공식 확정 ([ADR-002](../adr/ADR-002-score-formula.md))
- ✅ 백테스트 통과 (정확도 75%)
- ✅ API로 점수 조회 가능

**M2: Local Testing**
- ✅ Anvil 로컬 노드 + 컨트랙트 배포
- ✅ API ↔ Contract 연동 검증
- ✅ 200+ 테스트 통과

**M3: Real Agent Scoring**
- ✅ 7개 ERC-8004 에이전트 수집 (Sepolia 2, Base Sepolia 5)
- ✅ 점수 계산: avg 721, range 502-812
- ✅ [REAL_AGENT_REPORT.md](../demo/REAL_AGENT_REPORT.md) 생성

**M6: Dashboard**
- ✅ M3 실제 에이전트 점수 연동
- ✅ RealAgentList 컴포넌트 (tier 분포 표시)
- ✅ Vite build 성공 (295KB)

### 🚀 다음 진행

**M4: Testnet Deploy** (67% - M3 완료, 배포 준비)
- ✅ Foundry 세팅, 컨트랙트, 테스트, 배포 스크립트
- ⏳ Base Sepolia 배포
- ⏳ 배포 문서화

---

## 🔄 Feedback Loop

```
AgentFICO                      AgentFICO-Agents
────────────────────────────────────────────────────
1. 점수 API 제공         ────▶  2. 점수 기반 거래
                                      │
4. 공식 조정 (필요시)    ◀────  3. 성과 데이터 수집
```

---

## ADR (Architecture Decision Records)

| ID | Title | Status |
|:---|:---|:---|
| [ADR-001](../adr/ADR-001-backend-first.md) | 백엔드 우선 개발 | ✅ Approved |
| [ADR-002](../adr/ADR-002-score-formula.md) | 점수 공식 확정 | ✅ Approved |

---

## Quick Links

- [AGENTFICO_TECH_SPEC.md](../business-context/specs/AGENTFICO_TECH_SPEC.md) - 기술 명세
- [AGENTFICO_BUSINESS_STRATEGY.md](../business-context/AGENTFICO_BUSINESS_STRATEGY.md) - 비즈니스 전략

---

## Droid Assignment Guide

| Domain | Recommended Droid |
|:---|:---|
| Smart Contract | `web3-smart-contract-auditor` |
| Blockchain Data | `blockchain-data-analyzer` |
| REST API | `web3-api-developer` |
| DeFi Integration | `defi-protocol-specialist` |
| Testing | `hardhat-test-engineer` |
| Frontend | `vite-react-developer` |
| 마일스톤 계획 | `milestone-architect` |
