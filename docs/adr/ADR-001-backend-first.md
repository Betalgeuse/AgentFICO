# ADR-001: 백엔드 우선 개발

## Status
✅ APPROVED (2026-01-29)

## Context
- 스마트 컨트랙트 AgentFICOScore.sol 구현 완료
- 점수 계산 공식 (40-40-20 가중치) 미검증
- 데이터 소스 (Etherscan, x402, ERC-8004) 연동 미구현

## Decision
온체인 배포를 보류하고, 백엔드 점수 계산 로직을 먼저 개발한다.

**실행 순서:**
1. M1: Score Calculation Engine (점수 공식 개발 + 검증)
2. M2: Local Testing (로컬 통합 테스트)
3. M3: Testnet Deploy (Base Sepolia 배포)

## Consequences
### Positive
- 실제 데이터로 점수 공식 검증 가능
- 컨트랙트 재배포 리스크 최소화
- 신뢰할 수 있는 점수 시스템 구축

### Negative
- DeFi 연동 일정 지연
- 온체인 MVP 데모 지연

## Related
- [M1](../orchestrator/milestones/M1.md) - Score Calculation Engine ✅ 완료
- [M2](../orchestrator/milestones/M2.md) - Local Testing ✅ 완료
- [M3](../orchestrator/milestones/M3.md) - Testnet Deploy 🚀 진행 중
