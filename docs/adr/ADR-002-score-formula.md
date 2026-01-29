# ADR-002: AgentFICO 점수 공식 확정

## Status
✅ APPROVED (2026-01-29)

## Context
AgentFICO는 AI 에이전트의 신용도를 평가하는 점수 시스템입니다.
점수 공식은 온체인 스마트 컨트랙트에 반영되어 수정이 어려우므로,
충분한 검증 후 확정해야 합니다.

## 백테스트 결과

### 테스트 환경
- 샘플 에이전트: 8개 (다양한 성능 프로필)
- 테스트 기간: 30일
- 가중치 변형: 4가지 조합

### 기본 가중치 (40-40-20) 결과
| 지표 | 값 |
|------|-----|
| 예측 정확도 | 75.0% |
| 평균 점수 | 629 |
| 점수 범위 | 360 - 910 |
| 표준편차 | 168.0 |

### 점수 분포
| Tier | Count | 비율 |
|------|-------|------|
| EXCELLENT (850+) | 1 | 12.5% |
| GOOD (750-849) | 1 | 12.5% |
| AVERAGE (650-749) | 2 | 25.0% |
| BELOW_AVERAGE (550-649) | 2 | 25.0% |
| POOR (<550) | 2 | 25.0% |

### 개별 에이전트 결과
| Agent ID | Expected | Actual | Score | Match |
|----------|----------|--------|-------|-------|
| excellent_trader | EXCELLENT | EXCELLENT | 910 | ✓ |
| good_analyst | GOOD | GOOD | 760 | ✓ |
| average_bot | AVERAGE | AVERAGE | 660 | ✓ |
| struggling_agent | BELOW_AVERAGE | BELOW_AVERAGE | 560 | ✓ |
| risky_agent | POOR | POOR | 360 | ✓ |
| tx_specialist | AVERAGE | BELOW_AVERAGE | 640 | ✗ |
| profitable_but_risky | AVERAGE | AVERAGE | 660 | ✓ |
| new_agent | BELOW_AVERAGE | POOR | 480 | ✗ |

### 가중치 민감도 분석
| 가중치 (tx-x402-erc8004) | 정확도 | 평균 점수 |
|--------------------------|--------|----------|
| 40-40-20 (기본) | 75.0% | 629 |
| 50-30-20 (tx 강조) | 75.0% | 633 |
| 30-50-20 (x402 강조) | 75.0% | 624 |
| 33-33-34 (균등) | 37.5% | 616 |

### 분석 결론
- 40-40-20 및 50-30-20, 30-50-20 가중치가 동일한 최고 정확도(75%)를 달성
- 균등 가중치(33-33-34)는 37.5%로 현저히 낮은 정확도
- **40-40-20 가중치 유지** 권장 (기본값, tx와 x402 균형 중시)

## Decision

### 최종 점수 공식

```
overall = (txSuccess × 0.40 + x402Profitability × 0.40 + erc8004Stability × 0.20) × 10
```

**범위:**
- 입력: 각 지표 0-100
- 출력: overall 0-1000

### 가중치 결정 근거
1. **txSuccess (40%)**: 트랜잭션 성공률은 에이전트 신뢰도의 핵심 지표
2. **x402Profitability (40%)**: 수익성은 지속 가능성의 중요 지표
3. **erc8004Stability (20%)**: 등록/검증 상태는 보조 지표

### 리스크 레벨 임계값
| Level | 이름 | 점수 범위 | 의미 |
|-------|------|----------|------|
| 1 | EXCELLENT | 850+ | 최우수, 최저 위험 |
| 2 | GOOD | 750-849 | 우수 |
| 3 | AVERAGE | 650-749 | 평균 |
| 4 | BELOW_AVERAGE | 550-649 | 평균 이하 |
| 5 | POOR | <550 | 고위험 |

### 신뢰도(Confidence) 계산
```
confidence = 50 (기본)
           + min(30, tx_count ÷ 3)  (트랜잭션 수)
           + 20 (등록된 경우)
```

## Consequences

### Positive
- 검증된 공식으로 온체인 배포 가능
- DeFi 프로토콜이 신뢰할 수 있는 점수 제공
- 명확한 리스크 레벨로 의사결정 지원

### Negative
- 가중치 변경 시 컨트랙트 재배포 필요
- x402/ERC-8004 표준 변경 시 조정 필요

## M1 재개 조건 충족

✅ 이 ADR로 다음 조건이 충족됩니다:
1. 점수 공식 확정
2. 백테스트 통과 (정확도 75%, 목표 70%+ 초과)
3. API로 점수 조회 가능

→ M1 (온체인 배포) 재개 가능

## Related
- [ADR-002](ADR-002-deployment-order.md) - M2 우선 개발 결정
- [AGENTFICO_TECH_SPEC](../business-context/specs/AGENTFICO_TECH_SPEC.md) - 기술 명세
