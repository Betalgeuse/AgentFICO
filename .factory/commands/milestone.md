# milestone

마일스톤 및 이슈 태스크 문서를 자동 생성합니다.

## 사용법
```
/milestone api development
/milestone smart contract
/milestone AF-001 score calculation bug
/milestone frontend dashboard
```

## 동작
1. 기존 docs/orchestrator/milestones/M*.md 파일 확인
2. 자연어를 마일스톤 ID로 변환 (M2-api-development, AF-001 등)
3. feature branch 생성 (feature/M2-xxx 또는 feature/AF-xxx)
4. Linear 이슈 등록 (연동 시)
5. 상세 태스크 명세서 생성

## Agent
이 커맨드는 `milestone-architect` droid를 호출합니다.

---

$ARGUMENTS를 기반으로 마일스톤/이슈 태스크 명세서를 생성해주세요.

**필수 절차:**
1. `docs/orchestrator/milestones/M*.md` 파일들을 확인하여 다음 번호 결정
2. feature branch 먼저 생성 (`feature/M{N}-{slug}` 또는 `feature/AF-{NN}`)
3. Linear 프로젝트에 이슈 등록 (연동 시)
4. `docs/orchestrator/milestones/` 또는 `docs/orchestrator/issues/` 에 명세서 생성

**참조 문서:**
- `.factory/droids/milestone-architect.md` - 전체 가이드라인
- `docs/orchestrator/milestones/M1.md` - 마일스톤 예시
- `docs/ARCHITECTURE.md` - 아키텍처 참조

**AgentFICO Droid 할당:**
| Domain | Droid |
|:---|:---|
| Smart Contract | `web3-smart-contract-auditor` |
| Blockchain Data | `blockchain-data-analyzer` |
| REST API | `web3-api-developer`, `fastapi-pro` |
| DeFi Integration | `defi-protocol-specialist` |
| Testing | `hardhat-test-engineer` |
| Frontend | `vite-react-developer` |
| Linear 관리 | `linear-project-manager` |
