# Agent Trust Infrastructure - ICP Analysis

**Project:** AgentFICO (Agent Credit Scoring → Compliance 확장)  
**Date:** 2026-01-28  
**Pipeline:** biz-idea-b2b Step 1

---

## 📊 시장 규모 분석

### 직접 관련 시장

| 시장 | 2025 | 2026 | 2030+ | CAGR | 출처 |
|------|------|------|-------|------|------|
| **AI Model Risk Scoring** | $3.8B | ~$4.6B | $7.9B (2033) | 20.4% | HTF Market |
| **AI Governance/Compliance** | $2.5B | $3.4B | $68.2B (2035) | 39.4% | Market.us |
| **AI Agents Market** | $7.8B | $9.1B | $52.6B (2030) | 46.3% | M&M |
| **Agentic AI Market** | - | $9.1B | $139B (2034) | 40.5% | Fortune BI |

### TAM-SAM-SOM 분석

```
TAM (Total Addressable Market):
- AI Governance + AI Agents = $12.5B (2026)
- ERC-8004 에이전트 경제 포함 시 $15B+

SAM (Serviceable Addressable Market):
- Agent Trust/Reputation 특화 = TAM의 ~10%
- ~$1.2B-1.5B (2026)

SOM (Serviceable Obtainable Market):
- SMB + 초기 Enterprise = SAM의 ~2-5%
- ~$25M-75M (초기 3년)
```

**시장 규모 점수: 9/10** ✅ (TAM $50M+ 기준 충족)

---

## 🎯 ICP (Ideal Customer Profile) 분석 - REVISED

> ⚠️ **2026-01-29 수정**: SMB Non-crypto → DeFi/AgentFi + Regulated DeFi로 타겟 변경
> 
> **이유**: FICO(신용점수)는 자금/크레딧이 오가는 곳에서만 의미 있음 = DeFi Native

### Primary ICP: DeFi/AgentFi 프로토콜

| 속성 | 세부 내용 |
|------|----------|
| **Industry** | DeFi, AgentFi, Agent Marketplaces, 결제 프로토콜 |
| **프로젝트 유형** | 에이전트 대출, 크레딧 라인, 마켓플레이스, 결제 레이어 |
| **핵심 니즈** | 에이전트에게 자금/크레딧 제공 전 리스크 평가 |
| **Role (구매자)** | Founder, Protocol Lead, Head of Risk |
| **Tech Stack** | ERC-8004, x402, Ethereum/EVM, Solidity |
| **유스케이스** | 대출 한도 결정, 담보 비율 산정, 수수료 차등, 보험료 계산 |

**왜 DeFi가 핵심인가:**
```
신용점수가 필요한 순간:
- "이 에이전트에게 $10K 빌려줘도 될까?" → 대출 프로토콜
- "이 에이전트에게 크레딧 라인 얼마나 줄까?" → AgentFi
- "담보 얼마나 요구할까?" → 마켓플레이스
- "수수료 얼마로 할까?" → 결제 레이어
- "보험료 얼마로 할까?" → 보험 프로토콜

→ 전부 돈이 오가는 DeFi 유스케이스
```

### Secondary ICP: 규제 대응 필요 DeFi (Regulated DeFi)

| 속성 | 세부 내용 |
|------|----------|
| **프로젝트 유형** | 기관 고객 받으려는 DeFi, 미국/EU 진출 프로젝트 |
| **핵심 니즈** | 규제 준수 + 신용 평가 (Compliance + FICO 번들) |
| **Role (구매자)** | Legal/Compliance Lead, Founder |
| **차별화 포인트** | Bond.Credit에 없는 Compliance 기능 |

### Tertiary ICP: CeFi ↔ DeFi 브릿지

| 속성 | 세부 내용 |
|------|----------|
| **프로젝트 유형** | 금융기관의 DeFi 진입, CeFi-DeFi 브릿지 서비스 |
| **핵심 니즈** | 기존 금융 규제 + 에이전트 리스크 평가 |
| **Role (구매자)** | Head of Digital Assets, CTO, CCO |

### 구매 결정 구조 (DeFi 프로토콜)

```
Decision Maker: Founder / Protocol Lead (1-2명)
Influencer: Core Contributors, Investors
End User: Protocol, Smart Contracts
───────────────────────────────────────────
Sales Cycle: 2-4주 (DeFi), 2-3개월 (Regulated DeFi)
Procurement: 토큰/USDC or 계약
Budget: Protocol Treasury / Grants
```

**ICP 명확성 점수: 9/10** ✅ (타겟 명확해짐)

---

## 📈 Market Opportunity Signals

### Why Now? (타이밍 신호)

1. **ERC-8004 메인넷 런칭** (2026-01-28)
   - 오늘 런칭 = 에이전트 신뢰 인프라 수요 급증 예상

2. **규제 강화 트렌드**
   - 2026 State AI Bills: AI 책임 확대 법안 다수
   - EU AI Act: 고위험 AI 시스템 compliance 의무화
   - NAIC AI Model Bulletin: 23개 주 채택

3. **Gartner 예측**
   - 2026년 40% 기업 앱에 AI 에이전트 탑재 (2025년 5% → 8x 성장)

4. **투자 급증**
   - Agentic AI 스타트업 $966M+ 펀딩 (54개 기업)
   - AIUC $15M 시드 (에이전트 인증/보험)

### Pain Point Intensity (고통 강도)

| Pain Point | 강도 | 현재 해결책 |
|------------|------|------------|
| "에이전트 신뢰도를 어떻게 검증?" | 🔴 9/10 | 없음 (수동 테스트) |
| "규제 감사 대응 준비가 안 됨" | 🔴 9/10 | 수동 문서화 |
| "에이전트 선택 기준이 없음" | 🟡 8/10 | 유명한 것만 사용 |
| "사고 발생 시 책임 소재 불명확" | 🔴 9/10 | 없음 |

---

## 🏢 경쟁 포지셔닝

### 경쟁 구도

```
                    ┌─────────────────────────────────────┐
                    │        ERC-8004 생태계              │
                    │  (Identity + Reputation + Validation)│
                    └─────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
   ┌────▼────┐                ┌─────▼─────┐               ┌────▼────┐
   │ 기본     │                │ AgentFICO │               │ 기본     │
   │Reputation│                │ (우리)    │               │Validation│
   │(0-100)   │                │           │               │(zkML/TEE)│
   └─────────┘                └───────────┘               └─────────┘
        │                           │                           │
        │                    ┌──────┴──────┐                    │
        │                    │             │                    │
                        ┌────▼────┐   ┌────▼────┐
                        │ Credit  │   │Compliance│
                        │ Score   │   │ Audit   │
                        │ (1단계) │   │ (2단계) │
                        └─────────┘   └─────────┘
```

### 차별화 포인트

| vs 경쟁자 | AgentFICO 차별화 |
|-----------|-----------------|
| ERC-8004 Reputation | 단순 0-100 → 다차원 신용점수 (금융급) |
| FICO (인간용) | 인간 → AI 에이전트 특화 |
| AIUC | 인증+보험 → 점수+감사 |
| OpenRank | 소셜 그래프 → 에이전트 행동 기반 |

---

## 💰 Unit Economics 예상

### Phase 1: Agent Credit Scoring

| Metric | 예상치 | 벤치마크 |
|--------|--------|---------|
| **ACV** | $6K-12K/년 | SMB sweet spot |
| **Pricing** | $500-1,000/월 | API calls + 대시보드 |
| **Gross Margin** | 85%+ | SaaS 평균 이상 |
| **Payback** | 3-4개월 | ≤6개월 목표 |

### Phase 2: + Compliance Audit

| Metric | 예상치 | 벤치마크 |
|--------|--------|---------|
| **ACV** | $15K-30K/년 | Mid-market |
| **Expansion** | Credit → Compliance 번들 | 150% NRR 가능 |
| **LTV:CAC** | 4:1+ | Excellent |

---

## 📊 Step 1 스코어링

| 기준 | 점수 | 근거 |
|------|------|------|
| **Market Size** | 9/10 | TAM $12B+ (2026), SAM $1.2B+ |
| **ICP Clarity** | 8/10 | SMB AI/Web3 기업, CTO/VP Eng 명확 |
| **Timing** | 10/10 | ERC-8004 런칭일, 규제 강화 |
| **Competition** | 9/10 | Blue ocean (에이전트 신용점수 없음) |

**Step 1 Total: 18/20** ✅ PASS (≥16 기준)

---

## 🚀 확장 전략: Credit Score → Compliance

### Phase 1: AgentFICO Score (M1-6)
```
MVP: 에이전트 신용 점수 API
- ERC-8004 Reputation Registry 데이터 활용
- 다차원 점수 (성능, 안정성, 보안, 규제준수)
- 대시보드 + API

타겟: AI 에이전트 개발사, Web3 프로젝트
ACV: $6K-12K
```

### Phase 2: + Compliance Module (M6-12)
```
확장: 규제 준수 감사 도구 추가
- 감사 로그 자동 생성
- 규제 프레임워크 매핑 (EU AI Act, NAIC 등)
- 컴플라이언스 리포트 자동화

타겟: 규제 산업 (금융, 의료, 보험)
ACV: $15K-30K (번들)
```

### Phase 3: Full Trust Stack (M12+)
```
플랫폼: Trust Infrastructure 플랫폼
- Credit Score + Compliance + Insurance 연동
- 보험사 파트너십 (AIUC, Armilla 등)
- Enterprise 확장

타겟: Enterprise, 규제 기관
ACV: $50K+
```

---

## 🎯 Founder-Market Fit

| 강점 | 적용 |
|------|------|
| **금융규제 이해** | 신용점수 로직, 컴플라이언스 프레임워크 설계 |
| **풀스택 개발** | API, 대시보드, ERC-8004 통합 구현 |
| **AI/바이브코딩** | 점수 알고리즘, 자동화 파이프라인 |
| **MBA 네트워크** | 초기 고객 (AI 스타트업 창업자) |
| **기술↔비즈니스 통역** | 기술적 점수를 비즈니스 의사결정으로 전환 |

**Founder-Market Fit: 9/10** ✅

---

*다음 단계: GTM Strategy Fit Analysis (Step 1.5)*
