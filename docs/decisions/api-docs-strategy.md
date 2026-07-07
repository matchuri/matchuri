# API 문서화 전략

이 문서는 Matchuri 백엔드의 현재 API 문서화 전략을 정리합니다.
지금 단계의 목표는 문서화 방식을 이상적으로 나누는 것보다, 2인 팀이 실제로 유지 가능한 방식으로 계약을 빠르게 맞추는 것입니다.

## 목표

Matchuri의 API 문서는 아래 조건을 함께 만족해야 합니다.

- Swagger UI에서 바로 탐색 가능해야 합니다.
- 구현 코드와 문서가 쉽게 어긋나지 않아야 합니다.
- 요청값 제약, 인증 필요 여부, 대표 실패 케이스가 명확히 보여야 합니다.
- 문서 유지 비용이 팀 규모 대비 과도하게 커지지 않아야 합니다.

## 현재 기본 전략

- 문서 작성 중심: Swagger/OpenAPI
- 조회/탐색 UI: Swagger UI
- 보조 검증: 실제 API 동작 테스트, 필요한 경우 REST Docs 스니펫

즉, 현재 Matchuri는 REST Docs-first보다 Swagger UI 중심 운영에 가깝습니다.
계약 설명은 코드 인접 OpenAPI 메타데이터와 `docs/api/` 문서가 만들고, 테스트는 Swagger/OpenAPI 산출물 자체가 아니라 실제 API 동작을 확인하는 역할에 집중합니다.

## 왜 이 전략을 선택하는가

- 현재 저장소는 `AuthApi`, `MemberApi`, `MemberAgreementApi`처럼 Swagger 메타데이터를 인터페이스에 두는 구조가 이미 자리 잡고 있습니다.
- 팀이 실제로 가장 자주 확인하는 산출물은 `/docs/openapi`, `/docs/swagger-ui.html`, 그리고 `docs/api/` 문서입니다.
- 지금 단계에서 REST Docs 파이프라인까지 강하게 밀어붙이는 것보다, Swagger 산출물을 정확하게 유지하는 편이 운영 효율이 높습니다.
- 2인 팀에서는 "문서 생성 체계의 이상형"보다 "누가 봐도 지금 계약이 어디에 있는지 바로 아는 구조"가 더 중요합니다.

## Source Of Truth

현재 기준은 아래 순서로 봅니다.

1. 구현 코드와 함께 유지되는 OpenAPI 메타데이터
2. 실제 `/docs/openapi` 산출물과 Swagger UI
3. `docs/api/` 아래 현재 기준 문서
4. 관련 테스트

주의:

- 테스트는 중요하지만, 현재 단계에서 문서 작성의 1차 입력 원천은 Swagger 메타데이터입니다.
- Swagger/OpenAPI 산출물을 직접 검증하는 전용 테스트는 작성하지 않습니다.
- 테스트는 도메인 정책, API 동작, 대표 정상/실패 흐름을 검증하는 데 사용합니다.

## 역할 분리

### Swagger/OpenAPI

- 현재 계약의 주된 표현 수단입니다.
- 경로, 메서드, 요청 스키마, 응답 스키마, 인증 필요 여부, 예시를 드러냅니다.
- 프론트와 백엔드가 가장 빠르게 합의하는 화면은 Swagger UI라고 가정합니다.

### `docs/api/`

- Swagger UI만으로 설명이 부족한 맥락을 보완합니다.
- 플로우 설명, 운영 전제, 상태 해석 기준, 예외적 주의사항을 문장으로 정리합니다.
- 여러 API를 묶어 읽어야 이해되는 도메인 흐름은 `docs/api/` 문서에서 설명합니다.

### 테스트

- 대표 정상/실패 흐름을 고정합니다.
- 특히 공개 API/보호 API 구분, 공통 envelope 구조, 핵심 에러 코드 같은 회귀 위험이 큰 부분을 검증합니다.
- Swagger/OpenAPI 메타데이터와 산출물을 대상으로 한 전용 테스트는 만들지 않습니다.

### REST Docs

- 현재는 선택적 보조 수단입니다.
- 이미 작성된 스니펫이나 특정 제약 설명이 유용한 영역에서는 활용할 수 있습니다.
- 다만 현재 운영 기준은 "REST Docs를 먼저 만들고 Swagger UI를 그 결과로만 생성한다"가 아닙니다.

## DTO 배치 원칙

Swagger UI 중심으로 문서화할 때도, 실제 런타임 DTO와 문서 전용 DTO를 같은 폴더에 섞어 두지 않습니다.

현재 Matchuri 권장 구조:

- `api/<domain>/dto/request`
- `api/<domain>/dto/response`
- `api/<domain>/dto/docs`

의미:

- `request`: 실제 요청 body/path/query를 표현하는 입력 DTO
- `response`: 실제 런타임 `data` payload를 표현하는 DTO
- `docs`: Swagger/OpenAPI schema를 정확하게 표현하기 위한 문서 전용 DTO

예:

- `LoginRequest` -> `dto/request`
- `LoginResponse` -> `dto/response`
- `LoginApiResponse` -> `dto/docs`

이렇게 나누는 이유:

- 폴더만 봐도 런타임 모델과 문서용 모델의 책임 경계가 드러납니다.
- envelope wrapper 같은 문서 전용 DTO가 늘어나도 `dto` 루트가 지저분해지지 않습니다.
- 새 팀원이나 에이전트가 Swagger 전용 모델을 실제 응답 DTO로 오해할 가능성을 줄일 수 있습니다.

## 문서 메타데이터 위치 원칙

친절한 Swagger UI를 만들되 컨트롤러 구현을 과도하게 오염시키지 않는 구조를 유지합니다.

현재 Matchuri 권장 방식:

- `*Api` 인터페이스:
  - `@Tag`
  - `@Operation`
  - `@ApiResponses`
  - 필요한 `@Parameter`
- Controller:
  - `@RequestMapping`, `@GetMapping`, `@PostMapping` 같은 실제 HTTP 매핑
  - 입력 검증
  - 서비스 호출
- DTO:
  - 필드 설명
  - example
  - Bean Validation

이 방식의 장점:

- 구현부와 문서 메타데이터를 어느 정도 분리할 수 있습니다.
- Swagger UI에서 계약을 모아보기가 쉽습니다.
- 컨트롤러는 유스케이스와 입력 처리에 집중할 수 있습니다.

## 명세서다운 Swagger UI 기준

Swagger UI가 단순한 경로 목록을 넘어 명세서처럼 쓰이려면 아래 정보가 보여야 합니다.

- 요청 경로와 HTTP Method
- 인증 필요 여부
- 요청값의 의미와 필수 여부
- 요청값의 제약 조건
- 정상 응답 구조
- 공통 envelope 구조
- 대표 실패 케이스와 에러 코드

특히 요청값 제약 조건은 아래 수준까지 드러내는 것을 권장합니다.

- 길이 제한
- 허용 문자 집합
- 정규식 패턴
- enum 값
- 공백 허용 여부
- 허용 예시와 비허용 예시

예:

- `loginId` path variable이면 길이, 패턴, 허용 문자, 금지 예시를 함께 적습니다.
- `nickname`이면 공백만 허용되지 않는 점과 최대 길이를 함께 적습니다.

## 응답 문서화 원칙

Matchuri는 공통 응답 envelope(`success`, `data`, `error`)를 사용합니다.
따라서 Swagger UI도 payload DTO만 보여주지 말고, 실제 응답 envelope이 보이도록 유지해야 합니다.

권장 방식:

- 성공 응답 예시는 실제 envelope JSON 형태로 작성합니다.
- 성공 응답 schema도 가능하면 envelope wrapper를 가리키도록 맞춥니다.
- 실패 응답은 대표 에러 코드와 메시지 예시를 함께 둡니다.

실무 팁:

- 제네릭 `ApiResponse<T>`만으로 산출물이 모호해지면 문서 전용 wrapper DTO를 두는 방식을 허용합니다.
- 예: `LoginApiResponse`, `RegisterLocalMemberApiResponse`

## 실패 응답 Example Value 관리 원칙

Swagger UI의 code별 Example Value는 프론트엔드가 실패 분기 처리를 확인하는 첫 화면입니다.
따라서 실패 응답은 `responseCode`와 `description`만 두지 말고, 가능한 한 실제 런타임 envelope 예시를 함께 둡니다.

기본 원칙:

- 실패 응답 예시는 실제 `ApiResponse.failure(...)` 구조와 맞춥니다.
- `error.code`는 실제 `ErrorCode#getCode()` 결과와 맞춥니다.
- `error.message`는 실제 기본 메시지 또는 `format(...)` 결과와 맞춥니다.
- `error.details`는 없는 경우에도 빈 배열 `[]`로 둡니다.
- Bean Validation, path/query/body 검증 실패는 `COMMON_INVALID_*` 코드와 `details` 배열 구조를 보여줍니다.
- 인증 실패는 `AUTH_TOKEN_MISSING`, `AUTH_TOKEN_INVALID`, `AUTH_TOKEN_EXPIRED`처럼 실제 발생 가능한 토큰 코드를 우선 예시로 둡니다.
- 권한 실패는 단순 관리자 권한 부족과 온보딩 차단을 구분합니다. 예: `AUTH_FORBIDDEN`, `MEMBER_AGREEMENT_REQUIRED`, `MEMBER_NICKNAME_REQUIRED`

code별 예시 선택 기준:

- 한 HTTP status에 도메인 코드가 여러 개면, 프론트 분기나 사용자 안내가 달라지는 코드는 각각 예시를 둡니다.
- 같은 프론트 처리를 공유하는 유사 코드는 대표 예시 하나만 두고 설명에 나머지 가능 코드를 적을 수 있습니다.
- 새 실패 코드를 추가하거나 예외 매핑을 바꾸면 `*Api`의 Example Value와 관련 `docs/api/` 문서를 함께 확인합니다.
- 단순히 Swagger 화면을 예쁘게 보이게 하려고 실제로 발생하지 않는 코드를 넣지 않습니다.

## 인증 표기 원칙

- 인증이 필요한 API는 Bearer 토큰 기준으로 문서화합니다.
- 공개 API는 Swagger 산출물에 operation-level `security: []`가 드러나도록 유지합니다.
- 구현에서 permitAll인데 Swagger UI가 인증 필요처럼 보이면 문서가 어긋난 것으로 간주합니다.

## 테스트 운영 원칙

현재 단계에서 테스트는 아래 수준을 최소 기준으로 삼습니다.

- 대표 정상 흐름 1개 이상
- 대표 실패 흐름 1개 이상
- 외부 계약에 영향을 주는 동작은 controller 통합 테스트 또는 service/domain 테스트로 검증
- 실패 응답의 실제 envelope, `error.code`, `error.details` 구조는 필요 시 API 동작 테스트에서 확인

Swagger/OpenAPI 전용 테스트는 작성하지 않습니다. 문서 산출물은 코드 인접 메타데이터, `docs/api/` 문서, 필요 시 로컬 Swagger UI 확인으로 관리합니다.

## 계약 변경 시 업데이트 순서

API 계약이 바뀌면 아래 순서로 맞춥니다.

1. `*Api` 인터페이스와 DTO의 OpenAPI 메타데이터 수정
2. Controller/Service 구현 수정
3. `/docs/openapi`와 Swagger UI 기준 확인
4. 실제 동작을 검증하는 관련 테스트 수정
5. `docs/api/` 설명 문서 수정

실패 응답 계약이 바뀌는 경우에는 아래 항목도 함께 확인합니다.

- 실제 예외 발생 지점에서 어떤 `ErrorCode`가 사용되는지
- Spring Security 필터, `AuthenticationEntryPoint`, `AccessDeniedHandler`가 반환하는 공통 실패 응답
- Bean Validation과 `RequestValidationException`이 반환하는 `details` 배열
- Swagger UI code별 Example Value가 실제 JSON과 같은 envelope를 유지하는지


## 현재 기준 구현 방향

- OpenAPI 조회 경로: `/docs/openapi`
- Swagger UI 경로: `/docs/swagger-ui.html`
- 애플리케이션 경로 기준으로는 `/docs/**`를 공개 접근으로 유지합니다.
- staging/prod 외부 노출 보호는 Nginx Basic Auth로 처리합니다.
- 문서 설명 중심 위치:
  - `backend/src/main/java/.../api/*Api.java`
  - `backend/src/main/java/.../api/**/dto/*.java`
  - `docs/api/*.md`

## 언제 전략을 다시 바꿀까

아래 조건이 분명해지면 REST Docs 비중을 다시 높이는 방향을 검토할 수 있습니다.

- 문서 자동 생성 품질을 테스트 결과에 더 강하게 묶고 싶을 때
- 컨트롤러/인터페이스의 Swagger 메타데이터 양이 과도하게 커질 때
- API 변경 빈도가 높아져 사람 손으로 예시를 유지하는 비용이 커질 때

그 전까지는 현재처럼 Swagger UI 중심 운영을 기본 전략으로 둡니다.
