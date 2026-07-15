---
name: matchuri-backend-scope
description: Matchuri 작업을 backend-only 범위로 제한한다. backend 구현, API 계약, 데이터 모델, 보안, 신뢰성, 리팩터링처럼 백엔드 담당자가 backend와 직접 관련 문서만 수정하고 frontend 변경은 영향 분석과 후속 작업 보고로 남겨야 할 때 사용한다.
---

# Matchuri Backend Scope

이 스킬은 작업 방법이 아니라 수정 범위를 결정한다. 함께 사용하는 구현, 리뷰, 동기화 스킬은 이 범위를 확장할 수 없다.

## 범위

- `backend/**`를 수정한다.
- 변경된 동작이나 계약에 직접 관련된 `docs/backend/**`, `docs/api/**`, `docs/data/**`, `docs/decisions/**`만 함께 수정한다.
- 루트 공용 설정, 다른 문서, repo-local skill은 사용자가 해당 변경을 요청한 경우에만 수정한다.
- 영향 분석을 위해 `frontend/**`를 읽을 수 있지만 수정하지 않는다.

## 경계

- `frontend/**`를 수정하지 않는다.
- frontend API client, domain type, hook, selector, UI, test, config를 수정하지 않는다.
- frontend 전용 문서를 수정하지 않는다.
- 다른 스킬이 frontend 변경을 안내하더라도 실행하지 않는다.
- 범위 밖 변경이 완료에 필요하면 임의로 범위를 넓히지 말고 후속 작업으로 보고한다.

## API 계약 변경

1. backend 구현, OpenAPI metadata, 관련 `docs/api/**`와 backend tests를 갱신한다.
2. 현재 frontend 소비 지점을 읽고 호환성 영향을 확인할 수 있다.
3. 필요한 frontend 변경을 파일 또는 기능 단위로 기록한다.
4. 현재 frontend와 호환되지 않으면 남은 contract risk로 명시한다.

BE와 FE를 한 작업에서 함께 변경하라는 명시적 요청이 있으면 이 스킬 대신 `matchuri-api-contract-sync`를 사용한다.

## 충돌 처리

- `matchuri-frontend-scope`가 함께 요청되면 서로 충돌하므로 수정 전에 범위를 확인한다.
- `matchuri-api-contract-sync`가 함께 사용돼도 사용자가 cross-stack 수정을 명시하지 않았다면 backend-only 범위를 유지한다.

## 보고

- 수정한 backend 영역과 관련 문서
- 실행한 backend 검증
- frontend 영향과 필요한 후속 작업
- 의도적으로 수정하지 않은 frontend 영역

