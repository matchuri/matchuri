# 회원 필수 약관 동의 API

이 문서는 Matchuri의 회원 필수 약관 동의 기능에 대한 현재 API 기준입니다.
목적은 프론트와 백엔드가 "언제 약관 동의가 필요한지", "어떤 요청과 응답으로 상태를 주고받는지"를 같은 기준으로 이해하도록 만드는 것입니다.

## 범위

- 필수 약관 동의 완료 여부 조회
- 필수 약관 동의 제출
- 로그인 이후 필수 온보딩 상태 해석 기준

## 비범위

- 약관 전문 콘텐츠 제공 방식
- 관리자 약관 버전 관리 화면
- 선택 약관 또는 마케팅 수신 동의
- 약관 철회 처리

## 현재 확정 결정

- 현재는 필수 약관 동의만 고려합니다.
- 필수 약관은 `서비스 이용약관`, `개인정보 처리방침` 두 종류입니다.
- 최신 필수 버전은 서버 상수로 관리합니다.
- 약관 동의 이력은 별도 `member_agreements` 테이블에 저장합니다.
- 미동의 회원도 로그인은 가능하지만, 핵심 API는 차단합니다.
- 프론트는 로그인, refresh, OAuth2 교환 응답의 `data.onboarding.nextStep`을 기준으로 약관 또는 닉네임 온보딩 화면으로 이동합니다.
- 핵심 API 인가는 기본적으로 Access Token claim의 필수 약관 revision으로 판단합니다.
- 다만 기존 회원이 구 토큰을 계속 보유한 경우를 위해, claim이 현재 서버 revision과 다를 때만 DB로 최신 필수 약관 완료 여부를 fallback 확인할 수 있습니다.
- 필수 약관 완료 여부 계산은 과거 이력 전체를 덮어쓰지 않고, "현재 서버가 요구하는 최신 버전이 존재하는가" 기준으로 판단합니다.
- 자체 로그인과 소셜 로그인 신규 가입 모두 같은 약관 동의 기준을 사용합니다.
- 다만 새 자체 회원가입 기본 경로 `POST /api/v1/members/signup`은 필수 약관 동의를 회원가입 요청 안에서 함께 처리합니다.
- 닉네임 온보딩은 `members.nickname_completed` 기준으로 판단하며, 신규 소셜 회원은 임시 닉네임으로 생성되므로 닉네임 완료 전까지 핵심 API가 차단됩니다.

## API가 다루는 핵심 질문

- 현재 로그인한 회원은 필수 약관 2종의 최신 필수 버전에 모두 동의했는가
- 아직 동의하지 않은 약관 종류는 무엇인가
- 프론트가 현재 화면을 계속 진행해도 되는가

## 엔드포인트

### 1. 필수 약관 상태 조회

- Method: `GET`
- URL: `/api/v1/member-agreements/required-status`
- 권한: 로그인 회원
- 설명: 현재 로그인한 회원이 필수 약관 동의를 완료했는지 조회합니다.

동작:

1. Access Token 기준으로 현재 회원을 식별합니다.
2. 서버는 `TERMS_OF_SERVICE`, `PRIVACY_POLICY`의 최신 필수 버전 동의 여부를 확인합니다.
   이때 과거 버전 이력이 함께 있어도 최신 필수 버전 존재 여부만으로 판단합니다.
3. 완료 여부와 누락된 약관 종류를 반환합니다.

응답 payload 예시:

```json
{
  "requiredAgreementsCompleted": false,
  "missingAgreementTypes": [
    "TERMS_OF_SERVICE",
    "PRIVACY_POLICY"
  ]
}
```

완료 상태 예시:

```json
{
  "requiredAgreementsCompleted": true,
  "missingAgreementTypes": []
}
```

### 2. 필수 약관 동의 제출

- Method: `POST`
- URL: `/api/v1/member-agreements/consents`
- 권한: 로그인 회원
- 설명: 현재 로그인한 회원의 필수 약관 동의를 저장합니다.

요청 body 예시:

```json
{
  "agreements": [
    {
      "agreementType": "TERMS_OF_SERVICE",
      "agreementVersion": "2026-04-10"
    },
    {
      "agreementType": "PRIVACY_POLICY",
      "agreementVersion": "2026-04-10"
    }
  ]
}
```

동작:

1. 서버는 요청 회원을 확인합니다.
2. 서버는 요청에 필수 약관 2종이 모두 포함됐는지 확인합니다.
3. 서버는 각 약관 버전이 현재 서버 상수의 최신 필수 버전과 일치하는지 검증합니다.
4. 유효하면 `member_agreements`에 동의 기록을 저장합니다.
5. 저장 후 필수 약관 완료 여부를 다시 계산합니다.
6. 완료 시점의 최신 필수 약관 revision을 담은 새 Access Token을 재발급해 반환합니다.
7. 약관 동의 후 닉네임 온보딩이 남아 있으면 `data.onboarding.nextStep=REQUIRED_NICKNAME`을 반환합니다.

정확성 기준:

- 사용자가 과거 버전과 최신 버전 이력을 동시에 가지고 있어도, 상태 계산은 최신 필수 버전 레코드의 존재 여부만 봅니다.
- 따라서 향후 약관 개정 후 재동의가 발생해도, 오래된 레코드가 최신 동의 상태를 덮어써서는 안 됩니다.

성공 응답 `data` payload 예시:

```json
{
  "requiredAgreementsCompleted": true,
  "missingAgreementTypes": [],
  "onboarding": {
    "requiredAgreementsCompleted": true,
    "nicknameCompleted": false,
    "completed": false,
    "nextStep": "REQUIRED_NICKNAME"
  },
  "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
  "expiresIn": 3600
}
```

주의:

- `POST /api/v1/member-agreements/consents` 성공 응답의 `accessToken`으로 즉시 교체하는 것을 권장합니다.
- 서버는 기존 회원이 구 토큰을 들고 있는 경우를 위해 claim mismatch 시 DB fallback 검증을 수행할 수 있지만, 프론트는 최신 claim이 담긴 토큰으로 빠르게 교체하는 편이 가장 단순하고 예측 가능합니다.

## 로그인 이후 프론트 처리 기준

로그인 성공 직후 프론트는 인증 응답의 `data.onboarding.nextStep`을 기준으로 필수 온보딩 단계를 해석합니다.

### 로그인 응답 또는 후속 교환 응답에 포함

- 로그인, refresh, OAuth2 교환 응답 payload에 `onboarding`을 포함합니다.
- 프론트는 응답을 보고 즉시 약관 동의 또는 닉네임 설정 화면 이동 여부를 판단합니다.

장점:

- 추가 API 호출 수를 줄일 수 있습니다.

주의:

- 로그인 응답 계약이 커질 수 있습니다.
- 소셜 로그인 후속 교환 API와 자체 로그인 API 모두 같은 형식을 맞춰야 합니다.

`GET /api/v1/member-agreements/required-status`는 약관 화면 자체에서 현재 누락 타입을 다시 확인하는 보조 API로 유지합니다.

## 요청값 규칙

### `agreementType`

- 필수
- 허용 값:
  - `TERMS_OF_SERVICE`
  - `PRIVACY_POLICY`

### `agreementVersion`

- 필수
- 서버 상수의 최신 필수 버전과 일치해야 합니다.
- 현재 포맷은 문자열로 처리합니다.

가정(Assumption):

- 초기 버전 표기는 날짜형 문자열이나 배포 기준 문자열을 사용합니다.
- 예: `2026-04-10`, `v2026-04-10`

## 응답 규칙

공통 응답 envelope는 기존 Matchuri 규칙을 따릅니다.

- `success`
- `data`
- `error`

이 문서에서는 `data` payload 기준으로 아래 값을 사용합니다.

- `requiredAgreementsCompleted`
- `missingAgreementTypes`
- `onboarding`
  - `requiredAgreementsCompleted`
  - `nicknameCompleted`
  - `completed`
  - `nextStep`
- `accessToken` (`POST /api/v1/member-agreements/consents` 성공 시)
- `expiresIn` (`POST /api/v1/member-agreements/consents` 성공 시)

필요 시 후속 확장 가능 항목:

- `requiredAgreementVersions`
- 약관 전문 URL 또는 약관 표시용 메타데이터

`onboarding.nextStep`은 서버의 `OnboardingNextStep` enum을 문자열로 직렬화한 값입니다.
현재 값은 `REQUIRED_AGREEMENTS`, `REQUIRED_NICKNAME`, `READY`입니다.

## 검증 실패 및 오류 시나리오

### 인증 없음

- 로그인하지 않은 사용자가 상태 조회 또는 동의 제출을 호출한 경우
- 응답: `401`

### 필수 약관 누락

- 동의 제출 요청에 `TERMS_OF_SERVICE` 또는 `PRIVACY_POLICY`가 빠진 경우
- 응답: `400`

### 잘못된 약관 종류

- 지원하지 않는 `agreementType`이 들어온 경우
- 응답: `400`

### 버전 불일치

- 요청한 `agreementVersion`이 현재 서버 상수의 최신 필수 버전과 다를 경우
- 응답: `409` 또는 `400`

권장 판단:

- 현재 필수 버전과 충돌하는 상태로 보는 관점에서는 `409`가 더 자연스럽습니다.

### 중복 제출

- 동일 회원이 같은 `agreementType + agreementVersion`으로 다시 제출한 경우
- 응답:
  - 멱등 처리 후 성공 응답 권장

이유:

- 브라우저 재시도나 프론트 중복 호출을 운영 이슈로 키우지 않기 위해서입니다.

## 보호 API와의 관계

- 필수 약관 상태 조회 API는 로그인만 되어 있으면 호출할 수 있어야 합니다.
- 필수 약관 동의 제출 API도 로그인만 되어 있으면 호출할 수 있어야 합니다.
- 그 외 핵심 서비스 API는 현재 서버가 요구하는 필수 약관 revision claim과 `members.nickname_completed=true` 상태를 전제로 인가합니다.
- 차단 우선순위는 필수 약관 미완료, 닉네임 미완료 순서입니다.

예시:

- 허용:
  - 로그인
  - 로그아웃
  - 필수 약관 상태 조회
  - 필수 약관 동의 제출
  - 닉네임 중복 확인
  - 닉네임 설정용 `PATCH /api/v1/members/me`

- 차단 대상:
  - `members/me` 조회
  - 취향 프로필 수정
  - 개인 추천
  - 그룹 생성/참여/탈퇴
  - 그룹 추천과 투표

## 자체 로그인과 소셜 로그인의 연결 기준

### 자체 로그인 레거시/보정 흐름

- 계정 생성
- 로그인
- 필수 약관 상태 조회
- 약관 동의 화면 이동
- 필수 약관 동의 제출
- 필요 시 닉네임 설정
- 핵심 서비스 진입

### 자체 회원가입 통합 흐름

- `POST /api/v1/members/signup`
- 회원 생성, 필수 약관 동의 저장, 닉네임 확정
- 로그인
- 핵심 서비스 진입

### 소셜 로그인

- OAuth2 로그인 성공
- 신규 회원이면 즉시 계정 생성
- 필수 약관 상태 조회
- 약관 동의 화면 이동
- 필수 약관 동의 제출
- 닉네임 설정
- 핵심 서비스 진입

즉, 로그인 수단은 다르지만 약관 동의 완료 여부 판단 기준은 같아야 합니다.
다만 자체 회원가입은 새 기본 경로에서 약관 동의를 회원가입 요청에 포함하고, 소셜 로그인과 레거시 자체 로그인은 별도 약관 API를 계속 사용합니다.

## 검증 시나리오

- 로그인한 회원이 필수 약관 2종 모두 미동의 상태면 상태 조회 API가 `requiredAgreementsCompleted=false`를 반환한다.
- 한 종류만 동의한 상태면 나머지 타입이 `missingAgreementTypes`에 포함된다.
- 두 종류 모두 최신 필수 버전에 동의하면 `requiredAgreementsCompleted=true`를 반환한다.
- 과거 버전과 최신 버전 이력이 함께 있어도 최신 필수 버전 레코드가 있으면 `requiredAgreementsCompleted=true`를 유지한다.
- 동의 제출 요청에 필수 약관 2종이 모두 포함되면 저장 후 완료 상태가 된다.
- 동의 제출 성공 응답은 새 Access Token을 반환한다.
- 동의 제출 요청 버전이 서버 상수와 다르면 실패한다.
- 동일 버전 중복 제출은 멱등하게 처리할 수 있다.
- 미동의 회원은 로그인 후에도 핵심 서비스 API에서 차단된다.
- 약관 동의 완료 후에도 기존 Access Token은 차단되고, 동의 응답의 새 Access Token으로만 핵심 서비스 API에 접근할 수 있다.
- 약관 동의 완료 후 닉네임 미완료 상태면 `data.onboarding.nextStep=REQUIRED_NICKNAME`이 반환된다.
- 닉네임 미완료 회원은 핵심 API에서 `MEMBER_NICKNAME_REQUIRED`로 차단된다.
- 닉네임 미완료 회원도 인증된 상태라면 `PATCH /api/v1/members/me`로 닉네임을 확정할 수 있다.

## 현재 판단 메모

- 로그인/refresh/OAuth2 교환 응답에 온보딩 상태를 직접 포함하는 것을 현재 기본 기준으로 둡니다.
- 약관 정책 마스터 테이블 도입과 선택 약관 확장은 후속 범위로 남깁니다.
