# AgentFICO GTM-Driven Agile PRD Roadmap

**Philosophy:** "Ship → Learn → Iterate" (너무 완벽하지 말 것)

**Created:** 2026-01-29

---

## 📊 3단계 GTM 전략

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Stage 1: MVP (4주)        Stage 2: Scale (8주)             │
│  ──────────────────        ─────────────────                │
│  • 1명 고객 확보            • 5명 고객 확보                  │
│  • Proof of Concept        • 정식 계약                      │
│  • Manual everything       • 자동화 시작                    │
│                                                              │
│  Stage 3: Growth (12주+)                                    │
│  ──────────────────                                         │
│  • 20+ 고객 확보                                            │
│  • 자동 스케일링                                            │
│  • 수익화 최적화                                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🚀 Stage 1: MVP (4주) - 가장 최소한의 것

### 1주차: 핵심 하나만 정의

**PRD 요구사항:**
```
Q1. 첫 번째 고객 누구?
    예: HeyElsa, PayAI Network, 또는 Bond.Credit

Q2. 그 고객의 ONE 문제는?
    예: "AgentFICO로 에이전트 신뢰도를 점수화하고 싶어"

Q3. 최소 기능은?
    예: 1개 API 엔드포인트 (GET /score)
```

**1주차 작업:**
- [ ] 고객 1명 확정 (zoom call)
- [ ] 그들의 정확한 요구사항 정리 (1 page)
- [ ] 우리의 솔루션 스케치 (1 page)

**산출물:**
```
file: stage1-week1-customer-problem.md (2 page max)

1. Customer Profile
   - 이름: HeyElsa
   - 문제: AgentOS의 에이전트 신뢰도 평가 필요
   - 해결책 아이디어: AgentFICO 점수 제공

2. Our Solution (sketch)
   - 1 API 엔드포인트: GET /agent/0x123/score
   - 입력: agent_id
   - 출력: score (0-100), risk_level (high/med/low)
   - 계산법: (간단한 수식 1줄)
```

---

### 2주차: API 설계 (정말 간단하게)

**PRD 요구사항:**
```
Q4. Score는 어떻게 계산?
    옵션 A: 온체인 트래잭션 성공률 (가장 간단)
    옵션 B: 트래잭션 + 시간 (medium)
    옵션 C: 5 dimensions (너무 무거움)
    
    추천: 옵션 A (MVP는 A로 시작, B/C는 나중)

Q5. 데이터는 어디서?
    - Etherscan API (무료, 빠름)
    - 또는 기존 온체인 데이터
```

**2주차 작업:**
- [ ] API 스펙 1 page (엔드포인트 1개)
- [ ] 스코어 계산식 (수식 1줄)
- [ ] Mock API 응답 (JSON 샘플)

**산출물:**
```
file: stage1-week2-api-spec.md (2 page max)

1. API Endpoint

   GET /agent/:agent_id/score
   
   Response:
   {
     "agent_id": "0x123...",
     "score": 75,
     "risk_level": "medium",
     "updated_at": "2026-01-29T10:00Z"
   }

2. Score Calculation (Version 0.1)
   
   score = (successful_txns / total_txns) * 100
   
   Example: 150 successful out of 200 = 75 score

3. Data Source
   
   Etherscan API (on-chain transaction data only)
   Update: 1x per day (not real-time)
```

---

### 3주차: 개발 + 초기 테스트

**PRD 요구사항:**
```
Q6. 테스트는 어떻게?
    - 고객 데이터 10개 에이전트로 수동 검증
    - 손으로 계산해본 값과 비교
```

**3주차 작업:**
- [ ] API 개발 (FastAPI 또는 Express, 4시간)
- [ ] PostgreSQL에 agent table + score table (2시간)
- [ ] Etherscan 데이터 가져오기 (2시간)
- [ ] Manual test 10개 에이전트 (2시간)

**산출물:**
```
file: stage1-week3-dev-checklist.md

- [x] API 구현
- [x] Database 셋업
- [x] Etherscan 통합
- [x] 10개 에이전트 테스트 완료
- [ ] 고객 시연 준비
```

---

### 4주차: 고객 테스트 + 피드백

**PRD 요구사항:**
```
Q7. 고객 반응?
    - 점수가 맞나?
    - 뭘 더 해야 하나?
    - 가격은 얼마?
```

**4주차 작업:**
- [ ] 고객에게 API 제공 (Postman)
- [ ] 고객이 직접 테스트
- [ ] Feedback 수집 (Zoom call)
- [ ] Pivot or double down 결정

**산출물:**
```
file: stage1-week4-customer-feedback.md

Customer Feedback:
- "점수 계산이 맞는 것 같아"
- "근데 우리 에이전트 100개 있는데 한 번에 조회 안 되네?"
- "실시간 업데이트 되면 좋겠어"
- "가격은 $100/month 괜찮아"

Decision:
→ 진행! Stage 2로 간다
→ 배치 API 추가 (우선순위 높음)
→ 실시간 업데이트 (나중)
```

---

## Stage 1 완료 체크리스트

```
✅ 고객 1명 확보 (계약 아직 안 해도 됨)
✅ API 1개 (GET /score)
✅ 데이터 소스 1개 (Etherscan)
✅ Database 기본 (agents, scores 테이블)
✅ 고객 피드백 수집
✅ 다음 단계 명확함
```

**Stage 1 비용:** 4주, 1-2명 개발자, $0 인프라 (Vercel/Railway free tier)

---

## 📈 Stage 2: Scale (8주) - 고객 5명 목표

### 2주 간격으로 릴리스

#### Sprint 1 (주 5-6): 배치 API

```
PRD 요구:
  Q: 100개 에이전트 점수를 한 번에 조회?
  A: POST /scores/batch
     Input: [agent_id_1, agent_id_2, ...]
     Output: [score_1, score_2, ...]

개발: 1일
테스트: 1일
배포: 반일
```

#### Sprint 2 (주 7-8): 실시간 업데이트

```
PRD 요구:
  Q: 점수가 자동으로 업데이트 되나?
  A: 네. 매시간 (not 실시간)

개발: 2일 (scheduler)
테스트: 1일
배포: 반일
```

#### Sprint 3 (주 9-10): 파트너 #2 온보딩

```
PRD 요구:
  고객 #2를 위해 뭐 필요?
  A: 고객이랑 얘기하고 결정

개발/통합: 3일
```

#### Sprint 4 (주 11-12): 점수 정확도 개선

```
PRD 요구:
  고객 피드백에서 나온 문제?
  A: 점수가 너무 변덕스러움
  
  해결: 데이터 소스 1개 더 추가
  또는 계산식 조정

개발: 2일
테스트: 2일
```

---

## 📋 Stage 2 PRD (매 Sprint마다 업데이트)

### Sprint 1 PRD Template

```markdown
# Sprint 1: Batch Scoring API

## Goal
고객이 100개 에이전트 점수를 한 번에 조회 가능

## Feature
- POST /scores/batch
- Input: max 100 agent_ids
- Output: List of scores
- Latency: <1 sec

## Success Criteria
- [ ] API 동작
- [ ] 성능 테스트 통과 (<1s for 100)
- [ ] 고객 테스트 완료
- [ ] 다음 고객도 쓸 수 있게

## Estimate
1주일 (개발 3일 + 테스트/배포 2일 + 버퍼 2일)
```

---

## 💰 Stage 3: Growth (12주+) - 수익화

**Only if:**
- 고객 5명 이상
- 월 $5K+ recurring revenue
- 점수 정확도 >80%

**Then focus on:**
1. Sales (10명 고객까지)
2. 자동화 (수동 작업 제거)
3. 안정성 (uptime, monitoring)
4. 확장 (데이터 소스 추가, ML model)

---

## 📝 매주 1page PRD 템플릿

**모든 Sprint의 PRD는 이것만 쓰세요:**

```markdown
# Sprint N: [Feature Name]

## Why (고객 문제)
한 문장

## What (우리가 할 것)
- 기능 1
- 기능 2
(최대 3개)

## How (기술)
- API 엔드포인트 or 변경사항
- 데이터 소스
- 계산식 (있으면)

## Success = Done
- [ ] 개발 완료
- [ ] 테스트 통과
- [ ] 고객 테스트
- [ ] Deploy

## Estimate
X주

## Dependencies
- 없음 or [다른 Sprint]
```

---

## 🎯 Stage별 PRD 작성량

| Stage | 주수 | 주당 PRD 페이지 | 스프린트 | 총 PRD |
|-------|------|--------------|---------|--------|
| **1** | 4 | 1 page/주 | 4개 | 4 page |
| **2** | 8 | 1 page/2주 | 4개 | 2-4 page |
| **3** | 12+ | 1 page/2주 | 6개+ | 3-6 page |
| **Total** | 24 | | | ~10 page |

**vs 무거운 PRD:**
- 옛날: 처음에 50 page PRD 작성 → 2개월 지연
- 새로운 방식: 1 page/주 × 24주 = 실행력

---

## 📊 각 Stage 후 Go/No-Go 결정

### Stage 1 Exit Criteria (4주 후)

```
Go?
  [ ] 고객 1명이 "맞아, 이거 쓸 수 있겠다" 말함
  [ ] API 기본 동작
  [ ] 다음 고객 1명 더 찾음
  
No-Go?
  [ ] 고객 피드백이 "점수가 틀렸어"
  → Pivot: 다른 고객? 다른 계산법?
```

### Stage 2 Exit Criteria (8주 후)

```
Go?
  [ ] 고객 3명 이상 쓰고 있음
  [ ] 월 $1K+ 수익 (또는 약속)
  [ ] 기술적 안정성 (downtime 없음)
  
No-Go?
  [ ] 고객이 "이거 정확성이 낮아" 불평
  → Pivot: 더 정교한 모델? 다른 데이터?
```

### Stage 3 Go (12주 후)

```
[ ] 고객 5명 이상
[ ] 월 $5K+ 수익
[ ] 경쟁자 없음 (또는 우리가 더 좋음)
→ Growth mode로 전환
```

---

## 🗂️ 문서 구조 (매우 간단)

```
agentfico-gtm/
├─ stage1/
│  ├─ week1-customer-problem.md (2 page)
│  ├─ week2-api-spec.md (2 page)
│  ├─ week3-dev-checklist.md (1 page)
│  └─ week4-feedback.md (1 page)
│
├─ stage2/
│  ├─ sprint1-batch-api.md (1 page)
│  ├─ sprint2-realtime-updates.md (1 page)
│  ├─ sprint3-partner2.md (1 page)
│  └─ sprint4-accuracy.md (1 page)
│
└─ stage3/
   ├─ sprint1-sales.md
   ├─ sprint2-monitoring.md
   └─ ...
```

**각 파일 = 1-2 page 최대**

---

## ✅ 지금 바로 시작하기

**1시간 안에:**
1. [ ] Stage 1 Week 1 PRD 작성 (고객 1명 정하기)
2. [ ] 고객에게 zoom 신청
3. [ ] 1주 후 Week 2 PRD 작성 예약

**그게 전부.**

다음 주에:
- Week 2 PRD 쓰고
- API 설계하고
- 3주차부터 코딩 시작

---

## 🎯 핵심 원칙

```
1. 1 Stage = 최대 2-4주
2. 1 PRD = 최대 2 page
3. 고객 피드백이 우선
4. 완벽함보다 속도
5. 실패도 성공 (배우니까)
```

---

**Next:** Stage 1 Week 1 PRD 작성하기 👇
