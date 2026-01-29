# AgentFICO - Architecture Guide

> **마스터 아키텍처 문서** - 모든 개발자/Droid가 참조해야 하는 핵심 설계 문서

**Last Updated**: 2026-01-29  
**Version**: 0.1.0

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [아키텍처 결정 사항](#2-아키텍처-결정-사항-adr)
3. [시스템 아키텍처](#3-시스템-아키텍처)
4. [6-Layer 아키텍처](#4-6-layer-아키텍처)
5. [스토리지 전략](#5-스토리지-전략)
6. [Smart Contract 아키텍처](#6-smart-contract-아키텍처)
7. [Infrastructure as Code (IaC)](#7-infrastructure-as-code-iac)
8. [API 설계 규칙](#8-api-설계-규칙)
9. [코딩 규칙](#9-코딩-규칙-critical)
10. [Droid 역할 정의](#10-droid-역할-정의)

---

## 1. 시스템 개요

### 1.1 프로젝트 비전

**AgentFICO**는 AI 에이전트의 **신용점수 인프라**입니다. 전통적인 FICO 점수가 개인의 신용도를 평가하듯, AgentFICO는 **블록체인 기반 AI 에이전트의 신뢰도**를 평가합니다.

### 1.2 핵심 가치

| 가치 | 설명 |
|:---|:---|
| **Transparent** | 온체인 데이터 기반 투명한 점수 산출 |
| **Real-time** | 거래 발생 즉시 점수 업데이트 |
| **Composable** | DeFi 프로토콜과 쉽게 통합 가능 |
| **Decentralized** | 스마트 계약 기반 탈중앙화 |

### 1.3 Tech Stack

| Category | Technology | 용도 |
|:---|:---|:---|
| **Smart Contract** | Solidity 0.8.20+ | 점수 저장, 레지스트리 |
| **Framework** | Hardhat | 개발, 테스트, 배포 |
| **Backend** | FastAPI (Python 3.11+) | REST API 서버 |
| **Async HTTP** | httpx / aiohttp | 외부 API 호출 |
| **Database** | PostgreSQL | 집계 데이터, 히스토리 |
| **Cache** | Redis | 점수 캐싱 |
| **Data Source** | Etherscan API | 온체인 데이터 |
| **IaC** | Terraform | 인프라 코드 관리 (필수) |
| **Container** | Docker | 컨테이너화 |
| **CI/CD** | GitHub Actions | 자동화 파이프라인 |
| **Cloud** | AWS / GCP | 클라우드 인프라 |

---

## 2. 아키텍처 결정 사항 (ADR)

### ADR-001: Hybrid Architecture (API + Smart Contract)

**Status**: ✅ APPROVED

#### 문제

```
🔴 완전 온체인:
   └── 모든 점수 계산을 스마트 계약에서
   └── 가스비 과다 (수천 달러/일)
   └── 실시간 업데이트 불가

🔴 완전 오프체인:
   └── 중앙화 서버에서 점수 계산
   └── 신뢰 문제 (조작 가능성)
   └── DeFi 통합 어려움
```

#### 해결책

```
✅ Hybrid Architecture
   └── 오프체인: 점수 계산 (FastAPI)
   └── 온체인: 점수 저장 & 검증 (Solidity)
   └── 최적의 비용 + 신뢰도 조합
```

#### 패턴: "Compute Off-chain, Store On-chain"

| 구분 | 저장소 | 이유 |
|:---|:---|:---|
| 점수 계산 로직 | FastAPI (Off-chain) | 복잡한 연산, 빠른 업데이트 |
| 최종 점수 | Smart Contract (On-chain) | 신뢰성, DeFi 통합 |
| 상세 분석 | PostgreSQL | 복잡 쿼리, 히스토리 |
| 캐시 | Redis | 빠른 조회 |

---

## 3. 시스템 아키텍처

### 3.1 전체 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                      AgentFICO Architecture                      │
│              AI Agent Credit Scoring Infrastructure              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    API Layer (FastAPI)                      ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │ Score API   │  │ Assessment  │  │ Ranking             │ ││
│  │  │ /v1/score   │  │ /v1/assess  │  │ /v1/ranking         │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                         │                                        │
│                         ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                  Score Calculation Engine                   ││
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐ ││
│  │  │ Transaction   │  │ x402          │  │ ERC-8004        │ ││
│  │  │ Success Rate  │  │ Profitability │  │ Registry        │ ││
│  │  │ (40%)         │  │ (30%)         │  │ (30%)           │ ││
│  │  └───────────────┘  └───────────────┘  └─────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
│                         │                                        │
│         ┌───────────────┼───────────────┐                       │
│         ▼               ▼               ▼                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────────┐│
│  │ PostgreSQL │  │ Redis      │  │ Ethereum (Smart Contract)  ││
│  │ (History)  │  │ (Cache)    │  │ AgentFICOScore.sol         ││
│  └────────────┘  └────────────┘  └────────────────────────────┘│
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Data Sources                             ││
│  │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐ ││
│  │  │ Etherscan     │  │ x402 API      │  │ ERC-8004        │ ││
│  │  │ API           │  │ (Payments)    │  │ Registry        │ ││
│  │  └───────────────┘  └───────────────┘  └─────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 데이터 흐름

```
┌────────────────────────────────────────────────────────────────┐
│                      Score Update Flow                          │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Data Collection (Batch: 매일 00:00 UTC)                    │
│     └── Etherscan API → 거래 내역 수집                         │
│     └── x402 API → 결제 데이터 수집                            │
│     └── ERC-8004 → 등록 정보 확인                              │
│                                                                 │
│  2. Score Calculation (Off-chain)                              │
│     └── Transaction Success Rate 계산                          │
│     └── x402 Profitability 계산                                │
│     └── ERC-8004 Compliance 점수 계산                          │
│     └── 가중 평균으로 최종 점수 산출                           │
│                                                                 │
│  3. Score Storage                                              │
│     └── PostgreSQL: 상세 분석 저장                             │
│     └── Redis: 캐시 업데이트 (TTL: 1hr)                        │
│     └── Smart Contract: 최종 점수 기록 (온체인)                │
│                                                                 │
│  4. API Response                                               │
│     └── 캐시 히트 시 Redis에서 즉시 반환                       │
│     └── 캐시 미스 시 PostgreSQL 조회                           │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 4. 6-Layer 아키텍처

### 4.1 레이어 구조

```
┌─────────────────────────────────────────────┐
│  Presentation Layer (app/api/)              │  ← FastAPI Routers
├─────────────────────────────────────────────┤
│  Service Layer (app/services/)              │  ← Query/Command 분리 (CQRS)
├─────────────────────────────────────────────┤
│  Component Layer (app/components/)          │  ← 공유 컴포넌트
├─────────────────────────────────────────────┤
│  Model Layer (app/models/)                  │  ← Domain Models
├─────────────────────────────────────────────┤
│  Infra Layer (app/infra/)                   │  ← Etherscan, PostgreSQL, Redis
├─────────────────────────────────────────────┤
│  Core Layer (app/core/)                     │  ← Config, Settings
└─────────────────────────────────────────────┘
```

### 4.2 의존성 규칙

```
✅ 허용: 상위 → 하위 의존
   Presentation → Service → Infra → Core

❌ 금지: 하위 → 상위 의존 (역방향)
   Core ↛ Service
   Infra ↛ Presentation
```

### 4.3 디렉토리 구조

```
agentfico/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py           # Pydantic Settings
│   │   │   └── constants.py        # 상수 정의
│   │   ├── models/
│   │   │   ├── agent.py            # Agent Domain Model
│   │   │   ├── score.py            # Score Domain Model
│   │   │   └── assessment.py       # Assessment Domain Model
│   │   ├── infra/
│   │   │   ├── external/
│   │   │   │   ├── etherscan/      # Etherscan API Client
│   │   │   │   ├── x402/           # x402 API Client
│   │   │   │   └── erc8004/        # ERC-8004 Registry Client
│   │   │   └── persistence/
│   │   │       ├── postgres/       # PostgreSQL Repository
│   │   │       └── redis/          # Redis Cache
│   │   ├── services/
│   │   │   ├── score/
│   │   │   │   ├── query.py        # Score Query Service (Read)
│   │   │   │   └── command.py      # Score Command Service (Write)
│   │   │   └── assessment/
│   │   │       └── service.py      # Assessment Service
│   │   ├── components/
│   │   │   ├── calculator.py       # Score Calculator
│   │   │   └── aggregator.py       # Data Aggregator
│   │   └── api/
│   │       └── v1/
│   │           ├── endpoints/
│   │           │   ├── score.py    # Score Endpoints
│   │           │   ├── assessment.py
│   │           │   └── ranking.py
│   │           └── schemas/
│   │               ├── score.py    # Response Schemas
│   │               └── assessment.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── requirements.txt
│   └── Dockerfile
├── contracts/
│   ├── AgentFICOScore.sol
│   ├── ScoreRegistry.sol
│   ├── interfaces/
│   │   └── IAgentFICOScore.sol
│   └── test/
│       └── AgentFICOScore.test.ts
├── hardhat.config.ts
└── package.json
```

### 4.4 CQRS 패턴 (Query/Command 분리)

```python
# app/services/score/query.py (읽기 전용)
class ScoreQueryService:
    async def get_score(self, address: str) -> ScoreResponse:
        """점수 조회 (캐시 우선)"""
        cached = await self.redis.get(f"score:{address}")
        if cached:
            return ScoreResponse.parse_raw(cached)
        return await self.postgres.get_score(address)
    
    async def get_ranking(self, limit: int = 100) -> List[AgentRanking]:
        """랭킹 조회"""
        ...

# app/services/score/command.py (쓰기 전용)
class ScoreCommandService:
    async def update_score(self, address: str, score: int) -> None:
        """점수 업데이트 (DB + Cache + Contract)"""
        await self.postgres.save_score(address, score)
        await self.redis.set(f"score:{address}", score, ex=3600)
        await self.contract.update_score(address, score)
    
    async def recalculate_all(self) -> None:
        """전체 점수 재계산 (배치)"""
        ...
```

---

## 5. 스토리지 전략

### 5.1 Hybrid Storage Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐   ┌─────────────────────────────┐  │
│  │      PostgreSQL         │   │      Redis                  │  │
│  │      (Persistent)       │   │      (Cache)                │  │
│  ├─────────────────────────┤   ├─────────────────────────────┤  │
│  │ • agents (메타데이터)   │   │ • score:{address}          │  │
│  │ • scores (히스토리)     │   │ • ranking:top100           │  │
│  │ • assessments (분석)    │   │ • breakdown:{address}      │  │
│  │ • daily_aggregates      │   │                             │  │
│  ├─────────────────────────┤   ├─────────────────────────────┤  │
│  │ Complex Queries         │   │ TTL: 1 hour                 │  │
│  │ Historical Analysis     │   │ Sub-ms Latency              │  │
│  │ Aggregations            │   │ High Throughput             │  │
│  └─────────────────────────┘   └─────────────────────────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 Smart Contract (On-chain)                   ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │ • AgentFICOScore.sol: 최종 점수 저장                        ││
│  │ • ScoreRegistry.sol: 에이전트 목록, 랭킹                    ││
│  │ • 장점: 신뢰성, DeFi 통합, 불변성                           ││
│  │ • 단점: 가스비, 느린 업데이트                               ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 PostgreSQL 스키마

```sql
-- agents 테이블
CREATE TABLE agents (
    address VARCHAR(42) PRIMARY KEY,
    name VARCHAR(255),
    registered_at TIMESTAMP DEFAULT NOW(),
    erc8004_token_id BIGINT,
    is_active BOOLEAN DEFAULT TRUE
);

-- scores 테이블 (히스토리)
CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    agent_address VARCHAR(42) REFERENCES agents(address),
    score INTEGER CHECK (score >= 0 AND score <= 1000),
    tx_success_rate DECIMAL(5,4),
    x402_profitability DECIMAL(5,4),
    erc8004_compliance DECIMAL(5,4),
    calculated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_agent_date (agent_address, calculated_at DESC)
);

-- daily_aggregates 테이블 (집계)
CREATE TABLE daily_aggregates (
    id SERIAL PRIMARY KEY,
    agent_address VARCHAR(42) REFERENCES agents(address),
    date DATE,
    total_txs INTEGER,
    successful_txs INTEGER,
    total_volume_usd DECIMAL(18,2),
    profit_usd DECIMAL(18,2),
    UNIQUE (agent_address, date)
);
```

---

## 6. Smart Contract 아키텍처

### 6.1 계약 구조

```
contracts/
├── AgentFICOScore.sol      # 핵심 점수 계약
├── ScoreRegistry.sol       # 에이전트 레지스트리
├── interfaces/
│   ├── IAgentFICOScore.sol
│   └── IScoreRegistry.sol
└── libraries/
    └── ScoreLib.sol        # 점수 계산 헬퍼
```

### 6.2 AgentFICOScore.sol 구조

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract AgentFICOScore is Ownable, Pausable {
    struct Score {
        uint256 value;          // 0-1000
        uint256 lastUpdated;    // timestamp
        bool isRegistered;
    }
    
    mapping(address => Score) public scores;
    address[] public agents;
    
    // Oracle address (off-chain updater)
    address public oracle;
    
    event AgentRegistered(address indexed agent);
    event ScoreUpdated(address indexed agent, uint256 oldScore, uint256 newScore);
    
    modifier onlyOracle() {
        require(msg.sender == oracle, "Not oracle");
        _;
    }
    
    function registerAgent(address agent) external;
    function updateScore(address agent, uint256 score) external onlyOracle;
    function getScore(address agent) external view returns (uint256);
    function getTopAgents(uint256 limit) external view returns (address[] memory);
}
```

### 6.3 DeFi 통합 인터페이스

```solidity
// DeFi 프로토콜이 AgentFICO를 사용하는 방법
interface IAgentFICOConsumer {
    function agentFICO() external view returns (IAgentFICOScore);
    
    function getAgentScore(address agent) external view returns (uint256) {
        return agentFICO().getScore(agent);
    }
    
    // 점수 기반 대출 조건 예시
    function getLTV(address agent) external view returns (uint256) {
        uint256 score = getAgentScore(agent);
        if (score >= 900) return 80; // 80% LTV
        if (score >= 800) return 75;
        if (score >= 700) return 70;
        return 60; // 기본 60% LTV
    }
}
```

---

## 7. Infrastructure as Code (IaC)

> **⚠️ CRITICAL**: 모든 인프라는 반드시 Terraform으로 관리합니다. 콘솔 수동 설정 금지!

### 7.1 IaC 원칙

```
┌─────────────────────────────────────────────────────────────────┐
│                    Infrastructure as Code 원칙                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ✅ MUST DO:                                                    │
│     • 모든 인프라 변경은 Terraform 코드로                       │
│     • State는 원격 백엔드 (S3 + DynamoDB Lock)                  │
│     • 환경별 분리 (dev, staging, prod)                          │
│     • PR 리뷰 후 apply                                          │
│     • tfvars 파일은 절대 커밋 금지                              │
│                                                                  │
│  ❌ NEVER DO:                                                   │
│     • AWS/GCP 콘솔에서 수동 리소스 생성                         │
│     • terraform.tfstate 파일 커밋                               │
│     • Secret을 tf 파일에 하드코딩                               │
│     • plan 없이 바로 apply                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Terraform 디렉토리 구조

```
infrastructure/
├── terraform/
│   ├── environments/
│   │   ├── dev/
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   ├── outputs.tf
│   │   │   ├── backend.tf
│   │   │   └── terraform.tfvars.example  # 예시만 커밋
│   │   ├── staging/
│   │   │   └── ...
│   │   └── prod/
│   │       └── ...
│   ├── modules/
│   │   ├── api/                # FastAPI 서버 (ECS/Cloud Run)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── database/           # PostgreSQL (RDS/Cloud SQL)
│   │   │   └── ...
│   │   ├── cache/              # Redis (ElastiCache/Memorystore)
│   │   │   └── ...
│   │   ├── networking/         # VPC, Subnets, Security Groups
│   │   │   └── ...
│   │   └── monitoring/         # CloudWatch/Stackdriver
│   │       └── ...
│   └── shared/
│       └── backend.tf          # 원격 상태 저장소 설정
├── docker/
│   ├── backend.Dockerfile
│   └── docker-compose.yml
└── scripts/
    ├── deploy.sh
    └── destroy.sh
```

### 7.3 원격 상태 관리 (필수)

```hcl
# infrastructure/terraform/shared/backend.tf
terraform {
  backend "s3" {
    bucket         = "agentfico-terraform-state"
    key            = "env/${var.environment}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "agentfico-terraform-locks"
  }
}

# 또는 GCP의 경우
terraform {
  backend "gcs" {
    bucket = "agentfico-terraform-state"
    prefix = "env/${var.environment}"
  }
}
```

### 7.4 모듈 예시: API 서버

```hcl
# infrastructure/terraform/modules/api/main.tf
resource "aws_ecs_service" "api" {
  name            = "${var.project}-api-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [aws_security_group.api.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  tags = {
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "terraform"
  }
}
```

### 7.5 Secret 관리

```hcl
# ⚠️ Secret은 절대 코드에 포함하지 않음

# AWS Secrets Manager 참조
data "aws_secretsmanager_secret_version" "api_secrets" {
  secret_id = "${var.project}/${var.environment}/api"
}

locals {
  api_secrets = jsondecode(data.aws_secretsmanager_secret_version.api_secrets.secret_string)
}

# ECS Task Definition에서 사용
resource "aws_ecs_task_definition" "api" {
  # ...
  container_definitions = jsonencode([{
    name = "api"
    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = "${data.aws_secretsmanager_secret.api.arn}:DATABASE_URL::"
      },
      {
        name      = "ETHERSCAN_API_KEY"
        valueFrom = "${data.aws_secretsmanager_secret.api.arn}:ETHERSCAN_API_KEY::"
      }
    ]
  }])
}
```

### 7.6 CI/CD 통합

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - 'infrastructure/terraform/**'
  push:
    branches: [main]
    paths:
      - 'infrastructure/terraform/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        
      - name: Terraform Init
        run: terraform init
        working-directory: infrastructure/terraform/environments/${{ env.ENVIRONMENT }}
        
      - name: Terraform Plan
        run: terraform plan -out=tfplan
        working-directory: infrastructure/terraform/environments/${{ env.ENVIRONMENT }}
        
      - name: Post Plan to PR
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        # Plan 결과를 PR 코멘트로

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Terraform Apply
        run: terraform apply -auto-approve tfplan
```

### 7.7 환경별 변수 관리

```hcl
# infrastructure/terraform/environments/dev/variables.tf
variable "environment" {
  default = "dev"
}

variable "api_desired_count" {
  default = 1  # dev는 1개
}

variable "db_instance_class" {
  default = "db.t3.micro"  # dev는 작은 인스턴스
}

# infrastructure/terraform/environments/prod/variables.tf
variable "environment" {
  default = "prod"
}

variable "api_desired_count" {
  default = 3  # prod는 3개
}

variable "db_instance_class" {
  default = "db.r6g.large"  # prod는 큰 인스턴스
}
```

### 7.8 비용 예상 (참고)

| Resource | Dev (월) | Prod (월) |
|:---|:---|:---|
| ECS Fargate | $15 | $100 |
| RDS PostgreSQL | $15 | $200 |
| ElastiCache Redis | $15 | $100 |
| ALB | $20 | $50 |
| **Total** | **~$65** | **~$450** |

---

## 8. API 설계 규칙

### 8.1 camelCase Response (Required)

```python
from pydantic import BaseModel, ConfigDict

def to_camel(string: str) -> str:
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])

class ScoreResponse(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
    
    agent_address: str      # → agentAddress
    score: int
    risk_level: str         # → riskLevel
    last_updated: datetime  # → lastUpdated
```

### 7.2 REST Endpoints

| Method | Path | Description |
|:---|:---|:---|
| GET | /health | 헬스 체크 |
| GET | /v1/agent/{address}/score | 점수 조회 |
| GET | /v1/agent/{address}/breakdown | 상세 분석 |
| POST | /v1/agent/{address}/assess | 위험 평가 |
| GET | /v1/agents/ranking | 전체 랭킹 |
| GET | /v1/agents | 에이전트 목록 |

### 7.3 Response 형식

```json
// 성공 응답
{
  "agentAddress": "0x123...",
  "score": 850,
  "riskLevel": "low",
  "breakdown": {
    "transactionSuccessRate": 0.95,
    "x402Profitability": 0.82,
    "erc8004Compliance": 0.88
  },
  "lastUpdated": "2026-01-29T00:00:00Z"
}

// 에러 응답
{
  "error": "agent_not_found",
  "message": "Agent not registered in ERC-8004",
  "requestId": "uuid",
  "timestamp": "2026-01-29T00:00:00Z"
}
```

---

## 8. 코딩 규칙 (CRITICAL)

### 8.1 Async First

```python
# ✅ CORRECT: Async/Await for all I/O
async def get_score(self, address: str) -> ScoreResponse:
    cached = await self.redis.get(f"score:{address}")
    if cached:
        return ScoreResponse.parse_raw(cached)
    
    data = await self.etherscan.get_transactions(address)
    score = await self.calculator.calculate(data)
    return score

# ❌ WRONG: Sync calls
def get_score_bad(self, address):
    result = requests.get(...)  # Blocking!
    time.sleep(1)               # Blocking!
```

### 8.2 Type Hints (Required)

```python
# ✅ CORRECT: Full type hints
async def calculate_score(
    self,
    address: str,
    tx_data: List[Transaction],
    x402_data: Optional[X402Data] = None,
) -> ScoreResult:
    ...

# ❌ WRONG: No type hints
def calculate_score(self, address, tx_data, x402_data):
    ...
```

### 8.3 Configuration Management

```python
# ✅ CORRECT: Pydantic Settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ETHERSCAN_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str
    CONTRACT_ADDRESS: str
    
    class Config:
        env_file = ".env"

settings = Settings()

# ❌ WRONG: Hardcoded or scattered os.getenv
API_KEY = "hardcoded_key"  # NEVER!
```

### 8.4 Error Handling

```python
# ✅ CORRECT: Specific exceptions
from app.exceptions import AgentNotFoundError, EtherscanAPIError

try:
    data = await self.etherscan.get_transactions(address)
except EtherscanAPIError as e:
    logger.error(f"Etherscan API failed: {e}")
    raise HTTPException(502, "External API unavailable")
except AgentNotFoundError:
    raise HTTPException(404, "Agent not found")

# ❌ WRONG: Bare except
try:
    do_something()
except:
    pass
```

### 8.5 Logging Standards

```python
import logging
logger = logging.getLogger(__name__)

# ✅ CORRECT: Structured logging with context
logger.info(f"Score calculated: {address=}, {score=}, {latency_ms=}")
logger.error(f"Calculation failed: {address=}, error={str(e)}")

# ❌ WRONG: Generic messages
print("Score done")
logger.info("Something happened")
```

---

## 9. Droid 역할 정의

### 9.1 web3-smart-contract-auditor

- **역할**: 스마트 계약 보안 감사
- **담당**: AgentFICOScore.sol, ScoreRegistry.sol
- **문서 참조**: Section 6

### 9.2 web3-api-developer

- **역할**: REST API 개발
- **담당**: FastAPI 엔드포인트, 서비스 레이어
- **문서 참조**: Section 4, 7

### 9.3 blockchain-data-analyzer

- **역할**: 온체인 데이터 분석
- **담당**: Etherscan 데이터 수집, 점수 계산
- **문서 참조**: Section 3, 5

### 9.4 hardhat-test-engineer

- **역할**: 스마트 계약 테스트
- **담당**: Unit/Integration 테스트
- **문서 참조**: Section 6

### 9.5 defi-protocol-specialist

- **역할**: DeFi 프로토콜 통합
- **담당**: Aave, Uniswap 연동
- **문서 참조**: Section 6.3

---

## 관련 문서

| 문서 | 위치 | 설명 |
|:---|:---|:---|
| Tech Spec | `docs/AGENTFICO_TECH_SPEC.md` | 상세 기술 명세 |
| Business Strategy | `docs/AGENTFICO_BUSINESS_STRATEGY.md` | 비즈니스 전략 |
| M1 Tasks | `docs/orchestrator/milestones/M1.md` | 코어 인프라 태스크 |
| Droid Guide | `.factory/droids/` | Droid 명세 |
