# 회원 필수 온보딩 에러 코드

이 문서는 Matchuri의 회원 필수 약관 동의와 닉네임 온보딩에 대한 현재 에러 코드 기준입니다.
목적은 상태 조회, 동의 제출, 닉네임 설정, 핵심 API 차단 시 어떤 실패를 어떤 코드로 표현하는지 일관되게 정리하는 것입니다.

## 문서 목적

- 필수 약관 동의와 닉네임 온보딩의 대표 실패 케이스를 일관된 코드로 정리합니다.
- 프론트가 미동의 상태, 닉네임 미완료 상태, 버전 불일치, 잘못된 요청을 구분할 수 있게 합니다.
- 인증/인가 실패와 온보딩 미완료 실패를 섞어 쓰지 않도록 기준을 둡니다.

## 현재 전제

- 필수 약관은 `TERMS_OF_SERVICE`, `PRIVACY_POLICY` 두 종류입니다.
- 최신 필수 버전은 서버 상수로 관리합니다.
- 약관 동의 이력은 `member_agreements`에 저장합니다.
- 닉네임 온보딩 완료 여부는 `members.nickname_completed`에 저장합니다.
- 약관 또는 닉네임 온보딩 미완료 회원도 로그인은 가능하지만, 핵심 API는 차단합니다.

## 도메인 prefix

현재 prefix:

- `MEMBER_AGREEMENT_`
- `MEMBER_NICKNAME_`

이유:

- `AUTH_`는 순수 인증 실패에 더 가깝습니다.
- 필수 약관 동의와 닉네임 온보딩은 회원 가입 후 상태와 접근 제어 판단에 가까우므로 회원 도메인 prefix가 더 명확합니다.
- 약관 검증 실패는 `MEMBER_AGREEMENT_`, 닉네임 온보딩 실패는 `MEMBER_NICKNAME_`로 분리합니다.

가정(Assumption):

- 실제 enum 위치는 `member` 도메인 또는 `auth` 도메인 구현 방향에 따라 달라질 수 있습니다.
- 다만 사용자와 프론트가 해석하는 에러 코드는 인증 실패와 구분되는 `MEMBER_` 계열이 더 적절합니다.

## 공통 구분 원칙

- `400`: 요청 형식 또는 필드 검증 실패
- `401`: 인증 실패
- `403`: 로그인은 되었지만 권한 또는 이용 조건이 충족되지 않음
- `404`: 필요한 회원/리소스 조회 실패
- `409`: 현재 서버 기준 상태와 충돌하거나 버전이 맞지 않음

## 에러 코드

### 1. 필수 약관 미완료

- code: `MEMBER_AGREEMENT_REQUIRED`
- http status: `403`
- message template:
  - `필수 약관 동의가 필요합니다.`

설명:

- 로그인은 되었지만 현재 필수 약관 2종의 최신 필수 버전에 모두 동의하지 않은 상태에서 핵심 API를 호출한 경우

사용 예:

- `members/me` 주요 기능
- 취향 프로필 수정
- 개인 추천
- 그룹 생성/참여/투표

### 2. 닉네임 온보딩 미완료

- code: `MEMBER_NICKNAME_REQUIRED`
- http status: `403`
- message template:
  - `닉네임 설정이 필요합니다.`

설명:

- 로그인은 되었고 필수 약관도 완료했지만, 닉네임 온보딩을 완료하지 않은 상태에서 핵심 API를 호출한 경우

사용 예:

- `members/me` 조회
- 취향 프로필 수정
- 개인 추천
- 그룹 생성/참여/투표

예외:

- 닉네임 설정용 `PATCH /api/v1/members/me`는 인증은 필요하지만 닉네임 미완료 상태에서도 호출할 수 있습니다.

### 3. 잘못된 약관 종류

- code: `MEMBER_AGREEMENT_INVALID_TYPE`
- http status: `400`
- message template:
  - `유효하지 않은 약관 종류입니다. agreementType : {0}`

설명:

- `agreementType`이 지원하지 않는 값인 경우

### 4. 필수 약관 누락

- code: `MEMBER_AGREEMENT_REQUIRED_TYPES_MISSING`
- http status: `400`
- message template:
  - `필수 약관 동의 요청이 누락되었습니다. missingTypes : {0}`

설명:

- 동의 제출 요청에 `TERMS_OF_SERVICE`, `PRIVACY_POLICY` 중 일부가 빠진 경우

### 5. 약관 버전 불일치

- code: `MEMBER_AGREEMENT_VERSION_MISMATCH`
- http status: `409`
- message template:
  - `최신 필수 약관 버전과 일치하지 않습니다. agreementType : {0}, requestedVersion : {1}`

설명:

- 요청한 `agreementVersion`이 현재 서버 상수의 최신 필수 버전과 다를 경우

이유:

- 단순 형식 오류보다 "현재 서버가 요구하는 상태와 충돌"에 가깝습니다.

### 6. 약관 상태 조회 대상 회원 없음

- code: `MEMBER_AGREEMENT_MEMBER_NOT_FOUND`
- http status: `404`
- message template:
  - `약관 상태를 조회할 회원을 찾을 수 없습니다. memberId : {0}`

설명:

- 인증된 회원을 기준으로 조회했지만 실제 회원이 존재하지 않거나 비정상 상태인 경우

가정(Assumption):

- 대부분은 기존 `MEMBER_NOT_FOUND`를 재사용해도 충분할 수 있습니다.
- 다만 약관 동의 API 문맥에서 별도 코드를 둘지 구현 시점에 최종 확정할 수 있습니다.

### 7. 약관 동의 저장 실패

- code: `MEMBER_AGREEMENT_SAVE_FAILED`
- http status: `500` 또는 `502`
- message template:
  - `약관 동의 저장 중 오류가 발생했습니다.`

설명:

- 저장소 오류, 예기치 않은 중복 충돌 처리 실패 등 내부 오류

운영 메모:

- DB 저장 실패는 일반적으로 `500`으로 시작하는 편이 자연스럽습니다.

## 기존 공통 코드와의 관계

아래 케이스는 새 코드를 만들기보다 기존 공통 코드를 재사용하는 편이 자연스럽습니다.

- 인증 토큰 누락:
  - `AUTH_TOKEN_MISSING`
- 인증 토큰 무효:
  - `AUTH_TOKEN_INVALID`
- 로그인되지 않은 상태:
  - `AUTH_UNAUTHORIZED` 또는 동등 코드
- 요청 body 형식 전체가 잘못된 경우:
  - `COMMON_INVALID_BODY_FIELD`

즉, 약관 동의 기능은 "인증 이후의 상태와 버전 검증"을 중심으로 별도 코드를 갖고, 인증 실패 자체는 기존 `AUTH_` 코드를 유지하는 방향이 적절합니다.

## API별 대표 매핑

### `GET /api/v1/member-agreements/required-status`

- 인증 없음:
  - `401`
  - `AUTH_TOKEN_MISSING` 또는 `AUTH_UNAUTHORIZED`
- 인증 회원 조회 실패:
  - `404`
  - `MEMBER_NOT_FOUND` 또는 `MEMBER_AGREEMENT_MEMBER_NOT_FOUND`

### `POST /api/v1/member-agreements/consents`

- 인증 없음:
  - `401`
  - `AUTH_TOKEN_MISSING` 또는 `AUTH_UNAUTHORIZED`
- 잘못된 `agreementType`:
  - `400`
  - `MEMBER_AGREEMENT_INVALID_TYPE`
- 필수 약관 타입 누락:
  - `400`
  - `MEMBER_AGREEMENT_REQUIRED_TYPES_MISSING`
- 최신 필수 버전과 불일치:
  - `409`
  - `MEMBER_AGREEMENT_VERSION_MISMATCH`
- 저장 실패:
  - `500`
  - `MEMBER_AGREEMENT_SAVE_FAILED`

### 핵심 보호 API

- 미동의 회원 접근:
  - `403`
  - `MEMBER_AGREEMENT_REQUIRED`
- 닉네임 미완료 회원 접근:
  - `403`
  - `MEMBER_NICKNAME_REQUIRED`

## 프론트 해석 기준

- `MEMBER_AGREEMENT_REQUIRED`
  - 약관 동의 화면으로 이동
  - 기존 Access Token 대신 동의 성공 응답의 새 Access Token으로 교체
- `MEMBER_NICKNAME_REQUIRED`
  - 닉네임 설정 화면으로 이동
  - 인증된 상태에서 `PATCH /api/v1/members/me` 호출
- `MEMBER_AGREEMENT_VERSION_MISMATCH`
  - 최신 약관 화면 재조회 또는 재시도 안내
- `MEMBER_AGREEMENT_REQUIRED_TYPES_MISSING`
  - 필수 체크 누락 안내
- `MEMBER_AGREEMENT_INVALID_TYPE`
  - 클라이언트 요청 버그 가능성으로 간주

## 검증 시나리오

- 미동의 회원이 핵심 API를 호출하면 `MEMBER_AGREEMENT_REQUIRED`를 반환한다.
- 닉네임 미완료 회원이 핵심 API를 호출하면 `MEMBER_NICKNAME_REQUIRED`를 반환한다.
- 닉네임 미완료 회원도 `PATCH /api/v1/members/me`로 닉네임을 확정할 수 있다.
- 동의 제출에서 한 종류만 보내면 `MEMBER_AGREEMENT_REQUIRED_TYPES_MISSING`을 반환한다.
- 존재하지 않는 약관 타입을 보내면 `MEMBER_AGREEMENT_INVALID_TYPE`을 반환한다.
- 이전 버전 또는 잘못된 버전을 보내면 `MEMBER_AGREEMENT_VERSION_MISMATCH`를 반환한다.

## 현재 판단 메모

- `MEMBER_AGREEMENT_MEMBER_NOT_FOUND`, `MEMBER_AGREEMENT_SAVE_FAILED`는 현재 구현보다 넓은 후보 코드로 남아 있습니다.
- 실제 운영 기준은 구현과 테스트에서 사용 중인 코드 값을 우선합니다.
