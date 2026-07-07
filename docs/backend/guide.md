# 백엔드 가이드

이 문서는 Matchuri 백엔드 구현 작업의 실무 기준입니다.
제품 판단은 `docs/product/product-sense.md`, 전체 아키텍처와 운영 방향은 `docs/backend/architecture.md`, 코드 품질 판단은 `docs/decisions/backend-code-quality.md`를 기준으로 봅니다.

## 역할

`docs/backend/guide.md`는 아래 질문에 답하는 문서입니다.

- 새 백엔드 코드를 어느 패키지에 둘 것인가
- API DTO, 서비스 입출력 모델, 엔티티 책임을 어떻게 나눌 것인가
- 유스케이스, 보조 로직, 예외, 트랜잭션 경계를 어디에 둘 것인가
- 백엔드 변경 시 어떤 검증을 기본으로 볼 것인가

백엔드의 도메인 흐름, 인프라 채택/비채택 판단, 기술 선택 배경은 `docs/backend/architecture.md`에 중복 작성하지 않습니다.

## 기본 방향

- Spring Boot 4, Java 21, Gradle, Spring Data JPA, MySQL 기준으로 작성합니다.
- 초기 구현은 운영 가능한 단순함을 우선합니다.
- Redis, Docker, 복잡한 분산 구조는 필요가 분명해질 때 도입합니다.
- 새 작업은 검증 가능한 얇은 세로 슬라이스로 진행합니다.

## 패키지 구조

백엔드는 `api`, `domain`, `global`, `infra` 축으로 나눕니다.

```text
backend/src/main/java/matchuri/backend
├─ api
├─ domain
├─ global
└─ infra
```

### `api/<domain>`

- Controller
- 요청/응답 DTO
- Mapper
- Swagger/OpenAPI 메타데이터 인터페이스

역할:

- HTTP 요청/응답 처리
- 입력 검증
- 인증 경계 처리
- API 계약에 맞는 DTO 사용

### `domain/<domain>`

새 도메인이나 리팩토링 대상 도메인은 아래 골격을 기본값으로 삼습니다.

```text
domain/<domain>
├─ service
├─ command
├─ result
├─ support
├─ exception
├─ entity
└─ repository
```

- 모든 도메인이 처음부터 모든 하위 패키지에 구현 클래스를 가져야 하는 것은 아닙니다.
- 빈 패키지를 Git에 남겨야 할 때만 `.gitkeep`를 사용합니다.
- 실제 클래스가 추가된 패키지에서는 `.gitkeep`를 제거합니다.
- `package-info.java`는 패키지 설명이나 패키지 어노테이션이 실제로 필요할 때만 사용합니다.

### `global`

- 공통 응답 형식
- 공통 예외 처리
- 보안 공통 설정
- 전역 설정과 공통 유틸리티

도메인 규칙 자체를 `global`로 올리지 않습니다.

### `infra`

- 외부 시스템 연동
- 기술 구현 세부사항
- 배포/런타임 환경과 가까운 어댑터

도메인 판단을 `infra`에 숨기지 않습니다.

## 도메인 내부 책임

### `service`

역할:

- API나 다른 도메인이 호출하는 유스케이스 진입점
- 여러 `support`, `repository`, `entity`를 조합하는 흐름 제어
- 쓰기 유스케이스의 트랜잭션 경계
- 상태 전이 관리

두지 않는 것:

- 단순 DTO 변환
- command/result 모델
- 여러 유스케이스에서 반복되는 검증, 조회 조합, 계산 로직

경고 신호:

- public 메서드가 계속 늘어난다
- private helper가 public 메서드보다 많아진다
- 같은 repository 조회 패턴이나 예외 번역이 반복된다
- "현재 회원 조회", "필수 조건 확인", "정책 계산" 같은 문장이 여러 메서드에 반복된다

### `command`

- 서비스 유스케이스 입력 모델입니다.
- API request DTO와 분리합니다.
- request DTO 검증 어노테이션을 직접 들지 않습니다.
- 여러 유스케이스가 공유하더라도 진짜 공통 의미가 아니면 섣불리 합치지 않습니다.

### `result`

- 서비스 유스케이스 출력 모델입니다.
- API response DTO가 아니라 도메인 유스케이스 결과를 표현합니다.
- 한 서비스 인터페이스에만 쓰이더라도 `service`에 섞지 않고 `result`에 둡니다.

### `support`

역할:

- 여러 유스케이스에서 재사용하는 도메인 지원 로직
- 조회 조합, 검증, 계산, 정책 판단
- `service`가 비대해지지 않도록 반복 책임 흡수

승격 기준:

- 최소 2개 이상의 유스케이스에서 같은 책임이 반복된다
- 유스케이스 이름보다 도메인 개념 이름으로 설명하는 편이 자연스럽다
- 단독 테스트 가치가 있다
- controller, security, auth 같은 다른 경계에서도 재사용될 가능성이 있다

하위 패키지는 기술명보다 도메인 의미를 우선합니다.
`common`, `util`, `helper` 같은 포괄 이름은 가능한 한 피합니다.

네이밍 기준:

- 조회 조합: `Reader`, `Finder`, `Loader`
- 검증: `Validator`
- 계산/해석: `Resolver`, `Calculator`
- 규칙 묶음: `Policy`

### `exception`

- 도메인 전용 `ErrorCode`와 필요 시 도메인 전용 예외를 둡니다.
- 예외 코드는 도메인 규칙과 함께 진화하므로 API 패키지나 `global` 패키지로 올리지 않습니다.
- 서비스, 지원 컴포넌트, 다른 도메인이 같은 에러 언어를 사용하도록 유지합니다.

### `entity`

- JPA 매핑과 도메인 상태를 표현합니다.
- 검증 로직과 비즈니스 로직을 모두 엔티티에 몰아넣지 않습니다.
- 공통 감사 컬럼은 `BaseEntity`, `CreatedAtEntity`를 사용합니다.
- 유니크 제약, 인덱스, enum 저장 방식은 스키마 문서와 맞춥니다.

### `repository`

- 단순 조회/저장은 기본 `JpaRepository`로 시작합니다.
- 복잡한 동적 조건, 화면/유스케이스 전용 조회 모델, 쿼리 조립 책임이 분명해질 때만 Custom Repository를 검토합니다.

## 선행 예시

현재 `member`, `auth` 도메인은 새 구조의 기준 예시로 봅니다.

- `api/member`: Controller, DTO, Mapper
- `domain/member/service`: 회원/약관 관련 유스케이스 진입점
- `domain/member/command`, `domain/member/result`: 서비스 입출력 모델
- `domain/member/support`: 활성 회원 조회, 필수 약관 검증, 리비전 계산
- `domain/member/exception`: 회원/약관 에러 코드
- `domain/auth/service`: 인증 유스케이스 진입점
- `domain/auth/support/oauth2`: OAuth2 사용자 정보 해석과 소셜 회원 연결 보조
- `domain/auth/support/token`: JWT, refresh token, cookie 처리
- `domain/auth/exception`: 인증 에러 코드

새 도메인은 이 예시의 책임 분리를 따르되, 필요 없는 클래스를 억지로 만들지 않습니다.

## DTO 규칙

DTO는 아래 패키지 기준으로 구분합니다.

- `api/<domain>/dto/request`
- `api/<domain>/dto/response`
- `api/<domain>/dto/docs`

역할:

- `request`: 실제 입력 DTO
- `response`: 실제 런타임 `data` payload DTO
- `docs`: Swagger/OpenAPI 명세를 정확하게 표현하기 위한 문서 전용 DTO

`MemberResponse` 같은 응답 DTO는 공통 응답 전체가 아니라 `data` payload만 의미합니다.
공통 응답 구조(`success/data/error`)는 별도 공통 응답 객체에서 관리합니다.

문서 전용 DTO는 실제 컨트롤러 반환 타입을 바꾸기 위한 것이 아니라, Swagger 산출물의 schema와 예시를 실제 응답 구조에 가깝게 맞추기 위한 용도입니다.
API 문서화 세부 전략은 `docs/decisions/api-docs-strategy.md`를 기준으로 봅니다.

## Mapper 규칙

- Mapper는 DTO와 Entity/Result 변환 전용입니다.
- 비즈니스 로직, 조회 로직, 상태 판단 로직은 Mapper에 넣지 않습니다.
- 응답을 위해 여러 도메인 객체를 조합하는 책임은 Mapper보다 Service 쪽이 더 적절합니다.

## 인터페이스 규칙

- `service` 진입점은 기본적으로 인터페이스를 유지합니다.
- `support`는 구현체가 하나이고 mocking 이득이 작으면 concrete class로 둡니다.
- repository, 외부 연동, provider처럼 구현이 늘 가능성이 있는 경계에서만 인터페이스를 적극 검토합니다.
- 구현체가 하나뿐인 인터페이스를 습관적으로 늘리지 않습니다.

현재 기본 판단:

- `MemberService`, `MemberAgreementService`: 인터페이스 유지
- `ActiveMemberReader`, `RequiredAgreementRevisionResolver`: concrete class 우선

## 의존 방향

기본 흐름:

```text
api -> domain/<domain>/service -> command/result/support/repository/entity
```

허용:

- `service -> command/result/support`
- `service -> repository`
- `support -> repository`
- `service`, `support`가 같은 도메인의 `exception`을 사용하는 것
- `auth`나 `security` 같은 다른 도메인/공통 모듈이 필요한 `service` 또는 `support`를 사용하는 것

피할 것:

- `support -> service`
- `entity -> repository`
- `api dto -> entity` 직접 노출
- `support`가 컨트롤러 요청/응답 DTO를 아는 구조

## 트랜잭션 규칙

- 쓰기 유스케이스의 `@Transactional` 기본 위치는 `service`입니다.
- 단순 조회 유스케이스는 `readOnly = true`를 우선합니다.
- `support`는 가능하면 트랜잭션을 시작하지 않고 호출한 `service`의 경계를 따릅니다.
- 독립 배치나 별도 경계가 분명한 경우에만 `support` 자체 트랜잭션을 예외적으로 허용합니다.

## 검증 로직

- 현재는 검증 로직을 과도하게 추상화하지 않습니다.
- 단일 API에만 필요한 검증은 Controller나 가까운 구현 위치에 둘 수 있습니다.
- 같은 검증이 여러 API나 계층에서 반복될 때만 `Validator`, `Policy`, custom validation으로 승격합니다.
- 핵심 기준은 "이 검증이 정말 여러 곳에서 반복되는가"입니다.

## API 구현

- 구현 계약은 코드와 함께 유지되는 OpenAPI 메타데이터와 Swagger 산출물을 우선 기준으로 봅니다.
- 요청/응답 구조는 `success/data/error` 형태를 유지합니다.
- 인증 필요 여부를 엔드포인트마다 분명히 구분합니다.
- 상태 변경 API는 중복 호출, 권한 없음, 상태 충돌 케이스를 먼저 생각합니다.

API 문서화 전략과 업데이트 순서는 `docs/decisions/api-docs-strategy.md`, API 흐름 설명은 `docs/api/index.md`를 기준으로 봅니다.

비즈니스 로직 구현 전에 Swagger 계약과 프론트엔드 연동을 먼저 열어야 하는 API는 Mock API 계약 우선 개발 방식을 사용할 수 있습니다.
이때 Controller는 service를 호출하지 않고 response DTO의 명시적 mock factory를 반환하며, Swagger에는 mock 상태임을 표시합니다.
세부 기준은 `docs/decisions/mock-api-contract-first.md`를 봅니다.

## 설정 바인딩

- 외부 설정의 기준값은 `application.yaml`과 프로필별 `application-<profile>.yaml`에 둡니다.
- 환경 변수는 YAML에서 `${ENV_NAME:default}` 형태로 읽고, 운영 환경에서는 환경 변수나 안전한 주입 방식으로 덮어씁니다.
- `@ConfigurationProperties` 클래스는 설정 구조를 표현하는 역할에 집중합니다.
- 같은 기본값을 YAML과 자바 필드 양쪽에 중복 선언하지 않습니다.
- 필수 설정은 자바 필드 초기값으로 숨기지 말고, 누락 시 기동 실패가 나도록 검증합니다.
- 보안 민감값은 개발 편의를 위한 기본값이 운영으로 흘러가지 않도록 주의합니다.

## 예외 처리

- 에러 코드는 도메인 prefix 기준으로 통일합니다.
- 잘못된 요청은 4xx, 서버 내부 문제는 5xx로 구분합니다.
- 내부 클래스명, SQL, 스택트레이스는 응답에 노출하지 않습니다.
- 예외는 공통 응답 형식과 연결되어야 합니다.

보안/신뢰성 관점의 상세 기준은 `docs/backend/security.md`, `docs/backend/reliability.md`를 함께 봅니다.

## 점진적 이전

- 기존 `application` 구조는 과도기 상태로 보고 새 파일은 원칙적으로 추가하지 않습니다.
- 기존 파일을 수정할 때는 기능 변경 범위를 넘지 않는 선에서 `service`/`command`/`result`/`support`/`exception` 이동을 함께 검토합니다.
- 전 도메인 일괄 이동보다, 수정하는 도메인 단위로 얇게 이전합니다.
- 과도기 디렉터리가 비면 바로 정리해 현재 기준과 실제 구조가 어긋나지 않게 유지합니다.

## Seed 데이터

로컬 환경에서 API를 빠르게 검증할 수 있도록 시드 데이터를 사용할 수 있습니다.
운영 사고를 막기 위해 아래 원칙을 지킵니다.

- 로컬 Docker Compose DB는 최초 빈 volume 생성 시 `backend/init/sql/*.sql`로 테이블과 기준/샘플 seed를 준비합니다.
- 애플리케이션 기동 시점의 ApplicationRunner seed는 사용하지 않습니다.
- `prod`에서는 자동 실행되지 않도록 막습니다.
- 같은 초기화가 여러 번 실행돼도 데이터가 중복 생성되지 않아야 합니다.
- 기준 데이터(reference data)와 개발 편의용 샘플 데이터(sample data)를 구분합니다.
- 멱등성은 SQL의 유니크 키와 `ON DUPLICATE KEY UPDATE` 기준으로 보장합니다.

현재 기준:

- Docker init SQL 경로: `backend/init/sql/`
  - `01-schema.sql`: 로컬 MySQL 테이블, 인덱스, FK 생성
  - `02-reference-seed.sql`: 메뉴 기준 데이터와 매핑 seed
  - `03-local-sample-seed.sql`: 로컬 테스트 회원과 약관 동의 seed
- 로컬 DB 볼륨을 유지하는 Docker Compose 환경에서는 최초 `docker compose up` 시 init SQL을 실행하고, 이후 일반 실행은 `local`만 사용합니다.
- 로컬 수동 테스트용 샘플 계정과 관리자 계정은 개발 환경에서만 생성합니다.

기준 데이터와 스키마 세부 내용은 `docs/data/index.md`, `docs/data/implemented-jpa-data-model.md`를 기준으로 봅니다.

## 테스트

- 최소 기준: `./gradlew test`
- 커버리지 리포트가 필요하면 `./gradlew test jacocoTestReport`
- JaCoCo HTML: `backend/build/reports/jacoco/test/html/index.html`
- JaCoCo XML: `backend/build/reports/jacoco/test/jacocoTestReport.xml`
- 도메인 저장소와 상태 전이는 테스트 우선순위가 높습니다.
- 새 API를 추가하면 정상 흐름과 대표 실패 케이스를 함께 검증합니다.
- API 계약 변경 시 OpenAPI 메타데이터, Swagger 산출물, 관련 `docs/api/` 설명을 같이 확인합니다.
- Swagger/OpenAPI 산출물을 직접 검증하는 전용 테스트는 작성하지 않습니다. 계약 변경 검증은 실제 API 동작 테스트와 문서 확인으로 처리합니다.

## 리뷰 체크리스트

- 이 클래스는 외부 진입점인가, 내부 재사용 보조 로직인가
- 이 검증/조회/계산은 다른 유스케이스에서도 반복되는가
- `support` 이름이 도메인 의미를 설명하는가
- command/result가 API DTO 역할까지 떠안고 있지 않은가
- 트랜잭션 경계가 `service`에 남아 있는가
- 인터페이스가 실제 변동 지점 때문에 필요한가
- Swagger 문서용 DTO와 실제 런타임 DTO가 섞이지 않았는가
