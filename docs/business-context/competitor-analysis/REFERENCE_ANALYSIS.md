# AgentFICO 참고 프로젝트 비교 분석

> **목적**: AgentFICO 개발에 참고할 수 있는 오픈소스 프로젝트 비교 분석
> 
> **작성일**: 2026-01-29
> 
> **클론된 저장소 위치**: `/Users/zayden/Documents/web3_folder/`

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [아키텍처 비교](#2-아키텍처-비교)
3. [점수 계산 로직 비교](#3-점수-계산-로직-비교)
4. [스마트 컨트랙트 비교](#4-스마트-컨트랙트-비교)
5. [AgentFICO에 적용할 인사이트](#5-agentfico에-적용할-인사이트)
6. [참고 리소스](#6-참고-리소스)

---

## 1. 프로젝트 개요

### 1.1 클론된 프로젝트 목록

| 프로젝트 | 위치 | 목적 | Tech Stack |
|----------|------|------|------------|
| **awesome-erc8004** | `./awesome-erc8004/` | ERC-8004 표준 리소스 | Markdown |
| **Credora** | `./Credora/` | AI 신용점수 플랫폼 (Stellar) | Next.js, Soroban, Python ML |
| **kubera-backend** | `./kubera-backend/` | 온체인 신용점수 백엔드 | Node.js, ORA Protocol |
| **oink-protocol** | `./oink-protocol/` | 담보 부족 대출 평판 시스템 | Solidity, Foundry |
| **zkcreditscore** | `./zkcreditscore/` | ZK 기반 신용점수 | EZKL, Axiom, Next.js |
| **skorecard** | `./skorecard/` | ML 신용점수 모델 라이브러리 | Python, scikit-learn |
| **awesome-x402** | `./awesome-x402/` | x402 결제 프로토콜 리소스 | Markdown |

### 1.2 AgentFICO vs 참고 프로젝트

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          프로젝트 포지셔닝 비교                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│     [Target]           [Blockchain]           [Approach]                    │
│                                                                             │
│  AgentFICO ────────→ Ethereum/Base ────────→ Hybrid (API + Contract)       │
│  (AI 에이전트)        ERC-8004               x402 Profitability             │
│                                                                             │
│  Credora ──────────→ Stellar/Soroban ──────→ AI + On-chain Oracle          │
│  (개인/소기업)                               Off-chain ML Scoring           │
│                                                                             │
│  Kubera ───────────→ Ethereum ─────────────→ Verifiable On-chain           │
│  (DeFi 유저)         ORA Protocol            ZK Indexing (Aave)            │
│                                                                             │
│  O.I.N.K ──────────→ Ethereum ─────────────→ Pure On-chain                 │
│  (대출 사용자)       OpenZeppelin            Tiered Reputation             │
│                                                                             │
│  zkCreditScore ────→ Ethereum ─────────────→ ZKML + ZK Proofs              │
│  (프라이버시)        EZKL, Axiom             Privacy-preserving            │
│                                                                             │
│  skorecard ────────→ Off-chain Only ───────→ Traditional ML                │
│  (뱅킹)              scikit-learn            Logistic Regression           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 아키텍처 비교

### 2.1 Credora 아키텍처 (Stellar 기반)

**위치**: `./Credora/`

```
┌─────────────────────────────────────────────────────────────┐
│                    Credora Architecture                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend (Next.js + TailwindCSS)                           │
│      └── Wallet Connection (Freighter)                      │
│      └── User Dashboard / Partner Dashboard                 │
│                  │                                          │
│                  ▼                                          │
│  AI Scoring Engine (Python - scikit-learn, XGBoost)         │
│      └── On-chain Activity Analysis                         │
│      └── Off-chain Alternative Data                         │
│      └── Gemini API (AI Recommendations)                    │
│                  │                                          │
│                  ▼                                          │
│  Soroban Smart Contract (Score Oracle)                      │
│      └── Score Anchoring                                    │
│      └── Non-custodial Score Retrieval                      │
│                  │                                          │
│  Storage: IPFS/Arweave (Encrypted Vaults)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**핵심 구조** (`./Credora/src/`):
```
src/
├── ai/                 # AI 관련 로직
├── app/                # Next.js App Router
├── components/         # UI 컴포넌트
├── context/            # React Context
├── hooks/              # Custom Hooks
└── lib/                # 유틸리티
```

**AgentFICO 참고 포인트**:
- ✅ AI 스코어링 엔진 분리 구조
- ✅ 사용자/파트너 대시보드 분리
- ⚠️ Stellar 기반 (우리는 Ethereum/Base)


### 2.2 Kubera 아키텍처 (ORA Protocol)

**위치**: `./kubera-backend/`

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubera Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  API Endpoints                                               │
│      └── /insert: 신규 유저 데이터 삽입                      │
│      └── /update: 점수 업데이트 (last block → current)       │
│                  │                                          │
│                  ▼                                          │
│  ORA Protocol CLE (Compute Layer Engine)                    │
│      └── Aave V2 이벤트 인덱싱 (Borrow, Repay)               │
│      └── Verifiable & Tamper-proof Data                     │
│                  │                                          │
│                  ▼                                          │
│  Credit Score Formula                                        │
│      └── Outstanding Debt Aggregation                        │
│      └── Wei → USD Conversion                               │
│                  │                                          │
│                  ▼                                          │
│  Tableland + Smart Contract                                  │
│      └── Score Storage                                       │
│      └── Last Block Indexed                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**핵심 코드** (`./kubera-backend/src/exec.ts`):
```typescript
// ORA Protocol CLE를 사용한 온체인 데이터 인덱싱
export async function Exec(execBlockid: number) {
  const yaml = cleapi.CLEYaml.fromYamlContent(yamlContent)
  const dsp = cleapi.dspHub.getDSPByYaml(yaml, {})
  
  const state = await cleapi.execute(
    { wasmUint8Array, cleYaml: yaml },
    execParams
  )
  return Buffer.from(state).toString("hex")
}
```

**AgentFICO 참고 포인트**:
- ✅ 증분 인덱싱 (last block → current) - 효율적
- ✅ Verifiable 데이터 수집 패턴
- ✅ API 구조 (/insert, /update)


### 2.3 zkCreditScore 아키텍처 (ZKML)

**위치**: `./zkcreditscore/`

```
┌─────────────────────────────────────────────────────────────┐
│                 zkCreditScore Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Reputation Stack (Web3)                                     │
│      └── Transaction History                                 │
│      └── World ID Verification                               │
│      └── Axiom ZK Proofs                                     │
│                  │                                          │
│                  ▼                                          │
│  EZKL (Zero-Knowledge ML)                                    │
│      └── Private Credit Score Generation                     │
│      └── Proof Generation                                    │
│                  │                                          │
│                  ▼                                          │
│  Lendor Smart Contracts                                      │
│      └── Base, Scroll, Celo 배포                             │
│      └── Microcredit 지급                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**프로젝트 구조** (`./zkcreditscore/client/`):
```
client/
├── circuit/       # ZK Circuit 정의
├── contracts/     # Smart Contracts
├── src/           # Frontend
└── utils/         # 유틸리티
```

**AgentFICO 참고 포인트**:
- ✅ 프라이버시 보존 점수 (향후 로드맵)
- ✅ 멀티체인 배포 패턴 (Base, Scroll, Celo)
- ⚠️ ZKML은 복잡도 높음 (MVP 이후 고려)

---

## 3. 점수 계산 로직 비교

### 3.1 O.I.N.K 점수 시스템 (Pure On-chain)

**위치**: `./oink-protocol/contracts/`

```solidity
// ReputationScore.sol - Tier 기반 시스템
/*
 * RANKING HIERARCHY:
 * 0 = Bronze Tier    → 100% Collateralized
 * 250 = Silver Tier  → 75% Collateralized
 * 500 = Gold Tier    → 50% Collateralized
 * 750 = Platinum Tier → 25% Collateralized
 * 975-1000 = Diamond → 0% Collateralized
 *
 * POINT WEIGHTAGE:
 * On-time Interest Payment = 10 points
 * Limit Usage = 1 point per 10% of non-collateralized limit
 * Length of Reputation = 1 point per day
 */
```

```solidity
// Accounts.sol - 핵심 구현
contract Accounts is ReentrancyGuard {
    struct AccountDetails {
        uint256 points;
        uint256 creditLimit;
        uint256 creditBalance;
        uint256 collateralBalance;
        uint256 collateralRequired;
        uint256 currentAPR;
        uint256 accuredInterestBalance;
    }
    
    function _updateAccountDetails(address _user, uint256 _points) internal {
        if (_points < 250) {
            // Bronze: $1k limit, 100% collateral, 25% APR
            s_accountDetails[_user].creditLimit = s_bronzeCreditLimit;
            s_accountDetails[_user].collateralRequired = 100;
            s_accountDetails[_user].currentAPR = 25;
        } else if (_points < 500) {
            // Silver: $2k limit, 75% collateral, 20% APR
            ...
        }
        // Gold, Platinum, Diamond tiers...
    }
}
```

**AgentFICO 적용**:
| O.I.N.K 개념 | AgentFICO 매핑 |
|-------------|---------------|
| Points (0-1000) | AgentFICO Score (0-1000) |
| On-time Payment (+10) | Successful Tx (+점수) |
| Length of Reputation | ERC-8004 등록 기간 |
| Tiered Collateral | DeFi LTV 결정 |


### 3.2 skorecard 점수 모델 (ML 기반)

**위치**: `./skorecard/skorecard/`

```python
# skorecard.py - scikit-learn 호환 신용점수 모델
class Skorecard(BaseEstimator, ClassifierMixin):
    """
    전통적인 은행 신용점수 모델 구현
    - Logistic Regression 기반
    - Feature Bucketing (구간화)
    - Weight of Evidence (WoE) 인코딩
    """
    
    def __init__(
        self,
        bucketing=None,           # 구간화 단계
        encoder: str = "woe",     # WoE 인코딩
        variables: List = [],      # 사용 변수
        lr_kwargs: dict = {"solver": "lbfgs"},
        calculate_stats: bool = False,
    ):
        ...
```

**Bucketing 구조**:
```python
# 수치형 변수 구간화
prebucketing_pipeline = make_pipeline(
    DecisionTreeBucketer(variables=num_cols, max_n_bins=100),
    OrdinalCategoricalBucketer(variables=cat_cols, tol=0.01)
)

# 최적 구간 설정
bucketing_pipeline = make_pipeline(
    OptimalBucketer(variables=num_cols, max_n_bins=5, min_bin_size=0.08),
    OptimalBucketer(variables=cat_cols, max_n_bins=5, min_bin_size=0.08)
)
```

**AgentFICO 적용**:
```python
# AgentFICO Score Formula (제안)
def calculate_agent_score(
    tx_success_rate: float,      # 0-100 (Etherscan)
    x402_profitability: float,   # 0-100 (x402 API)
    erc8004_stability: float     # 0-100 (Registry)
) -> int:
    # 가중 평균 (40-40-20)
    score = (
        tx_success_rate * 0.40 +
        x402_profitability * 0.40 +
        erc8004_stability * 0.20
    ) * 10  # 0-1000 스케일
    
    return int(score)
```


### 3.3 점수 계산 비교표

| 항목 | AgentFICO | O.I.N.K | Credora | skorecard |
|------|-----------|---------|---------|-----------|
| **점수 범위** | 0-1000 | 0-1000 | 0-1000 | 0-1000 |
| **계산 위치** | Off-chain (API) | On-chain | Off-chain (ML) | Off-chain (ML) |
| **저장 위치** | On-chain (Smart Contract) | On-chain | On-chain (Soroban) | Off-chain |
| **주요 지표** | Tx Success, x402, ERC-8004 | Payment, Usage, Time | Alt Data, On-chain | Traditional Credit |
| **업데이트 주기** | Daily Batch | Real-time | Periodic | On-demand |
| **프라이버시** | Public | Public | User-owned | Private |

---

## 4. 스마트 컨트랙트 비교

### 4.1 O.I.N.K Accounts.sol 분석

```solidity
// 핵심 패턴 - Tiered System
contract Accounts is ReentrancyGuard {
    // Tier별 상수 정의
    uint256 public constant s_bronzeCreditLimit = 1000;
    uint256 public constant s_silverCreditLimit = 2000;
    uint256 public constant s_bronzeAPR = 25;
    uint256 public constant s_silverAPR = 20;
    
    // 유저 상태 관리
    mapping(address user => AccountDetails account) private s_accountDetails;
    
    // 포인트 기반 티어 업데이트
    function _updateAccountDetails(address _user, uint256 _points) internal {
        if (_points < 250) {
            // Bronze tier
        } else if (_points < 500) {
            // Silver tier
        }
        // ...
    }
}
```

**AgentFICO 적용 가능한 패턴**:
- ✅ Tiered risk level 시스템
- ✅ 점수 기반 자동 업데이트
- ✅ ReentrancyGuard 보안 패턴


### 4.2 AgentFICO 컨트랙트 제안 (개선)

```solidity
// AgentFICOScore.sol - O.I.N.K 패턴 적용
contract AgentFICOScore is Ownable, Pausable, ReentrancyGuard {
    
    // 위험 등급별 DeFi 파라미터
    struct RiskTier {
        uint256 minScore;
        uint256 maxLTV;          // Loan-to-Value ratio
        uint256 maxLoanAmount;   // 최대 대출 한도
        uint256 feeDiscount;     // x402 수수료 할인율
    }
    
    // 5단계 위험 등급 (O.I.N.K 패턴)
    RiskTier[5] public riskTiers;
    
    constructor() {
        // Diamond: 900-1000점, 80% LTV, $1M 한도, 75% 수수료 할인
        riskTiers[0] = RiskTier(900, 80, 1_000_000, 75);
        // Platinum: 800-899점
        riskTiers[1] = RiskTier(800, 75, 500_000, 50);
        // Gold: 700-799점
        riskTiers[2] = RiskTier(700, 70, 100_000, 25);
        // Silver: 600-699점
        riskTiers[3] = RiskTier(600, 65, 50_000, 10);
        // Bronze: 0-599점
        riskTiers[4] = RiskTier(0, 60, 10_000, 0);
    }
    
    // DeFi 통합 함수
    function getRiskTier(address agent) external view returns (RiskTier memory) {
        uint256 score = scores[agent].overall;
        for (uint i = 0; i < 5; i++) {
            if (score >= riskTiers[i].minScore) {
                return riskTiers[i];
            }
        }
        return riskTiers[4]; // Default: Bronze
    }
}
```

---

## 5. AgentFICO에 적용할 인사이트

### 5.1 아키텍처 인사이트

| 소스 | 인사이트 | 적용 방안 |
|------|----------|-----------|
| **Credora** | AI 엔진 분리 | `api/services/score_engine.py` 별도 모듈화 |
| **Kubera** | 증분 인덱싱 | Last indexed block 저장, 효율적 배치 처리 |
| **zkCreditScore** | 멀티체인 | Base 우선, 이후 Scroll/Arbitrum 확장 |
| **O.I.N.K** | Tier 시스템 | 5단계 위험 등급 (Diamond~Bronze) |

### 5.2 점수 계산 인사이트

```python
# AgentFICO 개선된 점수 공식 (skorecard 참고)

class AgentScoreCalculator:
    """
    skorecard의 Bucketing 개념을 AI 에이전트에 적용
    """
    
    # 구간별 점수 테이블 (전통 신용점수 패턴)
    TX_SUCCESS_BUCKETS = [
        (0.95, 1.00, 100),   # 95-100%: 100점
        (0.90, 0.95, 85),    # 90-95%: 85점
        (0.80, 0.90, 70),    # 80-90%: 70점
        (0.60, 0.80, 50),    # 60-80%: 50점
        (0.00, 0.60, 30),    # 0-60%: 30점
    ]
    
    def calculate_score(
        self,
        tx_success_rate: float,
        x402_profit_rate: float,
        erc8004_days: int
    ) -> int:
        tx_score = self._bucket_score(tx_success_rate, self.TX_SUCCESS_BUCKETS)
        x402_score = self._calculate_x402_score(x402_profit_rate)
        erc8004_score = self._calculate_tenure_score(erc8004_days)
        
        # 가중 평균
        return int(tx_score * 0.4 + x402_score * 0.4 + erc8004_score * 0.2) * 10
```

### 5.3 스마트 컨트랙트 인사이트

```solidity
// O.I.N.K 패턴 적용: 자동 티어 업그레이드

contract AgentFICOScore {
    event TierChanged(address indexed agent, uint8 oldTier, uint8 newTier);
    
    function updateScore(
        address agent,
        uint256 txScore,
        uint256 x402Score,
        uint256 erc8004Score
    ) external onlyOracle {
        uint8 oldTier = _getTier(scores[agent].overall);
        
        // 점수 계산
        uint256 overall = (txScore * 40 + x402Score * 40 + erc8004Score * 20) / 100;
        scores[agent].overall = overall;
        
        uint8 newTier = _getTier(overall);
        
        // 티어 변경 시 이벤트 발생 (DeFi 프로토콜이 구독)
        if (oldTier != newTier) {
            emit TierChanged(agent, oldTier, newTier);
        }
    }
}
```

### 5.4 우선순위별 적용 계획

```
┌─────────────────────────────────────────────────────────────┐
│                    적용 우선순위                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [P0 - MVP 필수]                                            │
│  ├── O.I.N.K: Tiered 위험 등급 시스템                       │
│  ├── Kubera: 증분 인덱싱 패턴                               │
│  └── awesome-x402: x402 SDK 통합                            │
│                                                              │
│  [P1 - MVP 권장]                                            │
│  ├── Credora: AI 엔진 모듈 분리                             │
│  ├── skorecard: Bucketing 점수 테이블                       │
│  └── awesome-erc8004: Identity Registry 연동                │
│                                                              │
│  [P2 - Post-MVP]                                            │
│  ├── zkCreditScore: ZKML 프라이버시                         │
│  └── Multi-chain 배포 (Scroll, Arbitrum)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. 참고 리소스

### 6.1 ERC-8004 리소스 (awesome-erc8004)

| 리소스 | URL | 용도 |
|--------|-----|------|
| EIP-8004 Spec | https://eips.ethereum.org/EIPS/eip-8004 | 공식 표준 |
| 8004.org | https://8004.org/ | 공식 사이트 |
| Reference Impl | https://github.com/ChaosChain/trustless-agents-erc-ri | 참조 구현 |
| TEE Example | https://github.com/HashWarlock/erc-8004-ex-phala/ | TEE 구현 |

### 6.2 x402 리소스 (awesome-x402)

| 리소스 | URL | 용도 |
|--------|-----|------|
| x402 Protocol | https://github.com/coinbase/x402 | 공식 SDK |
| x402 Python | https://pypi.org/project/x402/ | Python SDK |
| Base x402 Docs | https://docs.base.org/base-app/agents/x402-agents | Base 통합 |
| MCP Integration | https://docs.cdp.coinbase.com/x402/mcp-server | Claude 통합 |

### 6.3 클론된 저장소 활용법

```bash
# 저장소 위치
cd /Users/zayden/Documents/web3_folder/

# Credora AI 엔진 참고
ls Credora/src/ai/

# O.I.N.K 컨트랙트 참고
cat oink-protocol/contracts/Accounts.sol

# skorecard 점수 모델 참고
cat skorecard/skorecard/skorecard.py

# Kubera 인덱싱 로직 참고
cat kubera-backend/src/exec.ts

# zkCreditScore ZK 회로 참고
ls zkcreditscore/client/circuit/
```

---

## 📝 결론

AgentFICO는 기존 오픈소스 프로젝트들의 장점을 조합하여 **AI 에이전트 전용 신용점수 인프라**를 구축할 수 있습니다:

1. **O.I.N.K**: Tiered 평판 시스템 → AgentFICO 위험 등급
2. **Kubera**: 증분 온체인 인덱싱 → 효율적 배치 처리
3. **skorecard**: ML 기반 Bucketing → 점수 테이블 설계
4. **Credora**: AI 엔진 분리 → 모듈화된 아키텍처
5. **awesome-x402**: x402 SDK → 수익성 지표 수집
6. **awesome-erc8004**: ERC-8004 표준 → Identity Registry 연동

**차별화 포인트**:
- 기존 프로젝트는 **개인/DeFi 유저** 대상 → AgentFICO는 **AI 에이전트** 대상
- 기존은 단일 지표 → AgentFICO는 **Tx + x402 + ERC-8004** 복합 지표
- 기존은 단일 체인 → AgentFICO는 **Base L2 + Multi-chain** 확장 가능

---

> 📌 **다음 단계**: 이 분석을 바탕으로 `api/services/score_engine.py`와 `contracts/src/AgentFICOScore.sol` 구현 시작
