# ADR-003: Anti-Gaming 시스템 선택 (ZK 대신)

## Status
✅ APPROVED (2026-01-29)

## Context

AgentFICO 점수 시스템에서 게이밍(점수 조작) 방지가 필요합니다.

초기에는 ZK Proof를 통해 점수 계산의 기밀성을 유지하면서 검증 가능성을 확보하려 했습니다.

### ZK Proof 검토 결과

| 질문 | 답변 |
|:-----|:-----|
| 숨길 데이터가 있는가? | ❌ 트랜잭션, x402, ERC-8004 모두 온체인 공개 |
| 기밀 계산이 필요한가? | ❌ 입력이 공개되면 누구나 재계산 가능 |
| ZK가 해결하는 문제? | 공식 비공개 유지 |
| 더 간단한 대안? | ✅ Anti-Gaming 레이어로 동일 효과 |

### 실제 FICO와의 비교

```
실제 FICO:
- 입력: 개인 금융 데이터 (비공개)
- 공식: 비공개
- → ZK가 유용할 수 있음 (기밀 데이터 + 기밀 공식)

AgentFICO:
- 입력: 온체인 데이터 (공개)
- 공식: 공개 (투명성 가치)
- → ZK 의미 없음 (숨길 게 없음)
```

## Decision

**ZK Proof 대신 Anti-Gaming Scoring System 도입**

### 핵심 전략

1. **기본 공식 공개** (Web3 투명성)
   - 가중치: tx_success 40%, x402 40%, erc8004 20%
   - 계산 로직: 공개

2. **Anti-Gaming 레이어 추가** (게이밍 방지)
   - Time Decay: 최근 활동에 더 높은 가중치
   - Anomaly Detection: 급격한 변화 탐지
   - Consistency Bonus: 장기 성과 보상
   - TX Quality: 의미 있는 트랜잭션만 인정

3. **세부 계수 비공개** (FICO 방식)
   - 정확한 decay 곡선
   - 이상 탐지 임계값
   - 보너스 계산 공식

### 원칙
```
"무엇을 측정하는지는 공개, 어떻게 측정하는지는 비공개"
```

## Consequences

### Positive
- ZK 인프라 복잡성 제거 (Trusted Setup, Circuit 개발 등)
- 개발 시간 7-9주 → 2-3주로 단축
- 가스 비용 절감 (ZK 검증 ~200K gas 절약)
- 유지보수 용이

### Negative
- 완벽한 기밀성 불가 (시간이 지나면 패턴 추측 가능)
- 정기적인 계수 업데이트 필요

### Neutral
- 게이밍 방지 효과는 ZK와 유사하게 달성 가능

## Alternatives Considered

### Option A: ZK Proof (기각)
- 장점: 수학적 기밀성
- 단점: 입력이 공개라 의미 제한, 높은 복잡성

### Option B: 완전 공개 (기각)
- 장점: 최대 투명성
- 단점: 게이밍에 취약

### Option C: Anti-Gaming Layer (선택)
- 장점: 적절한 투명성 + 게이밍 방지, 낮은 복잡성
- 단점: 완벽하지 않음

## Related
- [M5: Anti-Gaming Scoring System](../orchestrator/milestones/M5.md)
- [ADR-002: Score Formula](ADR-002-score-formula.md)
