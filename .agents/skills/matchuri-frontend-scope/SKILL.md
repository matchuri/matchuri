---
name: matchuri-frontend-scope
description: Matchuri 작업을 frontend-only 범위로 제한한다. 화면, frontend API 연결, domain type, hook, 상태 처리, UI 리팩터링처럼 프론트엔드 담당자가 frontend와 직접 관련 문서만 수정하고 backend 변경은 계약 불일치와 후속 작업 보고로 남겨야 할 때 사용한다.
---

# Matchuri Frontend Scope

이 스킬은 작업 방법이 아니라 수정 범위를 결정한다. 함께 사용하는 구현, 리뷰, 동기화 스킬은 이 범위를 확장할 수 없다.

## 범위

- `frontend/**`를 수정한다.
- 변경된 frontend 동작이나 기준에 직접 관련된 `docs/frontend/**`만 함께 수정한다.
- 루트 공용 설정, 다른 문서, repo-local skill은 사용자가 해당 변경을 요청한 경우에만 수정한다.
- 계약 확인과 영향 분석을 위해 `backend/**`와 `docs/api/**`를 읽을 수 있지만 수정하지 않는다.

## 경계

- `backend/**`를 수정하지 않는다.
- Controller, request/response DTO, service, domain model, entity, migration, backend config와 test를 수정하지 않는다.
- OpenAPI metadata와 `docs/api/**`의 API 계약을 임의로 변경하지 않는다.
- 다른 스킬이 backend 변경을 안내하더라도 실행하지 않는다.
- 범위 밖 변경이 완료에 필요하면 임의로 범위를 넓히지 말고 후속 작업으로 보고한다.

## API 연결

1. backend code, OpenAPI metadata와 `docs/api/**`에서 현재 계약을 확인한다.
2. frontend API client, domain type, application logic와 UI를 현재 계약에 맞춘다.
3. frontend adapter 또는 mapping으로 해결 가능한 차이만 frontend 안에서 처리한다.
4. backend 계약 변경이 필요하면 필요한 endpoint, field, error code를 기록하고 backend를 수정하지 않는다.

BE와 FE를 한 작업에서 함께 변경하라는 명시적 요청이 있으면 이 스킬 대신 `matchuri-api-contract-sync`를 사용한다.

## 충돌 처리

- `matchuri-backend-scope`가 함께 요청되면 서로 충돌하므로 수정 전에 범위를 확인한다.
- `matchuri-api-contract-sync`가 함께 사용돼도 사용자가 cross-stack 수정을 명시하지 않았다면 frontend-only 범위를 유지한다.

## 보고

- 수정한 frontend 영역과 관련 문서
- 실행한 frontend 검증
- 발견한 API 계약 불일치와 필요한 backend 후속 작업
- 의도적으로 수정하지 않은 backend 영역

