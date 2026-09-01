---
name: matchuri-backend-api-change
description: Matchuri backend API 계약 변경을 구현하거나 검토한다. Spring Boot endpoint, request/response DTO, Swagger/OpenAPI metadata, controller mapping, API docs, backend 및 docs/api 테스트를 추가, 제거, 폐기, 수정할 때 사용한다.
---

# Matchuri Backend API 변경

backend가 소유한 API 변경에 사용한다. Controller, DTO, Swagger metadata, service wiring, tests, `docs/api`를 함께 맞춘다.

## 범위

아래 작업에 사용한다.

- 신규 endpoint
- endpoint path/method 변경
- request/response DTO 변경
- error code 또는 failure envelope 변경
- mock API에서 real API로 전환
- deprecation 처리
- Swagger/OpenAPI metadata 변경

frontend-only API consumption에는 사용하지 않는다. backend와 frontend가 함께 움직이면 `matchuri-api-contract-sync`를 사용한다.

## 먼저 읽을 것

1. Root `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/api/index.md`
4. `docs/decisions/api-docs-strategy.md`
5. endpoint가 mock이거나 mock에서 전환 중이면 `docs/decisions/mock-api-contract-first.md`
6. domain별 `docs/api/*.md`

구현 기준을 찾기 위해 GitHub Wiki나 local Wiki folder를 읽지 않는다.

## 절차

1. API surface를 식별한다.
   - Domain
   - API ID
   - HTTP method
   - Path
   - Auth requirement
   - Status: `planned`, `mock`, `real`, or `deprecated`

2. backend API layer를 갱신한다.
   - `backend/src/main/java/matchuri/backend/api/<domain>/*Api.java`
   - `*Controller.java`
   - `dto/request`
   - `dto/response`
   - `dto/docs`
   - service command/result 변환이 필요하면 Mapper
   - `OpenApiConfig.API_OPERATION_METADATA`의 API ID와 flow tag

3. DTO 책임을 분리한다.
   - request DTO: HTTP input과 Bean Validation
   - response DTO: runtime `data` payload
   - docs DTO: Swagger envelope/schema/example 전용
   - command/result: service boundary model

4. 필요한 만큼만 domain/service를 갱신한다.
   - `real` API의 Controller는 service를 호출한다.
   - `mock` API의 Controller는 명시적 response DTO mock factory를 반환할 수 있다.
   - business rule을 Mapper나 docs DTO에 숨기지 않는다.

5. API docs를 갱신한다.
   - 권한, 만료, 상태 전이처럼 코드만으로 설명되지 않는 정책이 바뀔 때만 관련 `docs/api/*.md`
   - numbering policy가 바뀔 때만 `docs/api/api-numbering-policy.md`

6. 검증한다.
   - root에서 `python backend\scripts\audit_api_contract.py --root backend --strict`를 실행한다.
   - 개발 중에는 변경 영향에 가장 가까운 service/domain test와 필요한 controller integration test를 `--tests`로 좁게 실행한다.
   - 마지막 동작 변경 후 `backend`에서 `./gradlew test --quiet`를 1회 이상 성공시킨다. 실패를 고친 뒤에는 다시 실행한다.
   - 실패 원인 분석에 상세 로그가 필요할 때만 해당 test를 `--quiet` 없이 다시 실행한다.
   - frontend 영향은 보고하되 frontend 코드를 수정하지 않는다.
   - 사용자가 BE와 FE 동시 수정을 명시한 경우에만 `matchuri-api-contract-sync`를 사용한다.

## Swagger 규칙

- operation metadata는 `*Api.java`에 둔다.
- runtime mapping은 Controller에 둔다.
- success와 대표 failure의 실제 envelope example을 보여준다.
- 구현의 실제 error code를 사용한다.
- mock API는 operation description에 명확히 표시한다.
- `real`로 전환할 때 mock 표현을 제거하거나 수정한다.

## API Registry 규칙

- public `/api/v1/**` API contract마다 `OpenApiConfig.API_OPERATION_METADATA` entry 하나를 추가한다.
- 기존 API ID를 재사용하지 않는다.
- 제거됐지만 호출 가능한 API는 `@Operation(deprecated = true)`로 표시한다.
- method/path/API ID 목록을 별도 문서에 복사하지 않는다.

## 완료 Checklist

- Controller mapping이 docs 및 Swagger와 일치한다.
- Request validation이 docs와 일치한다.
- Response DTO가 frontend contract와 일치한다.
- Error envelope example이 실제 error code와 일치한다.
- `OpenApiConfig.API_OPERATION_METADATA`의 API ID와 flow tag가 갱신됐다.
- 관련 `docs/api/*.md`가 갱신됐다.
- Backend tests를 실행했거나 실행하지 못한 이유를 보고했다.
