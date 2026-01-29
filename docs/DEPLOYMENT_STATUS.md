# AgentFICO Deployment Status

**Last Updated:** 2026-01-30
**Author:** AgentFICO Team

---

## 1. 완료된 작업

### 1.1 Smart Contract (Base Sepolia)

| 항목 | 상태 | 세부사항 |
|------|------|----------|
| **V2 Contract 배포** | ✅ 완료 | UUPS Proxy 패턴 |
| **Proxy Address** | `0xdF7699A597662330E553C0f48CEb16ace8b339C6` | 모든 호출은 이 주소로 |
| **Implementation** | `0x92e4FAF37DaD2f3BF300D550732f24fB76A63020` | 업그레이드 가능 |
| **Owner** | `0x733217E86135d1894bBa4775E45BA29778fBAC50` | 관리자 지갑 |
| **Basescan 검증** | ✅ 완료 | [View on Basescan](https://sepolia.basescan.org/address/0xdF7699A597662330E553C0f48CEb16ace8b339C6) |
| **등록된 에이전트** | 4개 | Jeff Zyfai, unabotter, Agent #1 (x2) |

**주요 기능:**
- `updateScore()` - 점수 업데이트 (owner only)
- `batchUpdateScores()` - 배치 업데이트 (gas efficient)
- `getScore()` / `getScoreOnly()` - 점수 조회 (+ ScoreQueried 이벤트)
- `assessRisk()` - 리스크 평가
- `requestScoreUpdate()` - 유료 업데이트 요청 (1시간 쿨다운)

**이벤트:**
- `ScoreUpdated` - 점수 업데이트 시 발생
- `ScoreQueried` - 점수 조회 시 발생 (누가 조회했는지 추적)

---

### 1.2 Frontend (Vercel)

| 항목 | 상태 | URL |
|------|------|-----|
| **Dashboard** | ✅ 배포됨 | `https://agentfico.luerre.ai` |
| **Framework** | Vite + React + TailwindCSS | |
| **Auto Deploy** | GitHub main branch 연동 | |

**현재 상태:**
- DNS 설정 완료 (Cloudflare → Vercel)
- VITE_API_URL 환경변수: `https://agentfico-api-python.onrender.com` (미작동)

---

### 1.3 Telegram Webhook (Render)

| 항목 | 상태 | URL |
|------|------|-----|
| **Webhook Service** | ✅ 배포됨 | `https://agentfico-webhook.onrender.com` |
| **Bot Token** | ✅ 설정됨 | Render 환경변수 |
| **Chat ID** | ✅ 설정됨 | Render 환경변수 |
| **Health Check** | ✅ 정상 | `/health` |

**엔드포인트:**
```
POST /webhook/score-updated   - ScoreUpdated 이벤트 알림
POST /webhook/score-queried   - ScoreQueried 이벤트 알림
POST /webhook/generic         - 일반 이벤트 알림
GET  /health                  - 상태 확인
```

**테스트 명령:**
```bash
curl -X POST https://agentfico-webhook.onrender.com/webhook/score-updated \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "0x34d6a7e5f9cd22e9b90d3028457c82e1748f344d",
    "overall": 336,
    "riskLevel": 5,
    "antiGamingApplied": true,
    "updatedBy": "0x733217E86135d1894bBa4775E45BA29778fBAC50"
  }'
```

---

### 1.4 API Server (로컬)

| 항목 | 상태 | 세부사항 |
|------|------|----------|
| **로컬 구동** | ✅ PM2 | `localhost:8000` |
| **외부 접근** | ❌ 미설정 | 방화벽/도메인 필요 |
| **Render 배포** | ❌ 실패 | 의존성 문제 (web3) |

**현재 API 기능:**
- `/v1/score/{address}` - 점수 계산 (Etherscan 실시간 조회)
- `/v1/contract/stats` - 컨트랙트 통계
- `/v1/agents` - ERC-8004 에이전트 목록
- `/health` - 상태 확인

---

### 1.5 데이터 소스

| 소스 | 상태 | 비고 |
|------|------|------|
| **txSuccess** | ✅ 실제 데이터 | Etherscan API |
| **x402Profitability** | ⚠️ NoData | 프로토콜 미확정 |
| **erc8004Stability** | ⚠️ NoData | 레지스트리 코드 있음, 비활성화 |

**점수 계산 공식:**
```
overall = (txSuccess × 0.4 + x402 × 0.4 + erc8004 × 0.2) × 10
```

현재 x402=0, erc8004=0이므로:
```
overall = txSuccess × 4  (최대 400점)
```

---

### 1.6 보안

| 항목 | 상태 | 세부사항 |
|------|------|----------|
| **Slither 분석** | ✅ 완료 | Medium 이슈 수정됨 |
| **테스트** | ✅ 100개 통과 | V1: 46 + V2: 54 |
| **Anti-Gaming** | ✅ 구현됨 | time decay, anomaly detection |
| **UUPS Proxy** | ✅ 적용됨 | 업그레이드 가능 |

---

## 2. 해결해야 할 사항

### 2.1 🔴 긴급 (P0)

#### API 외부 접근 설정
**문제:** 로컬 API (`localhost:8000`)가 외부에서 접근 불가
**영향:** Frontend가 API 호출 불가 → 대시보드 작동 안 함

**해결 옵션:**

| 옵션 | 난이도 | 비용 | 추천 |
|------|--------|------|------|
| **A. 방화벽 열기** | 쉬움 | 무료 | ⭐ |
| **B. Cloudflare Tunnel** | 중간 | 무료 | ⭐⭐ |
| **C. Nginx 리버스 프록시** | 중간 | 무료 | |
| **D. Railway/Fly.io 배포** | 중간 | 유료 | |

**Option A 실행 방법:**
```bash
# 1. 방화벽 포트 열기
sudo ufw allow 8000/tcp
sudo ufw enable

# 2. DNS 설정 (Cloudflare)
# api.agentfico.luerre.ai → 218.236.72.203

# 3. Frontend 환경변수 수정
VITE_API_URL=http://api.agentfico.luerre.ai:8000
```

---

### 2.2 🟡 중요 (P1)

#### Contract 이벤트 리스너
**문제:** Contract 이벤트 발생 시 자동으로 Telegram 알림 안 됨
**현재:** 수동으로 webhook 호출 필요

**해결 방법:**
```python
# event_listener.py
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://sepolia.base.org"))
contract = w3.eth.contract(address=PROXY_ADDRESS, abi=ABI)

# ScoreUpdated 이벤트 필터
event_filter = contract.events.ScoreUpdated.create_filter(fromBlock='latest')

while True:
    for event in event_filter.get_new_entries():
        # Webhook 호출
        requests.post(WEBHOOK_URL, json={
            "agent": event.args.agent,
            "overall": event.args.overall,
            ...
        })
    time.sleep(10)
```

**실행 방법:**
```bash
# PM2로 구동
pm2 start event_listener.py --name agentfico-listener
```

---

#### ERC-8004 데이터 활성화
**문제:** `erc8004_nodata.py` 사용 중 → 항상 0점
**현재:** `erc8004_registry.py`에 실제 코드 있음 (비활성화)

**해결 방법:**
```python
# dependencies.py 수정
from .data_sources.erc8004_registry import ERC8004RegistryClient

@lru_cache
def get_erc8004_source():
    return ERC8004RegistryClient(chain=Chain.BASE_SEPOLIA)
```

**레지스트리 주소:**
- Base Sepolia: `0xdc527768082c489e0ee228d24d3cfa290214f387`
- Sepolia: `0xf66e7CBdAE1Cb710fee7732E4e1f173624e137A7`

---

### 2.3 🟡 중요 (P1) - 추가

#### Private Config 프로덕션 배포
**문제:** Anti-Gaming 계수가 `AgentFICO-Config` private repo에 있어 로컬에서만 작동
**현재:** 클라우드 배포 시 fallback 기본값 사용 (실제 값과 다름)

**Config 파일 목록:**
```
AgentFICO-Config/coefficients/
├── time_decay.json    # 시간 기반 가중치 감소
├── anomaly.json       # 이상 탐지 임계값
├── consistency.json   # 일관성 보너스 설정
├── tx_quality.json    # 트랜잭션 품질 기준
└── sybil.json         # 시빌 공격 탐지
```

**해결 옵션:**

| 방법 | 보안 | 난이도 | 비용 | 추천 |
|------|------|--------|------|------|
| **1. 환경변수로 주입** | ⭐⭐⭐ | 쉬움 | 무료 | ⭐ 단순 |
| **2. Secret Manager (AWS/GCP)** | ⭐⭐⭐⭐⭐ | 중간 | $0.03/secret | ⭐⭐ 기업용 |
| **3. Private GitHub + Deploy Key** | ⭐⭐⭐⭐ | 중간 | 무료 | ⭐⭐ 현실적 |
| **4. Encrypted in Repo (SOPS)** | ⭐⭐⭐ | 중간 | 무료 | |
| **5. 별도 Config Server** | ⭐⭐⭐⭐⭐ | 어려움 | 유료 | 대규모 |

**추천: Option 1 + 3 조합**

```python
# config_loader.py 수정안
def load_config(name: str) -> dict:
    # 1. 환경변수에서 직접 로드 (프로덕션)
    env_key = f"AG_CONFIG_{name.upper()}"
    env_value = os.getenv(env_key)
    if env_value:
        return json.loads(env_value)
    
    # 2. 파일에서 로드 (로컬 개발용)
    config_path = _get_config_path()
    if config_path:
        ...
    
    # 3. Fallback (경고 로그)
    logger.warning(f"Using default config for {name}")
    return DEFAULT_COEFFICIENTS.get(name, {})
```

**GitHub Actions 예시:**
```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    steps:
      - uses: actions/checkout@v4
      
      # Private repo clone with Deploy Key
      - uses: actions/checkout@v4
        with:
          repository: Betalgeuse/AgentFICO-Config
          ssh-key: ${{ secrets.CONFIG_DEPLOY_KEY }}
          path: config
      
      # 환경변수로 변환
      - name: Set config env vars
        run: |
          echo "AG_CONFIG_TIME_DECAY=$(cat config/coefficients/time_decay.json)" >> $GITHUB_ENV
          echo "AG_CONFIG_ANOMALY=$(cat config/coefficients/anomaly.json)" >> $GITHUB_ENV
          # ...
```

---

### 2.4 🟢 개선 (P2)

#### 데이터베이스 캐싱
**문제:** 매 요청마다 블록체인 조회 → 느림
**해결:** PostgreSQL/SQLite에 점수 캐싱

```sql
CREATE TABLE agent_scores (
    agent_address VARCHAR(42) PRIMARY KEY,
    overall INTEGER,
    tx_success INTEGER,
    x402_profitability INTEGER,
    erc8004_stability INTEGER,
    risk_level INTEGER,
    updated_at TIMESTAMP
);
```

---

#### Cron Job 설정
**문제:** 에이전트 점수가 자동 업데이트 안 됨
**해결:** 주기적으로 점수 재계산

```bash
# crontab -e
0 */6 * * * /path/to/update_scores.py  # 6시간마다
```

---

#### HTTPS 설정 (API)
**문제:** API가 HTTP로만 접근 가능
**해결:** Let's Encrypt + Nginx 또는 Cloudflare Tunnel

---

## 3. 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Vercel)                                              │
│  https://agentfico.luerre.ai                                    │
│  - React Dashboard                                              │
│  - Agent Scores Display                                         │
│  - Real-time Updates                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  API Server (Local - PM2)                     ❌ 외부 접근 필요  │
│  http://localhost:8000                                          │
│  - Score Calculation                                            │
│  - Etherscan Integration                                        │
│  - Contract Client                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Etherscan     │  │  ERC-8004       │  │  x402 Protocol  │
│   API           │  │  Registry       │  │  (Not Ready)    │
│   ✅ Active     │  │  ⚠️ Inactive    │  │  ⚠️ Inactive    │
└─────────────────┘  └─────────────────┘  └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Smart Contract (Base Sepolia)                                  │
│  0xdF7699A597662330E553C0f48CEb16ace8b339C6                     │
│  - AgentFICOScoreV2 (UUPS Proxy)                               │
│  - 4 Agents Registered                                          │
│  - Events: ScoreUpdated, ScoreQueried                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Manual trigger needed)
┌─────────────────────────────────────────────────────────────────┐
│  Webhook Service (Render)                                       │
│  https://agentfico-webhook.onrender.com                        │
│  - Telegram Notifications                                       │
│  - Event Processing                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Telegram Bot                                                   │
│  @AgentFICOBot → Zayden                                        │
│  ✅ Connected                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 환경 변수 정리

### Frontend (Vercel)
```env
VITE_API_URL=https://agentfico-api-python.onrender.com  # 수정 필요
```

### API Server (Local)
```env
# api/.env.local
BASE_SEPOLIA_RPC=https://sepolia.base.org
AGENTFICO_CONTRACT=0xdF7699A597662330E553C0f48CEb16ace8b339C6
ETHERSCAN_API_KEY=xxx
BASESCAN_API_KEY=xxx
```

### Webhook (Render)
```env
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_CHAT_ID=<your-telegram-chat-id>
AGENTFICO_CONTRACT=0xdF7699A597662330E553C0f48CEb16ace8b339C6
```

### Contracts
```env
# contracts/.env
PRIVATE_KEY=0x...  # Owner wallet
BASE_SEPOLIA_RPC=https://sepolia.base.org
PROXY_ADDRESS=0xdF7699A597662330E553C0f48CEb16ace8b339C6
BASESCAN_API_KEY=xxx
```

---

## 5. 다음 단계 (우선순위)

1. **[P0] API 외부 접근 설정** - 방화벽 열기 또는 Cloudflare Tunnel
2. **[P0] Frontend API URL 수정** - 실제 작동하는 API로 변경
3. **[P1] Event Listener 구현** - Contract 이벤트 → Webhook 자동 호출
4. **[P1] ERC-8004 데이터 활성화** - 실제 레지스트리 연동
5. **[P2] 데이터베이스 캐싱** - 성능 최적화
6. **[P2] HTTPS 설정** - 보안 강화

---

## 6. 유용한 명령어

### Contract 조회
```bash
# 총 에이전트 수
cast call 0xdF7699A597662330E553C0f48CEb16ace8b339C6 "totalAgents()(uint256)" --rpc-url https://sepolia.base.org

# 에이전트 점수 조회
cast call 0xdF7699A597662330E553C0f48CEb16ace8b339C6 "getScoreOnly(address)(uint256)" 0x34d6... --rpc-url https://sepolia.base.org
```

### PM2 관리
```bash
pm2 status                    # 상태 확인
pm2 restart agentfico-api     # API 재시작
pm2 logs agentfico-api        # 로그 확인
```

### Render 서비스
```bash
# Dashboard: https://dashboard.render.com/web/srv-d5tnh7n18n1s73b0vbl0
# Logs: https://dashboard.render.com/web/srv-d5tnh7n18n1s73b0vbl0/logs
```

---

## 7. 관련 문서

- [ADR-001: Backend-First Development](/docs/adr/ADR-001-backend-first.md)
- [ADR-002: Score Formula (40-40-20)](/docs/adr/ADR-002-score-formula.md)
- [ADR-003: Anti-Gaming over ZK](/docs/adr/ADR-003-anti-gaming-over-zk.md)
- [Security Analysis](/docs/SECURITY_ANALYSIS.md)
- [Testnet Checklist](/docs/TESTNET_CHECKLIST.md)

---

*Generated by AgentFICO Development Team*
