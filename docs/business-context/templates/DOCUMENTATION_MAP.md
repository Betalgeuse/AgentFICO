# AgentFICO 문서화 로드맵

**작성일:** 2026-01-29  
**상태:** 초기 계획 단계  
**다음 마일스톤:** ERC-8004 메인넷 (2026-01-30)

---

## 📚 문서 체계

```
AgentFICO 문서 구조 (우선순위 순)

┌─────────────────────────────────────────────────────────────┐
│                    TIER 1: CRITICAL (즉시 필요)              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 🔴 Technical PRD (Product Requirements Document)         │
│     └─ 기술 스펙, API 설계, 데이터 모델                      │
│                                                              │
│  2. 🔴 Architecture & System Design                          │
│     └─ High-level 시스템 구조, 컴포넌트 다이어그램          │
│                                                              │
│  3. 🔴 Score Model Specification                            │
│     └─ 점수 계산 알고리즘, 가중치, 데이터 소스              │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                 TIER 2: HIGH (1-2주 내 필요)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  4. 🟠 API Reference Documentation                          │
│     └─ REST API 스펙, 엔드포인트, 요청/응답 예시             │
│                                                              │
│  5. 🟠 Integration Guide (x402, ERC-8004)                   │
│     └─ 파트너 연동 방식, 코드 예시                           │
│                                                              │
│  6. 🟠 Security & Compliance Spec                           │
│     └─ 인증, 암호화, 감시, 규제 고려사항                     │
│                                                              │
│  7. 🟠 Data Model & Schema                                  │
│     └─ Database schema, Entity relationships                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              TIER 3: MEDIUM (2-4주 내 필요)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  8. 🟡 Deployment & Operations Guide                        │
│     └─ 배포 체크리스트, 모니터링, 스케일링 전략              │
│                                                              │
│  9. 🟡 Testing & QA Strategy                                │
│     └─ 테스트 계획, 백테스팅 방법론, 검증 프레임워크        │
│                                                              │
│  10. 🟡 Partner Onboarding Documentation                    │
│      └─ 파트너 가이드, SDK 사용법, 통합 샘플               │
│                                                              │
│  11. 🟡 Business Model & Pricing                            │
│      └─ 수수료 구조, SLA, 계약 템플릿                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│             TIER 4: NICE-TO-HAVE (1개월 후)                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  12. 🔵 User Documentation & Tutorials                      │
│      └─ 사용자 가이드, 튜토리얼, FAQ                        │
│                                                              │
│  13. 🔵 Research & Benchmarking                             │
│      └─ 경쟁자 분석, 시장 데이터, 성능 비교                  │
│                                                              │
│  14. 🔵 Roadmap & Quarterly Plans                           │
│      └─ 장기 비전, 분기별 계획, 릴리스 노트                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 TIER 1: Critical Documents (우선순위 1순위)

### 1. Technical PRD (Product Requirements Document)

**파일:** `technical-prd.md`

**포함 항목:**
```
├─ Executive Summary
│  └─ 1줄 정의, 목표, 출시 일정
│
├─ Problem Statement
│  └─ x402/ERC-8004 context에서의 문제
│
├─ Solution Overview
│  ├─ AgentFICO Score API
│  ├─ 5-Dimension Model
│  └─ Integration with x402/ERC-8004
│
├─ Product Features (MVP)
│  ├─ 3 Core APIs: getScore, getBreakdown, getRiskLevel
│  ├─ Real-time Score Updates
│  ├─ ERC-8004 Integration
│  └─ x402 Pre-payment Verification
│
├─ Technical Specifications
│  ├─ API Endpoints (request/response examples)
│  ├─ Data Model (Agent, Score, AuditLog entities)
│  ├─ Score Calculation Logic
│  └─ Database Schema
│
├─ Success Metrics
│  ├─ Technical: API uptime 99.9%, latency <100ms
│  ├─ Business: 5+ integrated protocols by Q2 2026
│  └─ Product: Score accuracy >85% (backtesting)
│
└─ Dependencies & Risks
   ├─ ERC-8004 adoption rate
   ├─ x402 Market growth
   └─ Mitigation strategies
```

**작성자:** Engineering Lead  
**소비자:** 개발팀, 투자자, 파트너

---

### 2. Architecture & System Design

**파일:** `architecture.md`

**포함 항목:**
```
├─ System Architecture Diagram
│  ├─ Frontend (API Gateway)
│  ├─ Backend (Score Engine, Data Pipeline)
│  ├─ Blockchain Layer (ERC-8004, x402)
│  └─ Data Layer (PostgreSQL, Redis)
│
├─ Component Design
│  ├─ Score Calculation Engine
│  ├─ Data Aggregation Service
│  ├─ API Server
│  ├─ Blockchain Listener
│  └─ Monitoring & Alerting
│
├─ Data Flow Diagram
│  ├─ Input: On-chain transactions, MCP calls, 3rd party data
│  ├─ Processing: Score calculation, normalization, weighting
│  └─ Output: API response, Reputation Registry update, Audit log
│
├─ Technology Stack
│  ├─ Language: Python/Go
│  ├─ Framework: FastAPI/Go-Gin
│  ├─ Database: PostgreSQL
│  ├─ Cache: Redis
│  ├─ Blockchain: Web3.py, Ethers.js
│  └─ Deployment: Docker, Kubernetes
│
├─ Security Architecture
│  ├─ API Authentication (OAuth 2.0 / Web3 signatures)
│  ├─ Data Encryption (TLS, database encryption at rest)
│  ├─ Rate Limiting (Redis-based)
│  └─ Audit Logging (immutable)
│
└─ Scalability Strategy
   ├─ Horizontal scaling (API servers, worker nodes)
   ├─ Database optimization (indexing, partitioning)
   ├─ Caching strategy (Redis, CDN)
   └─ Load balancing (NGINX, HAProxy)
```

**작성자:** Architect  
**소비자:** 개발팀, DevOps

---

### 3. Score Model Specification

**파일:** `score-model.md`

**포함 항목:**
```
├─ Score Overview
│  ├─ Range: 0-1000 (또는 0-100)
│  ├─ Interpretation: 0-250 (High Risk), 250-750 (Medium), 750-1000 (Low Risk)
│  └─ Update Frequency: Real-time / Hourly / Daily
│
├─ 5-Dimension Model
│  ├─ 1. Performance (가중치: 25%)
│  │  ├─ 정의: Task completion rate, execution success
│  │  ├─ 데이터: On-chain transaction success rate, MCP tool call success
│  │  └─ 계산식: (successful_tasks / total_tasks) * 100
│  │
│  ├─ 2. Reliability (가중치: 25%)
│  │  ├─ 정의: Response time consistency, uptime
│  │  ├─ 데이터: API response times, service availability logs
│  │  └─ 계산식: (uptime_hours / total_hours) * 100
│  │
│  ├─ 3. Security (가중치: 20%)
│  │  ├─ 정의: No security incidents, audits passed
│  │  ├─ 데이터: Security audit reports, exploit history
│  │  └─ 계산식: Base 100 - incident_penalties
│  │
│  ├─ 4. Compliance (가중치: 15%)
│  │  ├─ 정의: Regulatory adherence, KYC/AML status
│  │  ├─ 데이터: Legal compliance checks, regulatory status
│  │  └─ 계산식: Compliance checklist score
│  │
│  └─ 5. Financial Behavior (가중치: 15%)
│     ├─ 정의: Transaction volume, repayment history
│     ├─ 데이터: Historical transactions, default rates
│     └─ 계산식: (repaid_amount / total_borrowed) * 100
│
├─ Data Sources (10+)
│  ├─ On-chain: Etherscan API, RPC endpoints
│  ├─ Off-chain: MCP tool call logs, 3rd party APIs
│  ├─ Community: ERC-8004 Reputation Registry
│  └─ Internal: Historical transactions
│
├─ Score Calculation Pipeline
│  ├─ Step 1: Data collection (hourly)
│  ├─ Step 2: Data normalization (0-100 scale per dimension)
│  ├─ Step 3: Weight application (multiply by factor)
│  ├─ Step 4: Final score aggregation (sum of weighted scores)
│  └─ Step 5: Update Reputation Registry
│
├─ Backtesting & Validation
│  ├─ Historical data: Last 6 months of 600 agents
│  ├─ Accuracy metric: Precision, Recall, F1-score
│  ├─ Comparison: vs manual audits, vs Bond.Credit scores
│  └─ Target: >85% accuracy
│
└─ Score Decay & Updates
   ├─ Inactive agents: Score decreases after 30 days
   ├─ Major incidents: Immediate score penalties
   └─ Positive behavior: Score increases with consistency
```

**작성자:** Data Science / Product  
**소비자:** 개발팀, 투자자, 파트너

---

## 📋 TIER 2: High Priority Documents (1-2주 내)

### 4. API Reference Documentation

**파일:** `api-reference.md`

**포함 항목:**
```
├─ Authentication
│  ├─ API Key: curl -H "Authorization: Bearer YOUR_API_KEY"
│  ├─ Web3 Signature: Sign message with wallet
│  └─ Rate Limits: 1000 req/min (free), unlimited (paid)
│
├─ Endpoint 1: GET /agent/:agent_id/score
│  ├─ Description: Get current score for an agent
│  ├─ Request:
│  │  ├─ Path: agent_id (0x... or uuid)
│  │  └─ Query: include_breakdown (bool), include_history (bool)
│  ├─ Response 200:
│  │  ├─ score (number: 0-1000)
│  │  ├─ risk_level (string: high/medium/low)
│  │  ├─ last_updated (timestamp)
│  │  └─ confidence (number: 0-100)
│  ├─ Response 404: Agent not found
│  └─ Example cURL: ...
│
├─ Endpoint 2: GET /agent/:agent_id/breakdown
│  ├─ Description: Get detailed score breakdown by dimension
│  ├─ Response:
│  │  ├─ performance (25% weight)
│  │  ├─ reliability (25% weight)
│  │  ├─ security (20% weight)
│  │  ├─ compliance (15% weight)
│  │  └─ financial_behavior (15% weight)
│  └─ Example: ...
│
├─ Endpoint 3: POST /agent/:agent_id/risk-level
│  ├─ Description: Assess risk for a transaction
│  ├─ Request:
│  │  ├─ amount (number: USDC)
│  │  ├─ protocol_type (string: lending, marketplace, payment)
│  │  └─ time_window (string: 24h, 7d, 30d)
│  ├─ Response:
│  │  ├─ risk_level (high/medium/low)
│  │  ├─ recommended_fee (number: %)
│  │  ├─ recommended_collateral (number: %)
│  │  └─ suggested_limit (number: USDC)
│  └─ Example: ...
│
├─ Webhooks (Optional)
│  ├─ Event: score_updated
│  ├─ Event: risk_alert (score drops >10%)
│  └─ Delivery: HTTPS POST with signature verification
│
├─ Error Codes
│  ├─ 400: Bad Request
│  ├─ 401: Unauthorized
│  ├─ 404: Not Found
│  ├─ 429: Rate Limited
│  └─ 500: Server Error
│
└─ SDK Examples
   ├─ Python: pip install agentfico
   ├─ JavaScript: npm install agentfico
   └─ Go: go get github.com/agentfico/go-client
```

**작성자:** API Designer  
**소비자:** 개발자, 파트너 엔지니어

---

### 5. Integration Guide (x402, ERC-8004)

**파일:** `integration-guide.md`

**포함 항목:**
```
├─ x402 Integration
│  ├─ Use Case: Verify agent credibility before payment
│  ├─ Flow:
│  │  ├─ 1. User initiates x402 payment to Agent API
│  │  ├─ 2. x402 Market calls AgentFICO /risk-level
│  │  ├─ 3. AgentFICO returns risk assessment
│  │  ├─ 4. x402 adjusts fee/collateral based on score
│  │  └─ 5. Payment proceeds with terms
│  │
│  ├─ Code Example (Python):
│  │  ```python
│  │  from agentfico import AgentFICO
│  │  
│  │  client = AgentFICO(api_key="YOUR_KEY")
│  │  risk = client.assess_risk(
│  │      agent_id="0x123...",
│  │      amount=100,  # USDC
│  │      protocol="x402_market"
│  │  )
│  │  if risk.risk_level == "high":
│  │      fee = risk.recommended_fee  # 5% vs 1%
│  │  ```
│  │
│  └─ x402 Adapter: Deploy middleware for automatic integration
│
├─ ERC-8004 Integration
│  ├─ Read: Query Reputation Registry for agent data
│  ├─ Write: Record AgentFICO score in Reputation Registry
│  ├─ Contract Address: 0x... (post-mainnet)
│  ├─ ABI: Link to ERC-8004 standard
│  └─ Code Example:
│     ```python
│     from web3 import Web3
│     
│     erc8004 = Web3(provider).eth.contract(
│         address="0x...", abi=ERC_8004_ABI
│     )
│     # Read agent reputation
│     rep = erc8004.functions.getReputation(agent_id).call()
│     # Write our score
│     erc8004.functions.setScore(agent_id, score).transact()
│     ```
│
├─ Webhook Integration
│  ├─ Receive ERC-8004 Reputation updates
│  ├─ Update our internal score when external data changes
│  └─ Example: Handle new on-chain transaction
│
├─ Testing in Testnet
│  ├─ Deploy to Sepolia
│  ├─ Test with 10 mock agents
│  ├─ Verify score calculations
│  └─ Load test with 1000 concurrent requests
│
└─ Production Checklist
   ├─ [ ] Mainnet contract addresses confirmed
   ├─ [ ] Security audit passed
   ├─ [ ] Rate limiting configured
   ├─ [ ] Monitoring alerts set up
   └─ [ ] 24/7 support ready
```

**작성자:** Integration Engineer  
**소비자:** 파트너 팀, 개발팀

---

### 6. Security & Compliance Spec

**파일:** `security-compliance.md`

**포함 항목:**
```
├─ Authentication & Authorization
│  ├─ API Keys: Rotate every 90 days
│  ├─ OAuth 2.0: Support for partner integrations
│  ├─ Web3 Signatures: Sign with agent wallet
│  └─ Role-Based Access: Admin, Partner, Public
│
├─ Data Security
│  ├─ Encryption in Transit: TLS 1.3+
│  ├─ Encryption at Rest: AES-256
│  ├─ Database: PostgreSQL with encryption
│  ├─ Secrets Management: Vault (HashiCorp)
│  └─ PII: No personal data collected
│
├─ Rate Limiting & DDoS
│  ├─ Per-IP: 100 req/min
│  ├─ Per-API-Key: 1000 req/min
│  ├─ Burst allowance: 10 req/sec
│  ├─ DDoS Protection: Cloudflare
│  └─ Geo-blocking: Optional
│
├─ Audit & Logging
│  ├─ All API calls logged (request, response, user)
│  ├─ Retention: 90 days hot, 1 year cold
│  ├─ Immutable logs: Append-only
│  ├─ Log access: Restricted to admins
│  └─ Export: SIEM integration (Splunk)
│
├─ Compliance
│  ├─ Data Privacy: GDPR-compliant (no PII)
│  ├─ Financial Compliance: Check with legal (SOX equivalent)
│  ├─ Web3 Compliance: Smart contract audit
│  ├─ Terms of Service: Clear API usage terms
│  └─ SLA: 99.9% uptime, <100ms latency
│
├─ Incident Response
│  ├─ Breach notification: 24 hours to affected users
│  ├─ On-call rotation: 24/7 support
│  ├─ Post-incident report: Within 72 hours
│  └─ Recovery RTO: <1 hour
│
└─ Security Testing
   ├─ Penetration testing: Quarterly
   ├─ OWASP Top 10 review: Before each release
   ├─ Dependency scanning: Weekly (Snyk)
   └─ Code review: Mandatory (GitHub Actions)
```

**작성자:** Security Lead / Legal  
**소비자:** 개발팀, 투자자, 파트너

---

### 7. Data Model & Schema

**파일:** `data-model.md`

**포함 항목:**
```
├─ Entity: Agent
│  ├─ agent_id (UUID or ERC-8004 address)
│  ├─ owner_wallet (0x... Ethereum address)
│  ├─ name (string)
│  ├─ description (text)
│  ├─ created_at (timestamp)
│  ├─ last_updated (timestamp)
│  └─ is_active (bool)
│
├─ Entity: Score
│  ├─ score_id (UUID)
│  ├─ agent_id (FK to Agent)
│  ├─ score (number: 0-1000)
│  ├─ risk_level (enum: high/medium/low)
│  ├─ performance (0-100)
│  ├─ reliability (0-100)
│  ├─ security (0-100)
│  ├─ compliance (0-100)
│  ├─ financial_behavior (0-100)
│  ├─ confidence (0-100)
│  ├─ calculated_at (timestamp)
│  └─ expires_at (timestamp: 90 days)
│
├─ Entity: ScoreHistory
│  ├─ history_id (UUID)
│  ├─ agent_id (FK to Agent)
│  ├─ score_before (number)
│  ├─ score_after (number)
│  ├─ change_reason (string)
│  └─ timestamp (timestamp)
│
├─ Entity: DataSource
│  ├─ source_id (UUID)
│  ├─ agent_id (FK to Agent)
│  ├─ source_type (enum: on_chain, mcp_logs, 3rd_party)
│  ├─ source_name (string)
│  ├─ data_point (JSON)
│  ├─ weight (number: 0-1)
│  └─ last_sync (timestamp)
│
├─ Entity: AuditLog
│  ├─ log_id (UUID)
│  ├─ user_id (string or wallet)
│  ├─ action (string: read_score, request_assessment, etc)
│  ├─ agent_id (FK to Agent)
│  ├─ timestamp (timestamp)
│  ├─ ip_address (string)
│  └─ details (JSON)
│
├─ Entity: APIKey
│  ├─ key_id (UUID)
│  ├─ key_hash (string: hashed)
│  ├─ partner_id (string)
│  ├─ rate_limit (number: req/min)
│  ├─ created_at (timestamp)
│  ├─ expires_at (timestamp)
│  └─ is_active (bool)
│
└─ Relationships
   ├─ Agent 1:N Score
   ├─ Agent 1:N ScoreHistory
   ├─ Agent 1:N DataSource
   ├─ Agent 1:N AuditLog
   └─ Partner 1:N APIKey
```

**작성자:** Database Architect  
**소비자:** 개발팀, DBA

---

## 📋 TIER 3: Medium Priority Documents (2-4주 내)

### 8. Deployment & Operations Guide

**파일:** `deployment-operations.md`

```
├─ Pre-Deployment Checklist
├─ Infrastructure Setup (AWS/GCP)
├─ Database Migration
├─ Monitoring & Alerting Setup
├─ Backup & Disaster Recovery
├─ Scaling Strategy
└─ On-Call Runbook
```

---

### 9. Testing & QA Strategy

**파일:** `testing-qa.md`

```
├─ Unit Testing (>80% coverage)
├─ Integration Testing (API + Blockchain)
├─ Backtesting Score Model
├─ Load Testing (5,000 RPS target)
├─ Security Testing
└─ Regression Testing
```

---

### 10. Partner Onboarding Documentation

**파일:** `partner-onboarding.md`

```
├─ Integration Checklist
├─ SDK Installation Guide
├─ Code Examples (Python, JS, Go)
├─ Support SLA
└─ Billing & Reporting
```

---

### 11. Business Model & Pricing

**파일:** `business-model-pricing.md`

```
├─ Pricing Tiers
│  ├─ Free: 1,000 API calls/month
│  ├─ Pro: $500/month (50,000 calls)
│  └─ Enterprise: Custom
│
├─ Revenue Streams
│  ├─ API subscription
│  ├─ x402 transaction fees
│  └─ BNPL interest
│
└─ ACV & Unit Economics
```

---

## 📋 TIER 4: Nice-to-Have Documents (1개월 후)

### 12-14. User Documentation, Research, Roadmap

```
├─ user-guide.md
├─ faq.md
├─ research-report.md
├─ quarterly-roadmap.md
└─ release-notes.md
```

---

## 🎯 문서 작성 우선순위 (실행 계획)

```
Week 1 (Jan 30 - Feb 5):
  Day 1: Technical PRD 초안
  Day 2: Architecture diagram 작성
  Day 3: Score Model 상세 정의
  Day 4-5: API Reference 작성
  
Week 2-3 (Feb 6 - Feb 19):
  Integration Guide, Security Spec 작성
  Data Model 정의, 첫 번째 리뷰
  
Week 4+ (Feb 20+):
  Deployment Guide, Testing Strategy
  Partner Onboarding, Pricing Model

```

---

## 📝 문서 소비자별 가이드

| 역할 | 꼭 읽어야 할 문서 | 선택 읽기 |
|------|-----------------|----------|
| **개발자** | Technical PRD, API Reference, Architecture | Data Model, Security |
| **파트너** | Integration Guide, API Reference, Onboarding | Technical PRD |
| **투자자** | Technical PRD, Business Model, Roadmap | Architecture, Security |
| **DevOps** | Deployment Guide, Architecture | Monitoring, Ops |
| **QA** | Testing Strategy, API Reference | Technical PRD |

---

## 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-01-29 | 문서화 로드맵 초기 생성 |
