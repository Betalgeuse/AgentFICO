# AgentFICO 기술 스펙

**목적:** AgentFICO 하이브리드 아키텍처 (API + 블록체인) 상세 설계

**Created:** 2026-01-29

**Status:** 🔧 기술 명세 (MVP)

**Architecture:** Hybrid (REST API + Smart Contract)

---

## 📋 목차

1. [아키텍처 개요](#아키텍처-개요)
2. [시스템 구성](#시스템-구성)
3. [API 명세](#api-명세)
4. [Smart Contract 명세](#smart-contract-명세)
5. [데이터 파이프라인](#데이터-파이프라인)
6. [배포 계획](#배포-계획)
7. [성능 & 보안](#성능--보안)
8. [개발 타임라인](#개발-타임라인)

---

## 🏗️ 아키텍처 개요

### 전체 구조

```
┌──────────────────────────────────────────────────────────┐
│                  AgentFICO Platform                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐         ┌──────────────────────┐  │
│  │  Data Sources   │         │  API Layer (REST)    │  │
│  ├─────────────────┤         ├──────────────────────┤  │
│  │ Etherscan API   │         │ GET /score           │  │
│  │ x402 API        │────────→│ POST /assessment     │  │
│  │ ERC-8004        │         │ GET /breakdown       │  │
│  └─────────────────┘         │ GET /history         │  │
│                              └────────┬─────────────┘  │
│                                       │                │
│  ┌──────────────────────────────────┐ │                │
│  │  Score Calculation Engine        │ │                │
│  ├──────────────────────────────────┤ │                │
│  │ • Input Validation               │ │                │
│  │ • Weight Aggregation (40-40-20)  │ │                │
│  │ • Risk Classification            │ │                │
│  │ • Anomaly Detection              │ │                │
│  └────────────┬─────────────────────┘ │                │
│               │                        │                │
│  ┌────────────▼─────────────────────┐ │                │
│  │  Data Storage Layer              │ │                │
│  ├──────────────────────────────────┤ │                │
│  │ PostgreSQL: Historical Scores    │ │                │
│  │ Redis: Cache (Latest Scores)     │ │                │
│  │ IPFS: Breakdown Details (링크)   │ │                │
│  └────────────┬─────────────────────┘ │                │
│               │                        │                │
│  ┌────────────▼─────────────────────┐ │                │
│  │  Batch Job (Daily 00:00 UTC)     │ │                │
│  ├──────────────────────────────────┤ │                │
│  │ 1. Collect Data (600 agents)     │ │                │
│  │ 2. Calculate Scores              │ │                │
│  │ 3. Update PostgreSQL             │ │                │
│  │ 4. Write to Smart Contract       │ │                │
│  └────────────┬─────────────────────┘ │                │
│               │                        │                │
│               └────────┬───────────────┘                │
│                        │                                │
│  ┌─────────────────────▼──────────────────────────┐   │
│  │  Smart Contract (ERC-8004 on Base L2)         │   │
│  ├────────────────────────────────────────────────┤   │
│  │ • AgentFICOScore.sol                          │   │
│  │ • State: mapping(address => Score)            │   │
│  │ • Events: ScoreUpdated, RiskAssessment        │   │
│  │ • Functions: updateScore, getScore, assess    │   │
│  └────────────┬─────────────────────────────────┘   │
│               │                                       │
└───────────────┼───────────────────────────────────────┘
                │
                ↓
        ┌──────────────────────┐
        │  DeFi Integration    │
        ├──────────────────────┤
        │ • Aave (Lending)     │
        │ • Uniswap (Swap)     │
        │ • Curve (Stables)    │
        └──────────────────────┘
                │
        ┌──────────────────────┐
        │  x402 Integration    │
        ├──────────────────────┤
        │ • Fee Adjustment     │
        │ • Agent Ranking      │
        └──────────────────────┘
                │
        ┌──────────────────────┐
        │  Platform Integration│
        ├──────────────────────┤
        │ • HeyElsa (Agents)   │
        │ • Theoriq (Agents)   │
        └──────────────────────┘
```

### 핵심 특징

```
1. 하이브리드 구조
   ├─ 빠른 조회: REST API (매 요청 <100ms)
   └─ 검증 가능: Smart Contract (영구 기록)

2. 자동화
   ├─ 일일 배치: 자동 점수 갱신
   └─ 자동 계약: 점수 기반 자동 실행

3. 확장성
   ├─ 무상태 API: 수평 확장 가능
   ├─ 점수 캐싱: 빠른 응답
   └─ 배치 처리: 효율적 비용

4. 투명성
   ├─ 공개 API: 누구나 조회 가능
   ├─ 온체인 기록: Basescan에서 확인
   └─ 오픈소스: 점수 계산 코드 공개
```

---

## 🔧 시스템 구성

### 1. Backend 서버

```
Framework: FastAPI (Python) / Node.js Express
Language: Python 3.11+ 또는 TypeScript
Runtime: AWS Lambda / EC2 / Railway

주요 모듈:
├─ api_handler.py (REST API)
├─ score_engine.py (점수 계산)
├─ data_collector.py (Etherscan, x402, ERC-8004)
├─ storage.py (DB 접근)
├─ blockchain.py (Smart Contract 연동)
├─ anomaly_detector.py (이상 탐지)
└─ scheduler.py (일일 배치)

Dependencies:
├─ web3.py (블록체인 연동)
├─ requests (API 호출)
├─ sqlalchemy (ORM)
├─ redis-py (캐싱)
├─ pydantic (데이터 검증)
└─ pytest (테스트)
```

### 2. 데이터베이스

```
Primary: PostgreSQL 14+
├─ agents 테이블
│  ├─ address (PK)
│  ├─ name
│  ├─ metadata_url (ERC-8004)
│  └─ created_at
│
├─ scores 테이블
│  ├─ id (PK)
│  ├─ agent_address (FK)
│  ├─ overall_score (0-1000)
│  ├─ tx_success_score (0-100)
│  ├─ x402_profit_score (0-100)
│  ├─ erc8004_stability_score (0-100)
│  ├─ risk_level (high/medium/low)
│  ├─ confidence (0-100)
│  ├─ breakdown_ipfs_hash
│  ├─ calculated_at
│  └─ created_at
│
├─ transactions 테이블
│  ├─ id (PK)
│  ├─ agent_address (FK)
│  ├─ tx_hash (Etherscan)
│  ├─ success (bool)
│  ├─ gas_used
│  ├─ block_number
│  └─ timestamp
│
├─ x402_trades 테이블
│  ├─ id (PK)
│  ├─ agent_address (FK)
│  ├─ trade_id (x402)
│  ├─ amount_usdc
│  ├─ success (bool)
│  ├─ profit_usdc
│  └─ timestamp
│
└─ erc8004_metadata 테이블
   ├─ id (PK)
   ├─ agent_address (FK)
   ├─ name
   ├─ description
   ├─ website
   ├─ verification_level (0-3)
   ├─ reputation_score (0-5)
   └─ updated_at

Cache: Redis
├─ scores:{agent_address} → 현재 점수
├─ tx_data:{agent_address} → 거래 캐시
└─ x402_data:{agent_address} → x402 캐시
```

### 3. Smart Contract (Solidity)

```solidity
// File: AgentFICOScore.sol
// Network: Base (Coinbase L2)
// Chain ID: 8453
// Location: TBD (배포 후 공개)

pragma solidity ^0.8.20;

interface IERC8004 {
    function getAgentMetadata(address agent) external view 
        returns (string memory name, string memory description, string memory website);
}

contract AgentFICOScore {
    
    // ============= Structs =============
    struct Score {
        uint256 overall;            // 0-1000
        uint256 txSuccess;          // 40% weight
        uint256 x402Profitability;  // 40% weight
        uint256 erc8004Stability;   // 20% weight
        uint256 confidence;         // 0-100
        string riskLevel;           // "high", "medium", "low"
        uint256 timestamp;
        string ipfsBreakdown;       // 상세 정보 IPFS 해시
    }
    
    struct RiskAssessment {
        uint256 riskLevel;          // 0-100
        uint256 defaultProbability; // 0-100 (%)
        uint256 expectedLoss;       // USDC
        string[] positiveFactors;
        string[] riskFactors;
    }
    
    // ============= State Variables =============
    address public owner;
    address public erc8004Registry;
    
    mapping(address => Score) public scores;
    mapping(address => Score[]) public scoreHistory;
    mapping(address => uint256) public lastUpdate;
    
    uint256 public constant MAX_AGENTS = 10000;
    uint256 public totalAgents;
    
    // ============= Events =============
    event ScoreUpdated(
        indexed address agent,
        uint256 overall,
        uint256 timestamp
    );
    
    event RiskAssessmentRequested(
        indexed address agent,
        uint256 amount,
        string protocolType
    );
    
    event ScoreBreakdownRecorded(
        indexed address agent,
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score
    );
    
    // ============= Constructor =============
    constructor(address _erc8004Registry) {
        owner = msg.sender;
        erc8004Registry = _erc8004Registry;
    }
    
    // ============= Main Functions =============
    
    /// @notice Update agent score (called daily by backend)
    /// @param agent Agent address
    /// @param txScore Transaction success score (0-100)
    /// @param x402Score x402 profitability score (0-100)
    /// @param erc8004Score ERC-8004 stability score (0-100)
    function updateScore(
        address agent,
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score,
        uint256 confidence,
        string memory riskLevel,
        string memory ipfsHash
    ) external onlyOwner {
        require(agent != address(0), "Invalid agent address");
        require(txScore <= 100 && x402Score <= 100 && erc8004Score <= 100, "Invalid scores");
        require(confidence <= 100, "Invalid confidence");
        
        // Calculate overall score (40-40-20 weighted)
        uint256 overall = (txScore * 40 + x402Score * 40 + erc8004Score * 20) / 100;
        
        // Create score object
        Score memory newScore = Score({
            overall: overall,
            txSuccess: txScore,
            x402Profitability: x402Score,
            erc8004Stability: erc8004Score,
            confidence: confidence,
            riskLevel: riskLevel,
            timestamp: block.timestamp,
            ipfsBreakdown: ipfsHash
        });
        
        // Store current score
        scores[agent] = newScore;
        scoreHistory[agent].push(newScore);
        lastUpdate[agent] = block.timestamp;
        
        // Track total agents (first time)
        if (lastUpdate[agent] == 0) {
            totalAgents++;
        }
        
        emit ScoreUpdated(agent, overall, block.timestamp);
        emit ScoreBreakdownRecorded(agent, txScore, x402Score, erc8004Score);
    }
    
    /// @notice Get current score for agent
    /// @param agent Agent address
    /// @return Current Score struct
    function getScore(address agent) external view returns (Score memory) {
        require(lastUpdate[agent] > 0, "Agent not registered");
        return scores[agent];
    }
    
    /// @notice Get overall score only (optimized for gas)
    /// @param agent Agent address
    /// @return Overall score (0-1000)
    function getScoreOnly(address agent) external view returns (uint256) {
        require(lastUpdate[agent] > 0, "Agent not registered");
        return scores[agent].overall;
    }
    
    /// @notice Get score history for agent
    /// @param agent Agent address
    /// @param limit Number of records to return
    /// @return Array of historical scores
    function getScoreHistory(address agent, uint256 limit) 
        external 
        view 
        returns (Score[] memory) 
    {
        require(lastUpdate[agent] > 0, "Agent not registered");
        
        Score[] storage history = scoreHistory[agent];
        uint256 length = history.length > limit ? limit : history.length;
        
        Score[] memory result = new Score[](length);
        for (uint256 i = 0; i < length; i++) {
            result[i] = history[history.length - 1 - i];
        }
        
        return result;
    }
    
    /// @notice Assess risk for a specific transaction
    /// @param agent Agent address
    /// @param amountUsdc Transaction amount
    /// @param protocolType Type of protocol ("lending", "trading", "payment")
    /// @return Risk assessment
    function assessRisk(
        address agent,
        uint256 amountUsdc,
        string memory protocolType
    ) external view returns (RiskAssessment memory) {
        require(lastUpdate[agent] > 0, "Agent not registered");
        
        Score memory score = scores[agent];
        
        // Risk calculation based on score
        uint256 baseRisk = 100 - score.overall;  // Higher score = lower risk
        
        // Adjust for protocol type
        uint256 protocolMultiplier = 100;
        if (keccak256(bytes(protocolType)) == keccak256(bytes("lending"))) {
            protocolMultiplier = 120;  // Lending is riskier
        } else if (keccak256(bytes(protocolType)) == keccak256(bytes("trading"))) {
            protocolMultiplier = 110;  // Trading is moderate risk
        }
        
        // Final risk level
        uint256 riskLevel = (baseRisk * protocolMultiplier) / 100;
        if (riskLevel > 100) riskLevel = 100;
        
        // Default probability
        uint256 defaultProbability = riskLevel;
        
        // Expected loss calculation
        uint256 expectedLoss = (amountUsdc * defaultProbability) / 100;
        
        // Prepare positive and risk factors
        string[] memory positiveFactors = new string[](3);
        string[] memory riskFactors = new string[](2);
        
        if (score.txSuccess > 80) {
            positiveFactors[0] = "High transaction success rate";
        }
        if (score.x402Profitability > 70) {
            positiveFactors[1] = "Consistent profitability";
        }
        if (score.erc8004Stability > 80) {
            positiveFactors[2] = "Strong ERC-8004 profile";
        }
        
        if (score.txSuccess < 60) {
            riskFactors[0] = "Below average transaction success";
        }
        if (score.x402Profitability < 50) {
            riskFactors[1] = "Weak profitability history";
        }
        
        return RiskAssessment({
            riskLevel: riskLevel,
            defaultProbability: defaultProbability,
            expectedLoss: expectedLoss,
            positiveFactors: positiveFactors,
            riskFactors: riskFactors
        });
    }
    
    /// @notice Check if agent is registered
    /// @param agent Agent address
    /// @return True if agent has at least one score
    function isRegistered(address agent) external view returns (bool) {
        return lastUpdate[agent] > 0;
    }
    
    /// @notice Get total number of agents with scores
    /// @return Total agent count
    function getTotalAgents() external view returns (uint256) {
        return totalAgents;
    }
    
    // ============= Admin Functions =============
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
    
    function updateERC8004Registry(address newRegistry) external onlyOwner {
        require(newRegistry != address(0), "Invalid address");
        erc8004Registry = newRegistry;
    }
}
```

---

## 📡 API 명세

### Base URL

```
Production: https://api.agentfico.com/v1
Staging: https://staging-api.agentfico.com/v1
```

### Authentication

```
모든 요청에 API Key 필요:
Authorization: Bearer sk_live_xxxxxxxxxxxxxxxx

키 타입:
├─ sk_live_* : 프로덕션 키
├─ sk_test_* : 테스트 키
└─ sk_dev_*  : 개발 키
```

### Endpoint 1: GET /agent/{address}/score

```
Request:
GET /agent/0x123abc/score?include_breakdown=true&include_history=true

Query Parameters:
├─ include_breakdown (optional, bool)
│  └─ Default: false
│
├─ include_history (optional, bool)
│  └─ Default: false
│
├─ history_window (optional, string)
│  └─ Values: 7d | 30d | 90d | all
│  └─ Default: 30d

Response (200 OK):
{
  "agent_id": "0x123abc456def...",
  "score": 750,
  "risk_level": "medium",
  "confidence": 92,
  "last_updated": "2026-01-29T00:00:00Z",
  "expires_at": "2026-04-29T00:00:00Z",
  "breakdown": {
    "transaction_success_rate": {
      "value": 85,
      "weight": 0.40,
      "contribution": 34,
      "data_points": {
        "successful_txs": 950,
        "total_txs": 1000,
        "period_days": 30
      }
    },
    "x402_profitability": {
      "value": 72,
      "weight": 0.40,
      "contribution": 28.8,
      "data_points": {
        "total_volume": 150000,
        "profit": 2500,
        "success_rate": 95.0
      }
    },
    "erc8004_stability": {
      "value": 90,
      "weight": 0.20,
      "contribution": 18,
      "data_points": {
        "metadata_complete": true,
        "verification_level": 3,
        "reputation_score": 4.8
      }
    }
  },
  "history": [
    {
      "date": "2026-01-29",
      "score": 750,
      "reason": "daily_update"
    },
    {
      "date": "2026-01-28",
      "score": 745,
      "reason": "transaction_volatility"
    }
  ]
}

Errors:
404 Not Found:
{
  "error": "agent_not_found",
  "message": "Agent not registered",
  "status": 404
}

429 Too Many Requests:
{
  "error": "rate_limit_exceeded",
  "message": "100 requests/min exceeded",
  "retry_after": 60,
  "status": 429
}

Performance:
├─ Latency: <100ms (p99)
├─ Cache: Redis (TTL: 1hour)
└─ Rate Limit: 100 req/min (Free), 1000 req/min (Pro)
```

### Endpoint 2: POST /agent/{address}/risk-assessment

```
Request:
POST /agent/0x123abc/risk-assessment
{
  "amount_usdc": 100000,
  "protocol_type": "lending",
  "time_window": "24h",
  "collateral_available": true
}

Body Parameters:
├─ amount_usdc (required, int)
│  └─ Range: 1 - 10,000,000
│
├─ protocol_type (required, string)
│  └─ Values: "lending" | "trading" | "payment" | "marketplace"
│
├─ time_window (required, string)
│  └─ Values: "24h" | "7d" | "30d"
│
├─ collateral_available (optional, bool)
│  └─ Default: false

Response (200 OK):
{
  "agent_id": "0x123abc...",
  "current_score": 750,
  "assessment": {
    "risk_level": "medium",
    "risk_score": 25,
    "default_probability": 0.15,
    "expected_loss_usdc": 15000,
    "confidence": 88
  },
  "recommendations": {
    "approval_status": "approved",
    "transaction_fee_percent": 2.0,
    "collateral_requirement_percent": 150,
    "maximum_limit_usdc": 250000,
    "suggested_monitoring": "daily",
    "early_warning_threshold": 650
  },
  "reasoning": {
    "positive_factors": [
      "High transaction success rate (85%)",
      "Stable ERC-8004 profile with verification level 3"
    ],
    "risk_factors": [
      "x402 profitability could be higher",
      "Recent transaction volatility detected"
    ]
  },
  "timestamp": "2026-01-29T10:30:00Z"
}

Errors:
400 Bad Request:
{
  "error": "invalid_parameters",
  "message": "amount_usdc must be positive",
  "status": 400
}

Performance:
├─ Latency: <200ms (p99)
├─ No cache (always fresh)
└─ Rate Limit: 100 req/min (Free), 1000 req/min (Pro)
```

### Endpoint 3: GET /agent/{address}/breakdown

```
Request:
GET /agent/0x123abc/breakdown?include_factors=true

Query Parameters:
├─ include_factors (optional, bool)
│  └─ Default: false (detailed factor analysis)

Response (200 OK):
{
  "agent_id": "0x123abc...",
  "overall_score": 750,
  "dimensions": {
    "transaction_success_rate": {
      "score": 85,
      "weight": 0.40,
      "contribution": 34,
      "status": "good",
      "data_points": {
        "successful_txs": 950,
        "total_txs": 1000,
        "success_rate_percent": 95.0,
        "period_days": 30,
        "data_freshness": "real-time"
      },
      "factors": [
        {
          "name": "Execution Success",
          "score": 95,
          "weight": 0.50
        },
        {
          "name": "Gas Efficiency",
          "score": 75,
          "weight": 0.50
        }
      ]
    },
    "x402_profitability": {
      "score": 72,
      "weight": 0.40,
      "contribution": 28.8,
      "status": "acceptable",
      "data_points": {
        "total_volume_usdc": 150000,
        "successful_volume_usdc": 142500,
        "success_rate_percent": 95.0,
        "profit_usdc": 2500,
        "profitability_percent": 1.67,
        "period_days": 7
      },
      "factors": [
        {
          "name": "Payment Success Rate",
          "score": 95,
          "weight": 0.50
        },
        {
          "name": "Profit Margin",
          "score": 48,
          "weight": 0.50
        }
      ]
    },
    "erc8004_stability": {
      "score": 90,
      "weight": 0.20,
      "contribution": 18,
      "status": "excellent",
      "data_points": {
        "metadata_completeness_percent": 100,
        "verification_level": 3,
        "reputation_score": 4.8,
        "reputation_reviews": 45
      },
      "factors": [
        {
          "name": "Profile Completeness",
          "score": 100,
          "weight": 0.50
        },
        {
          "name": "Verification Status",
          "score": 80,
          "weight": 0.50
        }
      ]
    }
  },
  "summary": "Agent has strong execution and profitability. Monitor margin trends.",
  "recommendations": [
    "Increase x402 activity to improve profitability score",
    "Maintain high transaction success rate",
    "Update ERC-8004 metadata to ensure latest information"
  ]
}

Performance:
├─ Latency: <150ms (p99)
├─ Cache: Redis (TTL: 6 hours)
└─ Rate Limit: 100 req/min (Free)
```

### Endpoint 4: GET /agent/{address}/history

```
Request:
GET /agent/0x123abc/history?limit=30&offset=0

Query Parameters:
├─ limit (optional, int)
│  └─ Default: 30, Max: 365
│
├─ offset (optional, int)
│  └─ Default: 0

Response (200 OK):
{
  "agent_id": "0x123abc...",
  "total_count": 45,
  "limit": 30,
  "offset": 0,
  "scores": [
    {
      "date": "2026-01-29",
      "score": 750,
      "tx_success": 85,
      "x402_profit": 72,
      "erc8004_stability": 90,
      "confidence": 92,
      "data_source": "scheduled_update"
    },
    {
      "date": "2026-01-28",
      "score": 745,
      "tx_success": 84,
      "x402_profit": 71,
      "erc8004_stability": 90,
      "confidence": 91,
      "data_source": "scheduled_update"
    }
  ]
}

Performance:
├─ Latency: <200ms (p99)
├─ No cache
└─ Rate Limit: 100 req/min
```

---

## 🔗 Smart Contract 명세

### Deployment 정보

```
Network: Base (Coinbase L2)
Chain ID: 8453
RPC: https://mainnet.base.org
Explorer: https://basescan.org
EVM Version: Istanbul (safe)
Compiler: Solidity ^0.8.20

Gas Estimate (L2 기준):
├─ Deploy: ~3.5M gas (~$0.50-1.00)
├─ updateScore: ~80K-150K gas (~$0.01-0.05/tx)

Functions Cost (USD, Base L2):
├─ updateScore: ~$0.01-0.05 (vs Ethereum $3-10)
├─ getScore: Free (read-only)
├─ getScoreOnly: Free (read-only)
├─ assessRisk: Free (read-only)
└─ getScoreHistory: Free (read-only)

월간 예상 비용 (600 agents 기준):
├─ Ethereum Mainnet: $100-300/월
└─ Base L2: $1-5/월 (97% 절감)
```

### Events

```solidity
event ScoreUpdated(indexed address agent, uint256 overall, uint256 timestamp);
event ScoreBreakdownRecorded(indexed address agent, uint256 txScore, uint256 x402Score, uint256 erc8004Score);
event OwnershipTransferred(indexed address previousOwner, indexed address newOwner);
```

### Integration with DeFi

**Example: Aave의 점수 기반 대출 승인**

```solidity
// Aave 계약에서 (의사 코드)
import "./AgentFICOScore.sol";

contract AaveLendingPool {
    AgentFICOScore public agentFICO;
    
    function depositAsCollateral(address agent, uint256 amount) external {
        // AgentFICO 점수 조회
        AgentFICOScore.Score memory score = agentFICO.getScore(agent);
        
        // 점수에 따라 대출 한도 결정
        uint256 maxLoanAmount = calculateLoanLimit(score.overall);
        
        require(amount <= maxLoanAmount, "Exceeds loan limit");
        
        // 대출 진행
        _depositCollateral(agent, amount);
    }
    
    function calculateLoanLimit(uint256 score) internal pure returns (uint256) {
        if (score >= 900) return 1_000_000 * 10 ** 6;      // $1M
        if (score >= 800) return 500_000 * 10 ** 6;        // $500K
        if (score >= 700) return 100_000 * 10 ** 6;        // $100K
        if (score >= 600) return 50_000 * 10 ** 6;         // $50K
        return 10_000 * 10 ** 6;                           // $10K
    }
}
```

### Integration with x402

**Example: x402의 수수료 자동 결정**

```solidity
// x402 계약에서
contract x402Market {
    AgentFICOScore public agentFICO;
    
    function executeTrade(address agent, uint256 amount) external returns (uint256) {
        // AgentFICO 점수에서 종합점수만 조회 (가스 효율적)
        uint256 score = agentFICO.getScoreOnly(agent);
        
        // 점수 기반 수수료 설정
        uint256 feePercent = calculateFee(score);
        uint256 feeAmount = (amount * feePercent) / 100;
        
        // 거래 실행
        _executeTrade(agent, amount, feeAmount);
        
        return feeAmount;
    }
    
    function calculateFee(uint256 score) internal pure returns (uint256) {
        if (score >= 900) return 25;   // 0.25%
        if (score >= 800) return 50;   // 0.50%
        if (score >= 700) return 75;   // 0.75%
        if (score >= 600) return 150;  // 1.50%
        return 300;                    // 3.00%
    }
}
```

---

## 🔄 데이터 파이프라인

### Daily Batch Job (00:00 UTC)

```python
# File: scheduler.py
# Runs daily at 00:00 UTC using APScheduler

from apscheduler.schedulers.background import BackgroundScheduler
from data_collector import collect_data
from score_engine import calculate_scores
from blockchain import update_on_chain
import logging

logger = logging.getLogger(__name__)

class AgentFICOScheduler:
    def __init__(self, app, db, w3, contract):
        self.app = app
        self.db = db
        self.w3 = w3
        self.contract = contract
        self.scheduler = BackgroundScheduler()
    
    def start(self):
        self.scheduler.add_job(
            self.daily_update,
            'cron',
            hour=0,
            minute=0,
            timezone='UTC',
            id='agentfico_daily_update'
        )
        self.scheduler.start()
        logger.info("AgentFICO scheduler started")
    
    async def daily_update(self):
        """
        Daily score calculation and blockchain update
        Timeline: ~15-30 minutes total
        """
        try:
            logger.info("Starting daily AgentFICO update...")
            
            # Step 1: Collect data (5 minutes)
            logger.info("Step 1: Collecting data from Etherscan, x402, ERC-8004...")
            start_time = time.time()
            
            all_agents = self.db.query(Agent).all()
            collected_data = []
            
            for agent in all_agents:
                data = await collect_data(agent.address)
                collected_data.append({
                    'address': agent.address,
                    'data': data
                })
            
            collection_time = time.time() - start_time
            logger.info(f"Data collection completed in {collection_time:.2f}s")
            
            # Step 2: Calculate scores (2 minutes)
            logger.info("Step 2: Calculating scores...")
            start_time = time.time()
            
            scores_to_update = []
            for item in collected_data:
                address = item['address']
                data = item['data']
                
                score = calculate_scores(
                    tx_data=data['transactions'],
                    x402_data=data['x402'],
                    erc8004_data=data['erc8004']
                )
                
                scores_to_update.append({
                    'address': address,
                    'score': score
                })
            
            calc_time = time.time() - start_time
            logger.info(f"Score calculation completed in {calc_time:.2f}s")
            
            # Step 3: Update PostgreSQL (1 minute)
            logger.info("Step 3: Updating PostgreSQL...")
            start_time = time.time()
            
            for item in scores_to_update:
                address = item['address']
                score = item['score']
                
                # Upsert into scores table
                existing_score = self.db.query(Score).filter(
                    Score.agent_address == address,
                    Score.created_at >= datetime.now() - timedelta(days=1)
                ).first()
                
                if existing_score:
                    existing_score.overall_score = score['overall']
                    existing_score.tx_success_score = score['tx_success']
                    existing_score.x402_profit_score = score['x402_profit']
                    existing_score.erc8004_stability_score = score['erc8004_stability']
                    existing_score.confidence = score['confidence']
                else:
                    new_score = Score(
                        agent_address=address,
                        overall_score=score['overall'],
                        tx_success_score=score['tx_success'],
                        x402_profit_score=score['x402_profit'],
                        erc8004_stability_score=score['erc8004_stability'],
                        confidence=score['confidence'],
                        risk_level=score['risk_level'],
                        calculated_at=datetime.now()
                    )
                    self.db.add(new_score)
            
            self.db.commit()
            db_time = time.time() - start_time
            logger.info(f"Database update completed in {db_time:.2f}s")
            
            # Step 4: Update Smart Contract (10 minutes, batch)
            logger.info("Step 4: Updating Smart Contract (batched)...")
            start_time = time.time()
            
            # Batch update in groups of 10 to save gas
            batch_size = 10
            for i in range(0, len(scores_to_update), batch_size):
                batch = scores_to_update[i:i+batch_size]
                
                for item in batch:
                    address = item['address']
                    score = item['score']
                    
                    tx = self.contract.functions.updateScore(
                        Web3.toChecksumAddress(address),
                        score['tx_success'],
                        score['x402_profit'],
                        score['erc8004_stability'],
                        score['confidence'],
                        score['risk_level'],
                        score['ipfs_hash']
                    ).build_transaction({
                        'from': self.w3.eth.accounts[0],
                        'nonce': self.w3.eth.get_transaction_count(self.w3.eth.accounts[0]),
                        'gas': 150000,
                        'gasPrice': self.w3.eth.gas_price,
                    })
                    
                    # Sign and send
                    signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                    
                    logger.info(f"Contract update for {address}: {tx_hash.hex()}")
                
                # Wait for confirmation
                time.sleep(30)
            
            blockchain_time = time.time() - start_time
            logger.info(f"Blockchain update completed in {blockchain_time:.2f}s")
            
            # Step 5: Invalidate cache
            logger.info("Step 5: Invalidating Redis cache...")
            redis_client.flushdb()
            
            total_time = collection_time + calc_time + db_time + blockchain_time
            logger.info(f"Daily update completed successfully in {total_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Daily update failed: {str(e)}", exc_info=True)
            # Send alert
            send_alert(f"AgentFICO Daily Update Failed: {str(e)}")
```

### Data Sources 통합

```python
# File: data_collector.py

from web3 import Web3
import requests
from datetime import datetime, timedelta
import json

class DataCollector:
    def __init__(self, etherscan_key, x402_key):
        self.etherscan_key = etherscan_key
        self.x402_key = x402_key
        self.session = requests.Session()
    
    async def collect_all(self, agent_address: str):
        """
        Collect data from all 3 sources concurrently
        """
        results = await asyncio.gather(
            self.collect_etherscan(agent_address),
            self.collect_x402(agent_address),
            self.collect_erc8004(agent_address),
            return_exceptions=True
        )
        
        return {
            'transactions': results[0],
            'x402': results[1],
            'erc8004': results[2],
            'collected_at': datetime.now()
        }
    
    async def collect_etherscan(self, address: str):
        """
        Get transaction data from Etherscan
        """
        url = "https://api.etherscan.io/api"
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": "0",
            "endblock": "99999999",
            "sort": "desc",
            "apikey": self.etherscan_key
        }
        
        response = await self.session.get(url, params=params, timeout=10)
        data = response.json()
        
        if data['status'] != '1':
            return []
        
        txs = data['result']
        cutoff_time = datetime.now() - timedelta(days=30)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        recent_txs = [
            tx for tx in txs
            if int(tx['timeStamp']) > cutoff_timestamp
        ]
        
        return recent_txs
    
    async def collect_x402(self, address: str):
        """
        Get x402 trading data
        """
        # TODO: x402 API endpoint 확인 후 구현
        url = "https://api.x402.world/agent/trades"
        params = {
            "agent_address": address,
            "period": "7d",
            "key": self.x402_key  # from env
        }
        
        try:
            response = await self.session.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            logger.warning(f"x402 data collection failed: {str(e)}")
            return {}
    
    async def collect_erc8004(self, address: str):
        """
        Get ERC-8004 metadata
        """
        w3 = Web3(Web3.HTTPProvider('https://eth-mainnet.alchemyapi.io/v2/YOUR_KEY'))
        
        # Call ERC-8004 registry contract
        contract = w3.eth.contract(
            address='0xERC8004_REGISTRY_ADDRESS',
            abi=ERC8004_ABI
        )
        
        try:
            metadata = contract.functions.getAgentMetadata(address).call()
            verification = contract.functions.getVerificationStatus(address).call()
            reputation = contract.functions.getReputation(address).call()
            
            return {
                'name': metadata[0],
                'description': metadata[1],
                'website': metadata[2],
                'verification_level': verification,
                'reputation_score': reputation[0],
                'reputation_reviews': reputation[1]
            }
        except Exception as e:
            logger.warning(f"ERC-8004 data collection failed: {str(e)}")
            return {}
```

---

## 🚀 배포 계획

### 개발 단계

```
Phase 1: Local Development (Week 1-2)
├─ FastAPI 서버 개발
├─ PostgreSQL 스키마 설계
├─ Smart Contract 개발 (Solidity)
├─ 기본 API 구현
└─ 단위 테스트 작성

Phase 2: Integration Testing (Week 3)
├─ API ↔ DB 통합 테스트
├─ Data Collector 테스트 (Mainnet Testnet 사용)
├─ Smart Contract 테스트 (Hardhat)
├─ End-to-End 테스트
└─ Performance 테스트

Phase 3: Staging Deployment (Week 4)
├─ AWS/Railway에 스테이징 배포
├─ Base Sepolia 테스트넷에 계약 배포
├─ 실제 데이터로 테스트
├─ 모니터링 설정
└─ 성능 최적화

Phase 4: Production Launch (Week 5)
├─ Base Mainnet에 Smart Contract 배포
├─ Production API 배포
├─ 모니터링 & Alert 설정
├─ Disaster Recovery 계획
└─ 공식 발표
```

### Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Load Balancer (CloudFlare)      │
│         (DDoS protection, Caching)      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼──────────────────────┐
│        API Gateway (Kong)               │
│        (Rate limiting, Auth)            │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┼─────────┐
        ↓         ↓         ↓
    ┌────────┐ ┌────────┐ ┌────────┐
    │API Pod │ │API Pod │ │API Pod │
    │  (n=3) │ │  (n=3) │ │  (n=3) │
    └────────┘ └────────┘ └────────┘
        │         │         │
        └─────────┼─────────┘
                  ↓
        ┌──────────────────────┐
        │  PostgreSQL (RDS)    │
        │  - Multi-AZ          │
        │  - Automated backup  │
        └──────────────────────┘
                  │
        ┌─────────┴──────────┐
        ↓                    ↓
    ┌────────┐        ┌──────────┐
    │ Redis  │        │ Scheduler│
    │(Cache) │        │(Job Queue)
    └────────┘        └──────────┘
                         │
                         ↓
                  ┌──────────────┐
                  │Ethereum RPC  │
                  │(Alchemy/     │
                  │ Infura)      │
                  └──────────────┘
```

---

## ⚡ 성능 & 보안

### 성능 목표

```
API Latency (p99):
├─ GET /score: <100ms
├─ POST /assessment: <200ms
├─ GET /breakdown: <150ms
└─ GET /history: <200ms

Throughput:
├─ 10,000 requests/second (peak)
├─ 99.99% availability
└─ <1s recovery time

Database:
├─ Query time: <50ms (with index)
├─ Write time: <100ms
└─ Replication lag: <1s
```

### 보안 조치

```
API Security:
├─ API Key 관리 (rotate every 90 days)
├─ Rate limiting (100-1000 req/min per key)
├─ CORS policy (whitelist specific domains)
├─ HTTPS enforced (TLS 1.3)
├─ WAF (Web Application Firewall)
└─ DDoS protection (CloudFlare)

Data Security:
├─ Encryption at rest (AES-256)
├─ Encryption in transit (TLS)
├─ Database credentials in Secrets Manager
├─ No sensitive data in logs
└─ GDPR compliant data retention

Smart Contract:
├─ OpenZeppelin audit (pre-launch)
├─ Multi-sig wallet for admin (2-of-3)
├─ Circuit breaker (pause function)
├─ Reentrancy guard
└─ Event logging for all changes
```

### 모니터링

```
Metrics:
├─ API response time (per endpoint)
├─ Database query time
├─ Error rates (4xx, 5xx)
├─ Rate limit violations
├─ Cache hit rate
├─ Blockchain transaction status
└─ Data collection status

Alerting:
├─ P99 latency > 500ms
├─ Error rate > 1%
├─ Database down
├─ Smart contract failure
├─ Rate limit abuse
└─ Data collection failure

Tools:
├─ Prometheus (metrics)
├─ Grafana (dashboards)
├─ ELK Stack (logs)
├─ PagerDuty (alerts)
└─ Sentry (error tracking)
```

---

## 📅 개발 타임라인

### Week 1-2: MVP 개발

```
Tasks:
├─ Backend API 기본 구조 (FastAPI)
├─ PostgreSQL 스키마 설계
├─ Etherscan 데이터 수집 (REST API)
├─ 점수 계산 엔진
├─ Smart Contract 기본 구현
└─ 단위 테스트

Deliverables:
├─ Basic API (GET /score)
├─ Database schema
├─ Score calculation logic
└─ Contract ABI

Hours: ~160 (2 engineers)
```

### Week 3: 통합 & 테스트

```
Tasks:
├─ API ↔ DB 통합
├─ x402 API 연동
├─ ERC-8004 메타데이터 수집
├─ 일일 배치 작업 구현
├─ Smart Contract 테스트 (Hardhat)
├─ 통합 테스트
└─ 성능 테스트

Deliverables:
├─ Full API (all 4 endpoints)
├─ Data pipeline
├─ Tested smart contract
└─ Performance baseline

Hours: ~120 (2 engineers + QA)
```

### Week 4: 스테이징 배포

```
Tasks:
├─ AWS/Railway 인프라 설정
├─ 모니터링 & Logging 설정
├─ Testnet에 계약 배포
├─ 스테이징 서버 배포
├─ E2E 테스트
└─ 보안 감사 (내부)

Deliverables:
├─ Staging environment
├─ Testnet contract
├─ Monitoring dashboard
└─ Security checklist

Hours: ~100 (1 engineer + DevOps)
```

### Week 5: 프로덕션 론칭

```
Tasks:
├─ Mainnet에 계약 배포
├─ 프로덕션 배포 (blue-green)
├─ Go-live checklist
├─ 초기 파트너 온보딩
├─ 모니터링 & Support
└─ Post-launch 최적화

Deliverables:
├─ Production API
├─ Mainnet contract (verified)
├─ API documentation
└─ Support playbook

Hours: ~80 (full team)
```

### 총 소요 시간

```
개발: 160 hours (2 engineers)
테스트: 80 hours (QA/engineer)
DevOps: 60 hours (1 engineer)
보안: 40 hours (security review)
────────────────────────────
Total: ~340 engineer-hours
       ~5-6주 (2-3명 팀)
```

---

## 📊 비용 추정

### 초기 구축 비용

```
개발 (340시간 @ $150/시간):      $51,000
인프라 설정:                      $5,000
보안 감사:                        $3,000
테스트 환경:                      $2,000
────────────────────────────────
Total MVP: ~$61,000
```

### 월간 운영 비용

```
Compute (3 API pods):            $300-500
Database (PostgreSQL RDS):       $200-400
Redis cache:                     $100-150
Smart Contract calls (Base L2):  $1-5 (vs Ethereum $100-300)
Basescan/RPC (Alchemy):          $100-200
Monitoring (Datadog):            $200-400
CDN (CloudFlare):                $100-200
────────────────────────────────
Total Monthly: ~$1,000-1,850 (Base L2 사용 시)
```

---

## 결론

**하이브리드 아키텍처로 AgentFICO를 구축하면:**

```
✅ 빠른 API 응답 (<100ms)
✅ 투명한 검증 (블록체인)
✅ 효율적인 비용 (~$1,500/월)
✅ 자동화된 시스템 (배치 처리)
✅ Web3 철학 준수 (Trustless)
✅ 확장 가능 (DeFi 자동 연동)

🎯 5-6주 만에 MVP 출시 가능
```
