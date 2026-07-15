---
name: matchuri-api-contract-sync
description: Matchuri backend와 frontend API 계약을 명시적인 cross-stack 범위에서 동기화한다. 사용자가 BE와 FE 동시 수정, frontend consumer 반영, 또는 양쪽 계약 drift 감사를 요청했을 때 backend API, frontend API client와 domain type, hook, docs/api, OpenAPI/Swagger를 함께 점검하거나 수정하는 데 사용한다. backend-only 또는 frontend-only 요청에는 사용하지 않는다.
---

# Matchuri API 계약 동기화

FE/BE contract alignment에 사용한다. 자동 background trigger가 아니라 cross-stack workflow로 취급한다.

## 범위

사용자가 cross-stack 작업 또는 양쪽 drift 감사를 명시한 아래 상황에 사용한다.

- backend endpoint path, method, request, response, error contract가 바뀐다.
- backend에 맞춰 frontend API client 또는 domain type을 바꿔야 한다.
- API status table이 오래됐을 수 있다.
- OpenAPI/Swagger output을 수동 또는 script로 검증해야 한다.
- PR이 `backend/`와 `frontend/`를 함께 건드린다.

상대 영역에 영향이 있다는 사실만으로 이 스킬을 사용하거나 수정 범위를 넓히지 않는다. backend-only 작업에는 `matchuri-backend-scope`와 관련 backend 스킬을 사용하고, frontend-only 작업에는 `matchuri-frontend-scope`를 사용한다.

## 먼저 읽을 것

1. Root `AGENTS.md`
2. backend code가 관련되면 `backend/AGENTS.md`
3. frontend code가 관련되면 `frontend/AGENTS.md`
4. `docs/api/index.md`
5. `docs/api/api-status.md`
6. domain별 `docs/api/*.md`

계약 기준을 찾기 위해 GitHub Wiki나 local Wiki folder를 읽지 않는다.

## 절차

1. 변경된 contract를 식별한다.
   - method와 path
   - request DTO
   - response payload
   - auth requirement
   - error code와 envelope
   - 관련 있으면 streaming/SSE behavior

2. backend/docs drift를 감사한다.

   ```powershell
   python .agents\skills\matchuri-api-contract-sync\scripts\audit_api_contract.py --root .
   ```

   drift finding으로 command를 실패시킬 때만 `--strict`를 사용한다.

3. contract source가 바뀌면 backend를 먼저 갱신한다.
   - `*Api.java`
   - Controller mapping
   - request/response/docs DTOs
   - service tests or controller integration tests
   - `docs/api/api-status.md`
   - 관련 `docs/api/*.md`

4. frontend consumer를 갱신한다.
   - `frontend/src/features/**/infrastructure/api`
   - `frontend/src/features/**/domain`
   - response shape에 의존하는 hooks/usecases/selectors
   - status 또는 error code로 분기하는 UI states

5. 검증한다.
   - Backend: `backend`에서 `./gradlew test`를 실행한다.
   - Frontend: `frontend`에서 `npm run lint`를 실행한다.
   - 사용 가능하거나 명시적으로 필요할 때만 추가 frontend build/type check를 실행한다.

## Contract 규칙

- Backend OpenAPI metadata와 Controller mapping을 implementation contract source로 본다.
- `docs/api/api-status.md`는 coordination table이며 code의 대체물이 아니다.
- Frontend type은 Swagger wrapper DTO를 맹목적으로 따르지 말고 UI가 실제 소비하는 response를 반영한다.
- Error handling은 backend의 실제 `error.code` 값을 사용한다.
- SSE contract는 event name과 payload shape를 모두 확인한다.

## Harness

`scripts/audit_api_contract.py`는 가벼운 static audit를 수행한다.

- backend `/api/v1/**` Controller mapping을 추출한다.
- API status table row를 추출한다.
- duplicate backend endpoint mapping을 보고한다.
- duplicate API ID를 보고한다.
- duplicate status row를 보고한다.
- status table에 없는 backend endpoint를 보고한다.
- backend Controller mapping에서 보이지 않는 status table path를 보고한다.
- frontend `features/**/infrastructure/api` directory를 나열한다.

이 script는 drift detector다. tests 또는 OpenAPI review를 대체하지 않는다.

## 보고

동기화를 끝낼 때 아래를 보고한다.

- 변경한 backend endpoints
- 변경한 frontend API files
- 변경한 docs/status rows
- 실행한 backend/frontend verification commands
- 남은 contract risk
