# 인증 이메일 검증과 계정 복구 API

이 문서는 이메일 인증, 로그인 ID 찾기, 비밀번호 재설정 API의 목표 계약을 정리합니다.
현재 구현된 `POST /api/v1/auth/email`은 메일 발송 초안이며, 기존 경로를 이 문서의 계약으로 직접 리팩토링합니다.

## 범위

- 이메일 인증 코드 발송
- 이메일 인증 코드 확인
- 로그인 ID 찾기
- 비밀번호 재설정

## 비범위

- 소셜 계정 복구
- 계정 병합
- 이메일 변경
- 관리자 계정 복구

## 공통 원칙

- 모든 API는 공통 envelope를 사용합니다.
- 인증 코드 원문은 응답에 포함하지 않습니다.
- MVP 프로토타입에서는 회원가입 UX를 우선해 `SIGNUP` 목적에서 이미 가입된 자체 로그인 이메일이면 중복 이메일 오류를 명시적으로 반환합니다.
- `FIND_LOGIN_ID`, `RESET_PASSWORD` 목적에서는 계정 존재 여부를 발송 요청 응답으로 노출하지 않습니다.
- verification token은 계정 복구 전용 DB 저장형 랜덤 토큰이며 access token이나 JWT가 아닙니다.
- verification token 원문은 인증 코드 확인 성공 응답에서 한 번만 내려가고, 서버에는 해시와 만료/사용 상태만 저장합니다.
- 비밀번호 재설정 성공 후 자동 로그인하지 않습니다.
- 비밀번호 재설정 성공 후 해당 회원의 refresh token 전체를 폐기하고, 현재 응답에서는 refresh token cookie도 만료시킵니다.

## 인증 목적

| 값 | 설명 |
| --- | --- |
| `SIGNUP` | 자체 회원가입 이메일 인증 |
| `FIND_LOGIN_ID` | 로그인 ID 찾기 |
| `RESET_PASSWORD` | 비밀번호 재설정 |

## 엔드포인트

### 1. 이메일 인증 코드 발송

- Method: `POST`
- URL: `/api/v1/auth/email`
- 권한: 비회원

요청 body 예시:

```json
{
  "email": "tester@example.com",
  "purpose": "RESET_PASSWORD",
  "loginId": "tester01"
}
```

요청값:

| 필드 | 필수 | 설명 |
| --- | --- | --- |
| `email` | Y | 인증 코드를 받을 이메일 |
| `purpose` | Y | 인증 목적 |
| `loginId` | 조건부 | `RESET_PASSWORD`에서는 필요 |

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "accepted": true,
    "resendAvailableAfterSeconds": 60
  },
  "error": null
}
```

동작 기준:

1. 서버는 요청 형식을 검증합니다.
2. 목적별로 발송 가능 여부를 판단합니다.
3. `SIGNUP` 목적에서 이미 가입된 자체 로그인 이메일이면 `MEMBER_DUPLICATE_EMAIL` 오류를 반환합니다.
4. `FIND_LOGIN_ID`, `RESET_PASSWORD` 목적에서는 계정 존재 여부와 무관하게 같은 성공 응답을 반환합니다.
5. 실제 발송 대상이면 인증 코드를 생성하고 메일을 보냅니다.
6. 기존 미완료 인증 코드는 만료 또는 폐기합니다.

중복 이메일 응답 예시:

```json
{
  "success": false,
  "data": null,
  "error": {
    "status": 409,
    "code": "MEMBER_DUPLICATE_EMAIL",
    "message": "이미 사용 중인 이메일입니다. email : tester@example.com",
    "details": []
  }
}
```

주의:

- `SIGNUP`에서 이미 가입된 자체 로그인 이메일이면 응답으로 중복 여부가 노출됩니다. 이는 MVP 프로토타입의 사용자 흐름 단순화를 위한 의도적 정책입니다.
- `FIND_LOGIN_ID`에서 이메일과 매칭되는 계정이 없어도 응답은 성공입니다.
- `RESET_PASSWORD`에서 `loginId + email`이 일치하지 않아도 응답은 성공입니다.
- 발송 시스템 자체 장애는 `AUTH_EMAIL_SEND_FAILED`로 실패할 수 있습니다.

### 2. 이메일 인증 코드 확인

- Method: `POST`
- URL: `/api/v1/auth/email/confirm`
- 권한: 비회원

요청 body 예시:

```json
{
  "email": "tester@example.com",
  "purpose": "RESET_PASSWORD",
  "loginId": "tester01",
  "code": "123456"
}
```

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "verified": true,
    "emailVerificationToken": "ev_eyJhbGciOiJIUzI1NiJ9...",
    "expiresIn": 600
  },
  "error": null
}
```

동작 기준:

1. 서버는 `email + purpose + loginId`에 해당하는 최신 미완료 인증 레코드를 찾습니다.
2. 만료 여부와 시도 횟수를 확인합니다.
3. 코드 해시를 비교합니다.
4. 성공하면 인증 레코드를 검증 완료로 바꾸고 DB 저장형 랜덤 verification token을 발급합니다.

실패 기준:

- 인증 레코드가 없거나 만료됨
- 인증 코드가 올바르지 않음
- 검증 시도 횟수 초과
- 이미 사용된 인증 코드

대표 실패 응답:

```json
{
  "success": false,
  "data": null,
  "error": {
    "status": 401,
    "code": "AUTH_EMAIL_VERIFICATION_FAILED",
    "message": "이메일 인증에 실패했습니다.",
    "details": []
  }
}
```

### 3. 로그인 ID 찾기

- Method: `POST`
- URL: `/api/v1/auth/recovery/login-id`
- 권한: 비회원

요청 body 예시:

```json
{
  "emailVerificationToken": "ev_eyJhbGciOiJIUzI1NiJ9..."
}
```

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "loginId": "tester01"
  },
  "error": null
}
```

동작 기준:

1. 서버는 verification token 해시가 `FIND_LOGIN_ID` 목적이고 만료/사용되지 않았는지 확인합니다.
2. token의 이메일에 연결된 활성 자체 로그인 계정을 조회합니다.
3. verification token을 사용 완료 처리합니다.
4. 로그인 ID 1개를 반환합니다.

확정 기준:

- 한 이메일에 여러 자체 로그인 ID를 허용하지 않습니다.
- 이메일 인증을 이미 통과한 사용자에게는 자체 로그인 ID 원문을 반환합니다.

### 4. 비밀번호 재설정

- Method: `POST`
- URL: `/api/v1/auth/recovery/password`
- 권한: 비회원

요청 body 예시:

```json
{
  "loginId": "tester01",
  "emailVerificationToken": "ev_eyJhbGciOiJIUzI1NiJ9...",
  "newPassword": "N3wP@ssw0rd!"
}
```

성공 응답 예시:

```json
{
  "success": true,
  "data": {
    "reset": true
  },
  "error": null
}
```

동작 기준:

1. 서버는 verification token 해시가 `RESET_PASSWORD` 목적이고 만료/사용되지 않았는지 확인합니다.
2. token의 `loginId`, `email`이 요청 계정과 일치하는지 확인합니다.
3. 새 비밀번호를 기존 비밀번호 정책으로 검증합니다.
4. 새 비밀번호를 BCrypt로 해시해 저장합니다.
5. verification token을 사용 완료 처리합니다.
6. 해당 회원의 기존 refresh token 전체를 폐기합니다.
7. 현재 응답의 refresh token cookie를 만료시킵니다.
8. 자동 로그인이나 토큰 발급 없이 성공 응답을 반환합니다.

## 구현 반영 상태

2026-04-26 첫 번째 API 단위 구현에서 기존 `POST /api/v1/auth/email`은 목표 계약에 맞춰 직접 수정했습니다.
이후 두 번째 API 단위 구현에서 `POST /api/v1/auth/email/confirm`을 추가했습니다.

반영된 사항:

- 요청 body는 `email`, `purpose`, `loginId` 기준입니다.
- 응답 body는 `accepted`, `resendAvailableAfterSeconds` 기준입니다.
- 인증 코드 원문과 인증 레코드 ID는 응답에 포함하지 않습니다.
- `SIGNUP` 목적에서 이미 가입된 자체 로그인 이메일이면 `MEMBER_DUPLICATE_EMAIL`을 반환합니다.
- `RESET_PASSWORD` 목적에서 `loginId`가 없으면 요청 검증 실패로 처리합니다.
- domain service는 API request/response DTO가 아니라 command/result를 사용합니다.
- 인증 확인 성공 시 DB 저장형 랜덤 `emailVerificationToken` 원문을 한 번만 응답하고, DB에는 token hash와 만료 시각을 저장합니다.
- 회원가입 통합 API는 `SIGNUP` 목적 token을 검증하고 사용 완료 처리합니다.
- 로그인 ID 찾기 API는 `FIND_LOGIN_ID` 목적 token을 검증하고 사용 완료 처리한 뒤 단일 `loginId`를 반환합니다.
- 비밀번호 재설정 API는 `RESET_PASSWORD` 목적 token을 검증하고 사용 완료 처리한 뒤 비밀번호를 교체하며 해당 회원의 기존 refresh token 전체를 폐기합니다.

리팩토링 전 초안 API는 아래 이유로 목표 계약과 달랐습니다.

- 경로가 이메일 인증 목적을 충분히 설명하지 않습니다.
- request body에 Bean Validation이 없습니다.
- `type` 문자열을 enum으로 직접 변환해 잘못된 값 처리 기준이 약합니다.
- 응답에 인증 레코드 ID가 포함됩니다.
- 인증 코드 확인과 후속 계정 복구 흐름이 없습니다.

별도 호환 경로는 두지 않습니다.

## 검증 시나리오

- 유효한 `SIGNUP` 발송 요청이면 인증 메일 발송이 시도된다.
- 이미 가입된 자체 로그인 이메일로 `SIGNUP` 발송을 요청하면 `MEMBER_DUPLICATE_EMAIL`이 발생한다.
- `RESET_PASSWORD`에서 `loginId`가 없으면 요청 검증 실패가 발생한다.
- 존재하지 않는 이메일로 로그인 ID 찾기 발송을 요청해도 응답은 성공이다.
- 만료된 코드는 확인할 수 없다.
- 틀린 코드를 5회 초과 입력하면 더 이상 확인할 수 없다.
- 인증 성공 후 같은 코드를 재사용할 수 없다.
- 인증 성공 후 발급된 `emailVerificationToken`은 한 번만 사용할 수 있다.
- `FIND_LOGIN_ID` token으로 비밀번호 재설정을 할 수 없다.
- `RESET_PASSWORD` token으로 로그인 ID 찾기를 할 수 없다.
- 비밀번호 재설정 후 기존 refresh token으로 access token을 재발급할 수 없다.
