# AgentFICO Testnet 배포 체크리스트

> **목표**: Base Sepolia에 안전하게 배포하기 전 모든 검토 항목 확인

---

## 1. 컨트랙트 설계 검토

### 1.1 UUPS Proxy 패턴 ✅
- [x] `AgentFICOScoreV2.sol` - UUPS Upgradeable 구현
- [x] `Initializable` - constructor 대신 initialize 사용
- [x] `UUPSUpgradeable` - 업그레이드 권한 관리
- [x] `OwnableUpgradeable` - 소유권 관리
- [x] `ReentrancyGuardUpgradeable` - 재진입 방지

### 1.2 주요 기능
| 기능 | 상태 | 설명 |
|:-----|:----:|:-----|
| `updateScore()` | ✅ | Owner/Oracle만 호출 가능 |
| `batchUpdateScores()` | ✅ | 대량 업데이트 (가스 효율) |
| `requestScoreUpdate()` | ✅ | 사용자 트리거 (수수료 지불) |
| `setOracle()` | ✅ | Oracle 권한 관리 |
| `withdrawFees()` | ✅ | 수수료 출금 |
| `renounceUpgradeability()` | ✅ | 영구 불변 전환 (비가역) |

### 1.3 하이브리드 업데이트 모델
```
┌─────────────────────────────────────────────────────────────────┐
│                    업데이트 모델                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Owner/Oracle 업데이트 (주기적)                                 │
│  ├─ 일 1회 또는 주 1회 배치 업데이트                            │
│  ├─ 가스비: 운영자 부담                                         │
│  └─ batchUpdateScores() 사용                                   │
│                                                                 │
│  사용자 트리거 업데이트 (온디맨드)                               │
│  ├─ requestScoreUpdate() 호출                                  │
│  ├─ 수수료: 0.001 ETH (설정 가능)                              │
│  ├─ 쿨다운: 1시간                                               │
│  └─ 이벤트 발생 → Oracle이 오프체인 계산 후 updateScore()       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 보안 체크리스트

### 2.1 정적 분석 도구
- [ ] **Slither** 실행 및 경고 검토
- [ ] **Aderyn** 실행 및 경고 검토
- [ ] **Solhint** 린팅 통과

### 2.2 수동 검토
- [ ] 재진입 공격 가능성 → `ReentrancyGuard` 적용됨 ✅
- [ ] 오버플로우/언더플로우 → Solidity 0.8+ 자동 체크 ✅
- [ ] Access Control 검토 → `onlyOwner`, `onlyAuthorized` ✅
- [ ] 외부 호출 위험 → `withdrawFees()`만 있음, nonReentrant 적용 ✅

### 2.3 키 관리
- [ ] 배포 키는 **하드웨어 월렛** 사용
- [ ] `.env` 파일에 평문 키 저장 금지
- [ ] 테스트넷 키와 메인넷 키 분리

---

## 3. 테스트 체크리스트

### 3.1 단위 테스트
- [ ] `initialize()` 정상 동작
- [ ] `updateScore()` 점수 계산 검증
- [ ] `batchUpdateScores()` 배열 처리
- [ ] `requestScoreUpdate()` 수수료 및 쿨다운
- [ ] `setOracle()` 권한 부여/해제
- [ ] `withdrawFees()` 출금 정상
- [ ] `assessRisk()` 리스크 계산
- [ ] 권한 없는 호출 revert

### 3.2 업그레이드 테스트
- [ ] V2 → V3 업그레이드 시뮬레이션
- [ ] 상태 유지 확인 (scores, totalAgents 등)
- [ ] `renounceUpgradeability()` 후 업그레이드 불가 확인

### 3.3 통합 테스트
- [ ] API → 컨트랙트 updateScore 연동
- [ ] 이벤트 리스닝 동작
- [ ] 프론트엔드 getScore 조회

---

## 4. 배포 전 준비

### 4.1 환경 설정
```bash
# .env 파일 (예시 - 실제 키 넣지 말 것!)
BASE_SEPOLIA_RPC=https://sepolia.base.org
BASESCAN_API_KEY=your_api_key

# 하드웨어 월렛 사용 시
PRIVATE_KEY=  # 비워두고 --ledger 또는 --trezor 플래그 사용
```

### 4.2 Faucet에서 테스트 ETH 수령
- [ ] [Coinbase Faucet](https://www.coinbase.com/faucets/base-ethereum-sepolia-faucet)
- [ ] 최소 0.1 ETH 확보

### 4.3 배포 명령어
```bash
# Foundry 설치 확인
forge --version

# 컴파일
forge build

# 로컬 테스트
forge test -vvv

# Base Sepolia 배포 (하드웨어 월렛)
forge script script/DeployV2.s.sol \
  --rpc-url https://sepolia.base.org \
  --broadcast \
  --verify \
  --ledger  # 또는 --trezor

# 또는 환경변수 키 사용 (테스트넷만!)
forge script script/DeployV2.s.sol \
  --rpc-url https://sepolia.base.org \
  --broadcast \
  --verify
```

---

## 5. 배포 후 검증

### 5.1 Basescan 확인
- [ ] Implementation 컨트랙트 Verified
- [ ] Proxy 컨트랙트 Verified
- [ ] "Read as Proxy" 기능 동작

### 5.2 기능 테스트
- [ ] `owner()` 반환값 확인
- [ ] `VERSION()` = 2 확인
- [ ] `updateScore()` 테스트 트랜잭션
- [ ] `getScore()` 조회 확인

### 5.3 API 연동
- [ ] API 환경변수에 컨트랙트 주소 설정
- [ ] `/v1/contract/update-score` 엔드포인트 테스트
- [ ] 이벤트 리스너 동작 확인

---

## 6. 모니터링 설정

### 6.1 알림 설정
- [ ] Owner 키 사용 트랜잭션 알림
- [ ] 비정상 업데이트 패턴 감지
- [ ] 가스비 급등 알림

### 6.2 대시보드
- [ ] Dune Analytics 쿼리 작성 (optional)
- [ ] 에이전트 수, 업데이트 빈도 추적

---

## 7. 롤백 계획

### 7.1 문제 발생 시
1. 즉시 `pause()` 호출 (구현 필요시 추가)
2. 원인 분석
3. 수정된 Implementation 배포
4. `upgradeToAndCall()` 실행

### 7.2 최악의 경우
- 새 Proxy 배포 후 마이그레이션
- 기존 데이터는 조회만 가능하도록 유지

---

## 체크리스트 완료 확인

| 단계 | 상태 | 담당 | 완료일 |
|:-----|:----:|:-----|:------|
| 컨트랙트 설계 | ✅ | Droid | 2026-01-29 |
| Slither 분석 | ⏳ | | |
| 단위 테스트 | ⏳ | | |
| 하드웨어 월렛 준비 | ⏳ | User | |
| 테스트 ETH 확보 | ⏳ | User | |
| Base Sepolia 배포 | ⏳ | | |
| Basescan 검증 | ⏳ | | |
| API 연동 테스트 | ⏳ | | |

---

**다음 단계**: Slither 정적 분석 실행
