# AgentFICO - Orchestrator Tasks Index

프로젝트 마일스톤 및 이슈 태스크 문서 인덱스입니다.

## Milestones

### 실행 순서 변경 안내
> ⚠️ **M2를 M1보다 먼저 진행합니다.**
> 
> 점수 계산 공식 검증 후 온체인 배포 예정. 참조: [ADR-002](../adr/ADR-002-deployment-order.md)

### 📋 Milestones

| 순서 | ID | Title | 상태 | 진행도 | 완료 예정 | 설명 |
|:---:|:---|:---|:---|:---:|:---:|:---|
| 1️⃣ | [M2](milestones/M2.md) | Score Calculation | ✅ 완료 | 100% | ✓ 2026-02-07 | 점수 계산 엔진 |
| 2️⃣ | [M1.5](milestones/M1.5.md) | Local Testing | ✅ 완료 | 100% | ✓ 2026-01-29 | 로컬 테스트 및 통합 검증 |
| 3️⃣ | [M1](milestones/M1.md) | Smart Contract | 🚀 진행 | 57% | 2026-02-01 | 스마트 컨트랙트 배포 (Base Sepolia/Mainnet) |
| 4️⃣ | [M3](milestones/M3.md) | DeFi Integration | 📋 계획 | 0% | TBD | Aave, Uniswap 등 연동 |
| - | [M4](milestones/M4.md) | Frontend Dashboard | 🚀 진행 | 30% | 2026-02-01 | 사용자 대시보드 UI |

### 마일스톤 프로그래스 상세

**M2: Score Calculation Engine** ✅ 완료
- ✅ 점수 공식 확정 (ADR-003)
- ✅ 백테스트 통과 (정확도 75%)
- ✅ API로 점수 조회 가능

**M1.5: Local Testing** ✅ 완료 (100%)
- ✅ M1.5-000: Linear 이슈 등록
- ✅ M1.5-001: Anvil 로컬 노드 설정
- ✅ M1.5-002: 컨트랙트 로컬 배포
- ✅ M1.5-003: API ↔ Contract 연동
- ✅ M1.5-004: 시나리오 테스트 (6/6 통과)
- ✅ M1.5-005: 가스 비용 분석 ($0.25~$2.45/월)
- ✅ M1.5-006: E2E 테스트 스위트 (200+ 테스트)
- ✅ M1.5-007: 테스트 결과 문서화 (LOCAL_TESTING_REPORT.md)

**M1: Smart Contract** 🚀 진행 중 (57% - 4/7 완료)
- ✅ M1-001: Foundry 프로젝트 세팅
- ✅ M1-002: AgentFICOScore.sol 구현
- ✅ M1-003: 단위 테스트 (46개 통과)
- ✅ M1-004: 배포 스크립트 작성
- 🚀 M1-005: Base Sepolia 배포 (시작)
- ⏳ M1-006: Base Mainnet 배포
- ⏳ M1-007: 배포 문서화

**M4: Frontend Dashboard** (진행 중, 상세는 M4.md 참조)

---

## Issues

### 🐛 Bug Fixes
| ID | Title | Status |
|:---|:---|:---|
| - | - | - |

### 🚀 Features
| ID | Title | Status |
|:---|:---|:---|
| - | - | - |

---

## Quick Links

- [AGENTFICO_TECH_SPEC.md](../AGENTFICO_TECH_SPEC.md) - 기술 명세
- [AGENTFICO_BUSINESS_STRATEGY.md](../AGENTFICO_BUSINESS_STRATEGY.md) - 비즈니스 전략
- [DOCUMENTATION_MAP.md](../DOCUMENTATION_MAP.md) - 문서 맵

---

## 문서 작성 규칙

### 마일스톤 문서 (M*.md)
- 새로운 대형 기능 개발
- Phase별 태스크 분류
- Droid 할당 테이블
- 비용 예상 (해당시)

### 이슈 문서 (QT*.md, AF*.md)
- 특정 Linear 이슈 해결
- 문제 정의 섹션
- 근본 원인 분석 테이블
- Goals / Non-Goals 구분

참고 Droids:
- [milestone-architect](../../.factory/droids/milestone-architect.md)
- [linear-project-manager](../../.factory/droids/linear-project-manager.md)

---

## Droid Assignment Guide

| Domain | Recommended Droid |
|:---|:---|
| Smart Contract | `web3-smart-contract-auditor` |
| Blockchain Data | `blockchain-data-analyzer` |
| REST API | `web3-api-developer` |
| DeFi Integration | `defi-protocol-specialist` |
| Testing | `hardhat-test-engineer` |
| Linear 관리 | `linear-project-manager` |
| 마일스톤 계획 | `milestone-architect` |
