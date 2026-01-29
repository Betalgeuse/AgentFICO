# Agent Trust Infrastructure - Unit Economics

**Project:** AgentFICO (Agent Credit Scoring → Compliance)  
**Date:** 2026-01-28  
**Pipeline:** biz-idea-b2b Step 2.5

---

## 💰 Unit Economics 분석

### Phase 1: Agent Credit Scoring (M1-6)

#### Revenue Model

| Tier | 월 가격 | 연 가격 (20% 할인) | 예상 Mix |
|------|--------|-------------------|----------|
| Free | $0 | $0 | 80% |
| Pro | $499 | $4,790 | 15% |
| Business | $999 | $9,590 | 4% |
| Enterprise | Custom | $15K+ | 1% |

#### ACV (Annual Contract Value)

```
Blended ACV Calculation:
- Free: $0 × 80% = $0
- Pro: $4,790 × 15% = $719
- Business: $9,590 × 4% = $384
- Enterprise: $15,000 × 1% = $150
────────────────────────────────
Blended ACV = ~$1,250 (all users)
Paid-only ACV = ~$6,250 (paying customers only)
```

**ACV: $6,250** ✅ (SMB sweet spot $3K-30K)

---

### CAC (Customer Acquisition Cost)

#### Acquisition Channels (Phase 1: PLG)

| Channel | 비용/월 | 예상 Leads | Conv. Rate | CAC |
|---------|--------|------------|------------|-----|
| **Content/SEO** | $500 | 200 | 2% | $125 |
| **Community** | $200 | 100 | 5% | $40 |
| **Paid Ads** | $1,000 | 150 | 1.5% | $444 |
| **Referral** | $0 | 50 | 10% | $0 |

**Blended CAC: ~$800-1,200**

#### CAC Breakdown

```
Marketing Spend: $1,700/month
New Paid Customers: 2-3/month (초기)
CAC = $1,700 / 2.5 = $680

+ Sales Time (Light Touch):
  - 5 demos/week × $50/hour × 1hr = $250
  - Close rate: 30%
  - Sales CAC addition: ~$420

Total CAC: ~$1,100
```

**CAC: $1,100** ✅ (< 6 months ACV = $3,125)

---

### LTV (Lifetime Value)

#### Assumptions

| Metric | Value | 근거 |
|--------|-------|------|
| ACV | $6,250 | Paid-only |
| Gross Margin | 85% | SaaS 표준 |
| Churn Rate | 15%/year | SMB 평균 |
| Expansion | 20%/year | Compliance 업셀 |
| Net Churn | -5%/year | 확장 > 이탈 |

#### LTV Calculation

```
Simple LTV = ACV × Gross Margin / Churn Rate
          = $6,250 × 0.85 / 0.15
          = $35,417

With Expansion (Net Churn -5%):
LTV = ACV × GM / (Churn - Expansion)
    = $6,250 × 0.85 / (-0.05)
    = Negative denominator → Infinite growth scenario

Conservative LTV (3-year horizon):
Year 1: $6,250 × 0.85 = $5,313
Year 2: $6,250 × 1.2 × 0.85 × 0.85 = $5,420
Year 3: $6,250 × 1.44 × 0.85 × 0.72 = $5,508
────────────────────────────────────
3-Year LTV = $16,241
```

**LTV: $16,241 (3-year)** ✅

---

### LTV:CAC Ratio

```
LTV:CAC = $16,241 / $1,100 = 14.8:1
```

**LTV:CAC: 14.8:1** ✅ (≥3:1 기준, Excellent)

---

### CAC Payback Period

```
CAC Payback = CAC / (ACV × Gross Margin / 12)
            = $1,100 / ($6,250 × 0.85 / 12)
            = $1,100 / $443
            = 2.5 months
```

**Payback: 2.5 months** ✅ (≤6 months 기준)

---

### Gross Margin

#### Cost Structure (Per Customer/Month)

| Cost Item | Monthly | Notes |
|-----------|---------|-------|
| Infrastructure (Vercel/Railway) | $5 | 공유 인프라 |
| Blockchain RPC calls | $10 | ERC-8004 조회 |
| Support (자동화) | $5 | Chatbot + Docs |
| **Total COGS** | **$20** | |

```
Monthly Revenue (Pro): $499
Monthly COGS: $20
Gross Margin = ($499 - $20) / $499 = 96%
```

**Gross Margin: 96%** ✅ (≥75% 기준)

---

### NRR (Net Revenue Retention)

#### Projection

| Factor | Rate | Impact |
|--------|------|--------|
| Logo Churn | -15% | SMB 평균 |
| Downgrade | -5% | Tier 다운 |
| Upsell | +15% | 더 높은 Tier |
| **Expansion (Compliance)** | +30% | Phase 2 모듈 |

```
NRR = 100% - 15% - 5% + 15% + 30% = 125%
```

**NRR: 125%** ✅ (≥95% 기준, Excellent)

---

## 📊 Phase 2 확장 시 Unit Economics

### Agent Credit Score + Compliance Bundle

| Metric | Phase 1 | Phase 2 | Change |
|--------|---------|---------|--------|
| **ACV** | $6,250 | $15,000 | +140% |
| **CAC** | $1,100 | $2,500 | +127% (Sales 필요) |
| **LTV (3yr)** | $16,241 | $45,000 | +177% |
| **LTV:CAC** | 14.8:1 | 18:1 | +22% |
| **Payback** | 2.5mo | 3mo | +20% |
| **NRR** | 125% | 150% | +25pp |

---

## 🎯 Unit Economics Scorecard

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **ACV** | $3K-30K | $6,250 | ✅ PASS |
| **CAC** | < 6mo ACV | $1,100 (2.1mo) | ✅ PASS |
| **LTV:CAC** | ≥3:1 | 14.8:1 | ✅ PASS |
| **Payback** | ≤6 months | 2.5 months | ✅ PASS |
| **Gross Margin** | ≥75% | 96% | ✅ PASS |
| **NRR** | ≥95% | 125% | ✅ PASS |

**Unit Economics: ALL PASS** ✅

---

## 📈 Path to $1M ARR

### Scenario Modeling

```
Target: $1M ARR = $83K MRR

With Blended ARPU $520/month (mix of tiers):
Customers needed = $83K / $520 = 160 paying customers

Timeline:
- M6: 50 customers × $520 = $26K MRR
- M12: 160 customers × $520 = $83K MRR = $1M ARR
- M18: 400 customers × $600 = $240K MRR = $2.9M ARR
```

### Growth Assumptions

| Month | New Custs | Churn | Net | Total | MRR |
|-------|-----------|-------|-----|-------|-----|
| M1 | 5 | 0 | 5 | 5 | $2.6K |
| M3 | 15 | 1 | 14 | 25 | $13K |
| M6 | 25 | 3 | 22 | 50 | $26K |
| M9 | 40 | 5 | 35 | 100 | $52K |
| M12 | 50 | 8 | 42 | 160 | $83K |

---

## 💡 Key Insights

### Strengths
1. **높은 Gross Margin (96%)** - SaaS 인프라 비용 최소화
2. **빠른 Payback (2.5mo)** - PLG 모델 효율성
3. **강한 NRR (125%)** - Compliance 확장으로 업셀

### Risks
1. **SMB Churn** - 15% 가정, 실제는 더 높을 수 있음
2. **CAC 상승** - 경쟁 심화 시 마케팅 비용 증가
3. **Expansion 실패** - Compliance 업셀 안 되면 NRR 하락

### Mitigation
1. **고객 성공 투자** - 온보딩 자동화, 프로액티브 지원
2. **커뮤니티 중심 성장** - 낮은 CAC 유지
3. **Phase 2 빠른 검증** - Compliance 수요 조기 확인

---

*다음 단계: Validation Loop (Step 3)*
