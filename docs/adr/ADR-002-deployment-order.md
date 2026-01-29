# ADR-002: 백엔드 우선 개발 (M2 before M1)

## Status
✅ APPROVED (2026-01-29)

## Context
- 스마트 컨트랙트 AgentFICOScore.sol 구현 완료
- 점수 계산 공식 (40-40-20 가중치) 미검증
- 데이터 소스 (Etherscan, x402, ERC-8004) 연동 미구현

## Decision
온체인 배포(M1)를 보류하고, 백엔드 점수 계산 로직(M2)을 먼저 개발한다.

## Consequences
### Positive
- 실제 데이터로 점수 공식 검증 가능
- 컨트랙트 재배포 리스크 최소화
- 신뢰할 수 있는 점수 시스템 구축

### Negative
- DeFi 연동 일정 지연
- 온체인 MVP 데모 지연

## Related
- M1: Smart Contract 배포 → **BLOCKED** (M2 완료 후 진행)
- M2: Score Calculation Engine → **IN PROGRESS**
