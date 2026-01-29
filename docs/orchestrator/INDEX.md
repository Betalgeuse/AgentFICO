# AgentFICO - Orchestrator Tasks Index

프로젝트 마일스톤 및 이슈 태스크 문서 인덱스입니다.

## Milestones

### 실행 순서 변경 안내
> ⚠️ **M2를 M1보다 먼저 진행합니다.**
> 
> 점수 계산 공식 검증 후 온체인 배포 예정. 참조: [ADR-002](../adr/ADR-002-deployment-order.md)

### 📋 Milestones
| ID | Title | Description | Status |
|:---|:---|:---|:---|
| [M2](milestones/M2.md) | Score Calculation | 점수 계산 엔진 | 🚀 In Progress |
| [M1](milestones/M1.md) | Core Infrastructure | 스마트 컨트랙트 배포 | ⏸️ Blocked |
| [M3](milestones/M3.md) | DeFi Integration | Aave, Uniswap 등 DeFi 프로토콜 연동 | 📋 Planned |
| [M4](milestones/M4.md) | Frontend Dashboard | 사용자 대시보드 + 모니터링 UI | 📋 Planned |

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
