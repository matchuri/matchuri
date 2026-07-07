# 인증 세션 API

이 문서는 Matchuri의 현재 인증 세션 API 계약을 정리합니다.
목적은 로컬 로그인, refresh token 기반 세션 복구, 로그아웃의 현재 동작을 프론트와 백엔드가 같은 기준으로 이해하도록 만드는 것입니다.

## 범위

- 로컬 로그인
- refresh token 쿠키 기반 access token 재발급
- 로그아웃
- 현재 단계의 세션 종료 의미

## 비범위

- 소셜 OAuth2 리다이렉트 및 교환 상세
- 소셜 회원 생성 규칙
- 필수 약관 동의 화면 UX
- 다중 디바이스 세션 관리 UI

관련 OAuth2 흐름은 `docs/api/auth-google-oauth2.md`를 따릅니다.

## 현재 확정 결정

- `POST /api/v1/auth/login`은 `accessToken`을 응답 body에 반환합니다.
- `refreshToken`은 응답 body가 아니라 `HttpOnly` 쿠키로 내려갑니다.
- `POST /api/v1/auth/refresh`는 요청 body 없이 refresh token 쿠키만으로 새 access token을 발급합니다.
- refresh 성공 시 refresh token도 새 값으로 회전하여 쿠키를 다시 설정합니다.
- `POST /api/v1/auth/logout`은 현재 세션의 refresh token만 폐기합니다.
- 로그아웃 후에도 이미 발급된 access token은 만료 전까지 즉시 무효화되지 않습니다.
- 필수 약관 또는 닉네임 온보딩 미완료 회원은 로그인 자체는 가능하지만 핵심 보호 API 접근은 차단될 수 있습니다.
- 로그인과 refresh 응답은 앱 재진입 시에도 프론트가 다음 필수 온보딩 단계를 판단할 수 있도록 `onboarding` 상태를 포함합니다.

## 공통 응답 형식

인증 세션 API는 공통 envelope 구조를 사용합니다.

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": null,
    "expiresIn": 3600,
    "member": {
      "id": 1,
      "role": "MEMBER",
      "nickname": "점심탐험가"
    },
    "onboarding": {
      "requiredAgreementsCompleted": true,
      "nicknameCompleted": true,
      "completed": true,
      "nextStep": "READY"
    }
  },
  "error": null
}
```

주의:

- 현재 `refreshToken` 필드는 body에서 항상 `null`입니다.
- 실제 refresh token 값은 `Set-Cookie` 헤더의 `matchuri_refresh_token` 쿠키로 전달됩니다.

## 엔드포인트

### 1. 로컬 로그인

- Method: `POST`
- URL: `/api/v1/auth/login`
- 권한: 비회원

요청 body 예시:

```json
{
  "loginId": "tester01",
  "password": "P@ssw0rd!"
}
```

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiJ9...",
    "refreshToken": null,
    "expiresIn": 3600,
    "member": {
      "id": 1,
      "role": "MEMBER",
      "nickname": "점심탐험가"
    },
    "onboarding": {
      "requiredAgreementsCompleted": true,
      "nicknameCompleted": true,
      "completed": true,
      "nextStep": "READY"
    }
  },
  "error": null
}
```

동작 기준:

1. 서버는 `loginId`로 회원을 조회합니다.
2. 비밀번호 해시를 검증합니다.
3. 활성 회원이면 access token과 refresh token을 발급합니다.
4. access token은 body에, refresh token은 `HttpOnly` 쿠키에 내려갑니다.

실패 기준:

- 아이디 또는 비밀번호가 올바르지 않으면 `AUTH_LOGIN_FAILED`
- 비활성 회원이면 `MEMBER_INACTIVE_MEMBER`

### 2. refresh token으로 access token 재발급

- Method: `POST`
- URL: `/api/v1/auth/refresh`
- 권한: 비회원
- 요청 body: 없음

동작 기준:

1. 서버는 `matchuri_refresh_token` 쿠키를 읽습니다.
2. 유효한 현재 세션이면 새 access token을 발급합니다.
3. refresh token도 새 값으로 회전하여 쿠키를 다시 설정합니다.
4. 유효하지 않거나 만료된 refresh token이면 쿠키를 비우고 실패를 반환합니다.

성공 응답 payload는 로컬 로그인과 같습니다.

실패 기준:

- refresh token 쿠키가 없으면 `AUTH_REFRESH_TOKEN_MISSING`
- 유효하지 않은 refresh token이면 `AUTH_REFRESH_TOKEN_INVALID`
- 만료된 refresh token이면 `AUTH_REFRESH_TOKEN_EXPIRED`
- 비활성 회원이면 `MEMBER_INACTIVE_MEMBER`

주의:

- 필수 약관 미완료 회원도 refresh 자체는 가능할 수 있습니다.
- 다만 이후 보호 API 호출 시 `MEMBER_AGREEMENT_REQUIRED`가 반환될 수 있습니다.

### 3. 로그아웃

- Method: `POST`
- URL: `/api/v1/auth/logout`
- 권한: 회원

요청 기준:

- `Authorization: Bearer <accessToken>` 헤더가 필요합니다.
- 현재 세션의 `matchuri_refresh_token` 쿠키도 함께 필요합니다.

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "loggedOut": true
  },
  "error": null
}
```

동작 기준:

1. 서버는 현재 인증된 회원을 확인합니다.
2. 요청 쿠키의 refresh token을 서버 저장소에서 폐기합니다.
3. 응답에서 refresh token 쿠키를 삭제합니다.

현재 단계의 의미:

- 로그아웃은 refresh token 재발급을 막는 동작입니다.
- 이미 발급된 access token은 즉시 무효화되지 않습니다.
- 따라서 access token은 만료 전까지 보호 API 호출에 계속 사용될 수 있습니다.

실패 기준:

- access token이 없거나 유효하지 않으면 `AUTH_TOKEN_MISSING` 또는 `AUTH_TOKEN_INVALID`
- refresh token 쿠키가 없으면 `AUTH_LOGOUT_FAILED`

## 쿠키 정책 메모

- refresh token 쿠키 이름은 현재 `matchuri_refresh_token`입니다.
- 쿠키는 `HttpOnly` 기준으로 내려갑니다.
- `Secure` 속성은 환경 설정 `MATCHURI_COOKIE_SECURE`에 따라 달라집니다.
  - 운영 HTTPS 환경에서는 `true`로 사용하는 것을 전제합니다.
  - 저장소 기본 설정만 기준으로 하면 항상 `Secure`로 고정된 것은 아닙니다.

## 검증 시나리오 초안

- 유효한 로컬 계정이면 access token body와 refresh token 쿠키가 함께 내려간다.
- 로그인과 refresh 성공 응답에는 `data.onboarding.nextStep`이 포함된다.
- refresh 호출 성공 시 기존 refresh token은 회전되고 이전 토큰은 더 이상 유효하지 않다.
- refresh token이 없거나 잘못되면 재발급이 실패하고 쿠키가 비워진다.
- 로그아웃 성공 시 refresh token 저장소 기록과 쿠키가 함께 삭제된다.
- 로그아웃 후에도 기존 access token은 만료 전까지 사용할 수 있다.
