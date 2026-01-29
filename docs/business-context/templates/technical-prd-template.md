# Technical PRD: AgentFICO Score API v1.0

**Document Version:** 0.1 (Draft)  
**Last Updated:** 2026-01-29  
**Status:** 📝 In Progress (Awaiting product decisions)  
**Owner:** [Product Manager / Tech Lead]

---

## 📌 Executive Summary

**One-Liner Definition:**
> AgentFICO is a real-time credit scoring API for ERC-8004 agents, enabling DeFi protocols and x402-powered services to assess agent trustworthiness before financial transactions.

**Key Facts:**
- **MVP Target Launch:** Q2 2026 (April-June)
- **Primary Users:** DeFi protocols (lending, marketplaces), x402 Market integration
- **Core Value:** Reduce risk of agent-based financial transactions through verifiable, data-driven reputation scoring
- **KPIs:** 5+ integrated protocols, <100ms API latency, >85% score accuracy

---

## 🎯 Problem Statement & Opportunity

### The Problem: AI Agent Trust Deficit

**Context:**
- ERC-8004 (launching Jan 30, 2026) = standardized agent identity & reputation registry
- x402 (live since 2025) = payment protocol for agent-to-human/agent-to-agent transactions
- **Gap:** No standardized trust scoring for agents conducting DeFi/payment operations

**Specific Pain Points:**

1. **DeFi Protocols** (Aave, Compound, lending primitives)
   - "Should I allow this agent to borrow $100K?"
   - Current solution: Manual audits (slow, expensive)
   - AgentFICO solution: Real-time score-based risk assessment

2. **x402 Market** (payment settlement layer)
   - "Should I accept this agent's payment request?"
   - Current solution: Accept all (high fraud risk) or manual checks
   - AgentFICO solution: Dynamic fee/collateral based on score

3. **Agent Platforms** (HeyElsa, Theoriq, Minara)
   - "Which agents should I highlight/recommend?"
   - Current solution: Ad-hoc reputation (Twitter, community feedback)
   - AgentFICO solution: Standardized, on-chain reputation

### Market Opportunity

| Segment | 2026 TAM | AgentFICO SAM | Use Case |
|---------|----------|---------------|----------|
| **DeFi Lending** | $50B | $5B | Agent borrow limits |
| **x402 Payments** | $1B | $200M | Risk-adjusted fees |
| **Agent Marketplaces** | $500M | $50M | Agent ranking/discovery |
| **BNPL for Agents** | $100M | $30M | Agent credit lines |
| **Total** | **$51.6B** | **$5.28B** | |

**AgentFICO Addressable Market (Year 1):** ~$50-100M (assuming 2-5% SAM capture)

---

## 💡 Solution Overview

### Core Product: AgentFICO Score API

```
┌─────────────────────────────────────────────────┐
│          AgentFICO Score API (REST)             │
├─────────────────────────────────────────────────┤
│  Inputs:                                         │
│  • Agent ID (ERC-8004 address or UUID)          │
│  • Optional: Amount, Protocol, Time window      │
│                                                  │
│  Processing:                                    │
│  • Aggregate 10+ on-chain/off-chain data        │
│  • Calculate 5-dimensional score                │
│  • Apply risk model                             │
│                                                  │
│  Outputs:                                       │
│  • Overall Score (0-1000)                       │
│  • Risk Level (High/Medium/Low)                 │
│  • Dimension Breakdown                          │
│  • Recommended Terms (fee %, collateral %)      │
└─────────────────────────────────────────────────┘
```

### Integration Model

```
Integration Point 1: x402 Market
┌──────────────┐        ┌──────────────┐
│   Agent API  │ wants  │  Agent USDC  │
│              │ to get │   Payment    │
└──────────────┘        └──────────────┘
                              ↓
                    x402 Market receives request
                              ↓
                    Calls AgentFICO API
                              ↓
                    ┌──────────────────────┐
                    │ AgentFICO Response:  │
                    │ Score: 750           │
                    │ Risk: Medium         │
                    │ Fee: 1% (not 3%)     │
                    └──────────────────────┘
                              ↓
                    x402 adjusts payment terms
                    Payment processed

Integration Point 2: ERC-8004 Reputation Registry
┌──────────────┐        ┌──────────────┐
│  Agent Data  │        │ ERC-8004     │
│ (on-chain)   │ ----→  │ Reputation   │
│              │        │ Registry     │
└──────────────┘        └──────────────┘
         ↓                      ↓
    AgentFICO ←────────────────┘
  (reads & writes)
```

---

## 🎯 Product Features (MVP Scope)

### Phase 1 (MVP): Core Scoring

#### Feature 1: Real-Time Agent Scoring
- **Description:** Query current trust score for any ERC-8004 agent
- **Input:** `agent_id` (address or UUID)
- **Output:** Score (0-1000), Risk Level (High/Medium/Low), Timestamp
- **Update Frequency:** Real-time (update within 5 minutes of new data)
- **Use Case:** "Is this agent safe to do business with?"

#### Feature 2: Risk Assessment for Transactions
- **Description:** Assess risk for a specific transaction (amount, protocol, time)
- **Input:** `agent_id`, `amount` (USDC), `protocol_type` (lending/marketplace/payment), `time_window` (24h/7d/30d)
- **Output:** Risk Level, Recommended Fee (%), Recommended Collateral (%), Suggested Limit
- **Use Case:** "What terms should I apply to this agent's payment?"

#### Feature 3: Score Breakdown
- **Description:** Get detailed breakdown of score by the 5 dimensions
- **Input:** `agent_id`
- **Output:** Performance (0-100), Reliability (0-100), Security (0-100), Compliance (0-100), Financial Behavior (0-100)
- **Use Case:** "Why is this agent's score 600? Where are the weaknesses?"

#### Feature 4: Historical Score Tracking
- **Description:** View score history over time
- **Input:** `agent_id`, `time_range` (7d/30d/90d/all)
- **Output:** List of scores + change reasons
- **Use Case:** "Is this agent improving or degrading over time?"

### Phase 2 (Later): Enhanced Features
- [ ] Batch scoring (score 100+ agents in one call)
- [ ] Webhooks (notify on score changes)
- [ ] Custom scoring models (partner-specific weights)
- [ ] Predictive scoring (predict future risk)

---

## 🔧 Technical Specification

### 1. Score Model Specification

#### 5-Dimension Model

| Dimension | Weight | Data Source | Formula | Range |
|-----------|--------|-------------|---------|-------|
| **Performance** | 25% | On-chain success rate, MCP logs | `(successful_tasks / total_tasks) * 100` | 0-100 |
| **Reliability** | 25% | API uptime, response time consistency | `(uptime_hours / total_hours) * 100` | 0-100 |
| **Security** | 20% | Security audits, exploit history | `base_100 - (exploits * 10)` | 0-100 |
| **Compliance** | 15% | Regulatory status, audit trail | Checklist-based (boolean factors) | 0-100 |
| **Financial Behavior** | 15% | Transaction history, repayment rate | `(repaid / borrowed) * 100` | 0-100 |

**Final Score Calculation:**
```
AgentScore = 
  (Performance * 0.25) +
  (Reliability * 0.25) +
  (Security * 0.20) +
  (Compliance * 0.15) +
  (FinancialBehavior * 0.15)

Result: 0-1000 (scale by 10 for display)
```

#### Risk Level Mapping

| Score Range | Risk Level | Recommended Action |
|-------------|------------|-------------------|
| 0-250 | 🔴 High | Reject or require collateral |
| 250-750 | 🟡 Medium | Normal terms (1-2% fee) |
| 750-1000 | 🟢 Low | Preferred terms (0.5% fee) |

#### Data Sources (10+)

1. **On-Chain (Primary)**
   - Etherscan API: Transaction history, contract interactions
   - RPC Endpoint: Smart contract state, event logs
   - ERC-8004 Registry: Agent metadata, identity claims

2. **Off-Chain (Secondary)**
   - MCP Tool Call Logs: Task completion rates
   - x402 Market: Payment success history
   - 3rd Party APIs: Agent reputation (Trusta, Wach, etc)

3. **Community (Tertiary)**
   - ERC-8004 Reputation Registry: Community feedback
   - Twitter/Discord: Agent team activity
   - GitHub: Code commits, updates

### 2. API Specification

#### Authentication

```
Authorization: Bearer {API_KEY}
X-API-Signature: {HMAC_SHA256(request_body, secret)}
```

#### Endpoint 1: `GET /v1/agent/{agent_id}/score`

**Description:** Get current score for an agent

**Request:**
```bash
curl -X GET "https://api.agentfico.com/v1/agent/0x123abc/score" \
  -H "Authorization: Bearer sk_live_..."
```

**Query Parameters:**
```json
{
  "include_breakdown": true,      // Optional: Include dimension breakdown
  "include_history": false,        // Optional: Include score history
  "history_window": "30d"          // Optional: 7d, 30d, 90d
}
```

**Response (200 OK):**
```json
{
  "agent_id": "0x123abc...",
  "score": 750,
  "risk_level": "medium",
  "confidence": 92,
  "last_updated": "2026-01-29T14:32:00Z",
  "expires_at": "2026-04-29T14:32:00Z",
  "breakdown": {
    "performance": {
      "value": 85,
      "weight": 0.25,
      "weighted_score": 21.25
    },
    "reliability": {
      "value": 72,
      "weight": 0.25,
      "weighted_score": 18.0
    },
    "security": {
      "value": 90,
      "weight": 0.20,
      "weighted_score": 18.0
    },
    "compliance": {
      "value": 60,
      "weight": 0.15,
      "weighted_score": 9.0
    },
    "financial_behavior": {
      "value": 65,
      "weight": 0.15,
      "weighted_score": 9.75
    }
  },
  "history": [
    {
      "score": 740,
      "timestamp": "2026-01-28T14:32:00Z",
      "reason": "transaction_success"
    },
    {
      "score": 730,
      "timestamp": "2026-01-27T14:32:00Z",
      "reason": "no_activity_penalty"
    }
  ]
}
```

**Response (404 Not Found):**
```json
{
  "error": "agent_not_found",
  "message": "Agent 0x123abc not registered on ERC-8004",
  "status": 404
}
```

#### Endpoint 2: `POST /v1/agent/{agent_id}/risk-assessment`

**Description:** Assess risk for a specific transaction

**Request:**
```bash
curl -X POST "https://api.agentfico.com/v1/agent/0x123abc/risk-assessment" \
  -H "Authorization: Bearer sk_live_..." \
  -H "Content-Type: application/json" \
  -d '{
    "amount_usdc": 100000,
    "protocol_type": "lending",
    "time_window": "24h"
  }'
```

**Request Body:**
```json
{
  "amount_usdc": 100000,           // USDC amount
  "protocol_type": "lending",      // lending | marketplace | payment
  "time_window": "24h",            // 24h | 7d | 30d | all
  "collateral_available": true,    // Optional
  "agent_track_record": "known"    // Optional: known | new
}
```

**Response (200 OK):**
```json
{
  "agent_id": "0x123abc...",
  "score": 750,
  "risk_level": "medium",
  "transaction": {
    "amount_usdc": 100000,
    "protocol_type": "lending",
    "time_window": "24h",
    "assessed_at": "2026-01-29T14:32:00Z"
  },
  "risk_assessment": {
    "risk_score": "medium",
    "likelihood_default": 0.15,       // 15% default probability
    "expected_loss": 15000,           // 15% of 100K
    "recommended_fee_percent": 2.0,   // 2% transaction fee
    "recommended_collateral_percent": 150,  // 150% collateral required
    "suggested_limit_usdc": 250000,   // Max amount to transact
    "confidence": 88
  }
}
```

#### Endpoint 3: `GET /v1/agent/{agent_id}/breakdown`

(Similar to above, returns only dimensional breakdown)

### 3. Data Model & Database Schema

**Agent Table:**
```sql
CREATE TABLE agents (
  agent_id UUID PRIMARY KEY,
  erc8004_address VARCHAR(42) UNIQUE,
  owner_wallet VARCHAR(42),
  name VARCHAR(255),
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_updated TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true,
  metadata JSONB
);
```

**Score Table:**
```sql
CREATE TABLE scores (
  score_id UUID PRIMARY KEY,
  agent_id UUID REFERENCES agents(agent_id),
  overall_score INT CHECK (overall_score >= 0 AND overall_score <= 1000),
  performance INT,
  reliability INT,
  security INT,
  compliance INT,
  financial_behavior INT,
  risk_level VARCHAR(20),
  confidence INT,
  calculated_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP,
  data_sources JSONB
);

CREATE INDEX idx_scores_agent_id ON scores(agent_id);
CREATE INDEX idx_scores_calculated_at ON scores(calculated_at DESC);
```

**AuditLog Table:**
```sql
CREATE TABLE audit_logs (
  log_id UUID PRIMARY KEY,
  api_key_id UUID,
  action VARCHAR(255),
  agent_id UUID REFERENCES agents(agent_id),
  timestamp TIMESTAMP DEFAULT NOW(),
  ip_address VARCHAR(45),
  details JSONB,
  status_code INT
);
```

### 4. Architecture & System Design

**High-Level System Diagram:**

```
┌──────────────────────────────────────────────────────────┐
│                      Clients                              │
│  (x402 Market, DeFi Protocols, Agent Platforms)          │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                   API Gateway (Kong)                      │
│  • Authentication (API Key, Web3 Signature)              │
│  • Rate Limiting (1000 req/min per key)                  │
│  • Request Logging                                        │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│                  API Server (FastAPI)                     │
│  ├─ GET /v1/agent/:id/score                              │
│  ├─ POST /v1/agent/:id/risk-assessment                   │
│  └─ GET /v1/agent/:id/breakdown                          │
└──────────────────────────────────────────────────────────┘
                    ↙          ↓        ↖
        ┌────────────┐   ┌──────────┐   ┌──────────┐
        │ Score Calc │   │ Cache    │   │ Audit    │
        │ Engine     │   │ (Redis)  │   │ Logger   │
        └────────────┘   └──────────┘   └──────────┘
                ↓               ↓
        ┌────────────────────────────┐
        │   PostgreSQL Database      │
        │  (Agents, Scores, Audit)   │
        └────────────────────────────┘
                ↓
        ┌────────────────────────────┐
        │    Data Pipeline           │
        │  (Hourly Score Updates)    │
        └────────────────────────────┘
                ↓         ↓        ↓
            ┌────────┬────────┬────────┐
            │Etherscan│MCP   │ 3rd    │
            │ API    │ Logs  │ Party  │
            │        │       │ APIs   │
            └────────┴────────┴────────┘
                ↓
        ┌────────────────────────────┐
        │   ERC-8004 Registry        │
        │  (Read Agent Data)         │
        └────────────────────────────┘
```

---

## 📊 Success Metrics & Acceptance Criteria

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **API Uptime** | 99.9% | CloudWatch monitoring |
| **Latency (p50)** | <50ms | APM (New Relic) |
| **Latency (p99)** | <200ms | APM (New Relic) |
| **Score Accuracy** | >85% | Backtesting on 600 agents |
| **Data Freshness** | <5 min | Event-driven updates |

### Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Integrated Protocols** | 5+ | Partner contracts signed |
| **Daily API Calls** | 100K+ | API dashboard |
| **Customer Acquisition Cost** | <$5K | Salesforce tracking |
| **Monthly Recurring Revenue** | $25K+ | Stripe reporting |

### Product Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Score Stability** | <5% monthly change | Score history analysis |
| **False Positive Rate** | <5% | Manual audit of flagged agents |
| **Feature Usage** | >70% of endpoints | API analytics |

---

## ⚙️ Technical Dependencies & Risks

### Dependencies

| Dependency | Status | Risk |
|------------|--------|------|
| **ERC-8004 Mainnet** | Launching Jan 30, 2026 | 🟢 Low - Public launch scheduled |
| **x402 Market** | Live | 🟢 Low - Already operational |
| **Etherscan API** | Stable | 🟢 Low - Reliable service |
| **Data Availability** | TBD | 🟡 Medium - Depends on agent onboarding |

### Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| **Low agent adoption** | Can't score agents | 🟡 Medium | Seed data with synthetic agents, partner directly with platforms |
| **Data quality issues** | Inaccurate scores | 🟡 Medium | Manual audits, backtesting, feedback loops |
| **x402 integration delays** | Reduced go-to-market | 🟡 Medium | Build generic payment integration first |
| **Regulatory changes** | Compliance burden | 🟡 Medium | Engage legal team early, include compliance dimension |

---

## 🚀 Rollout Plan

### Phase 1: MVP Launch (Q2 2026)

**Timeline:** April-June 2026

**Scope:**
- Core 3 APIs (getScore, getBreakdown, getRiskLevel)
- 5-dimension scoring model
- Testnet deployment (Sepolia)
- 5 alpha partners

**Success Criteria:**
- [ ] All 3 APIs deployed and tested
- [ ] Score accuracy >80% on backtesting
- [ ] 5 partners integrated and testing
- [ ] <100ms latency achieved

### Phase 2: Mainnet Launch (Q3 2026)

**Timeline:** July-September 2026

**Scope:**
- Mainnet deployment
- ERC-8004 Reputation Registry integration
- x402 Market integration
- Public launch announcement

**Success Criteria:**
- [ ] 99.9% uptime SLA met
- [ ] 100K+ daily API calls
- [ ] 10+ paying customers

### Phase 3: Expansion (Q4 2026 - Q1 2027)

**Scope:**
- Batch scoring API
- Webhooks
- Predictive scoring (ML models)
- Agent BNPL module

---

## 📋 Open Questions for Product Review

**Before greenlight, need clarity on:**

1. **Score Calculation:**
   - [ ] Confirm 5 dimensions + weights
   - [ ] Confirm 0-1000 range vs 0-100
   - [ ] Specify data freshness requirement (real-time vs hourly)

2. **MVP Scope:**
   - [ ] Confirm 3 APIs is sufficient or add more?
   - [ ] Include batch scoring in MVP?
   - [ ] Include webhooks in MVP?

3. **Partnerships:**
   - [ ] Which 3-5 protocols/platforms target first?
   - [ ] Any existing relationships to leverage?

4. **Timeline:**
   - [ ] Q2 2026 realistic for MVP launch?
   - [ ] Resources allocated?

5. **Infrastructure:**
   - [ ] Preferred cloud provider (AWS, GCP)?
   - [ ] Budget for infrastructure?

---

## 🔗 Related Documents

- `architecture.md` - Detailed system design
- `score-model.md` - In-depth scoring methodology
- `api-reference.md` - Full API documentation
- `integration-guide.md` - Partner integration guide
- `security-compliance.md` - Security & compliance specifications
- `data-model.md` - Database schema & entity relationships

---

## 📝 Sign-Off

| Role | Name | Date | Status |
|------|------|------|--------|
| **Product Manager** | [TBD] | - | ⏳ Pending |
| **Tech Lead** | [TBD] | - | ⏳ Pending |
| **Security Lead** | [TBD] | - | ⏳ Pending |
| **CEO/Founder** | [TBD] | - | ⏳ Pending |

---

**Next Step:** Schedule PRD review meeting with stakeholders ➜
