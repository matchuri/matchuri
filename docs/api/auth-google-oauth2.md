# 인증 API 초안: Google/Kakao/Naver OAuth2 로그인

이 문서는 회원/인증 2단계에서 구현한 Google/Kakao/Naver OAuth2 로그인 계약 초안입니다.
현재 목적은 프론트와 백엔드가 리다이렉트 흐름, 성공 처리, 실패 처리, 토큰 전달 방식을 같은 기준으로 이해하도록 만드는 것입니다.

## 범위

- Google/Kakao/Naver OAuth2 로그인 시작
- Google/Kakao/Naver OAuth2 콜백 처리
- Matchuri JWT 발급
- 신규 소셜 회원 즉시 생성
- 필수 약관 동의 필요 상태 진입
- 임시 닉네임 부여 후 후속 닉네임 설정 필요 상태 진입
- 실패 시 프론트 복귀 규칙

## 비범위

- Google/Kakao/Naver 외 다른 OAuth2 제공자
- 소셜 계정과 자체 계정의 연결 또는 병합
- OAuth2 이후 추가 온보딩 화면 상세 UX
- 세션 관리 UI

## 현재 확정 결정

- 현재 지원 provider는 `Google`, `Kakao`, `Naver`입니다.
- 소셜 로그인 성공 후 프론트는 provider 토큰이 아니라 Matchuri JWT만 사용합니다.
- 신규 소셜 사용자는 즉시 회원 생성합니다.
- 신규 소셜 사용자는 서버 규칙 기반 임시 닉네임을 먼저 부여받습니다.
- 신규 소셜 사용자는 회원 생성 후 필수 약관 동의가 완료되어야 핵심 서비스 기능을 사용할 수 있습니다.
- 신규 소셜 사용자는 회원 생성 후 닉네임 온보딩이 완료되어야 핵심 서비스 기능을 사용할 수 있습니다.
- 소셜 계정 정보는 별도 연결 테이블이 아니라 `members` 모델에 저장합니다.
- 필수 약관 동의 이력은 별도 `member_agreements` 테이블에 저장합니다.
- Refresh Token은 로그인 단위 다중 저장 정책을 사용합니다.
- OAuth2 성공 후 프론트 복귀는 `단기 교환 코드 전달` 방식을 사용합니다.
- 브라우저 세션 복구를 위해 `POST /api/v1/auth/refresh`를 제공합니다.
- 자체 로그인 계정과 소셜 로그인 계정은 자동 병합하지 않습니다.
- 필수 약관 종류는 `서비스 이용약관`, `개인정보 처리방침` 두 가지입니다.
- 최신 필수 버전은 서버 상수로 관리합니다.

## 현재 운영 기준값

- 프론트 canonical 도메인: `https://www.matchuri.com`
- apex redirect: `https://matchuri.com -> https://www.matchuri.com`
- 백엔드 API 도메인: `https://api.matchuri.com`
- 백엔드 callback endpoint: `https://api.matchuri.com/login/oauth2/code/{provider}`
- 프론트 성공 복귀 URL: `https://www.matchuri.com/auth/callback/{provider}`
- 프론트 실패 복귀 URL: `https://www.matchuri.com/login`

가정(Assumption):

- 현재 코드는 `MATCHURI_FRONTEND_ORIGIN` 값을 CORS 허용 origin과 OAuth2 프론트 복귀 URL base에 함께 사용합니다.
- 현재 Spring Security 설정은 provider별 callback 경로 `/login/oauth2/code/{provider}`를 사용합니다.

## 엔드포인트 초안

### 1. 소셜 로그인 시작

- Method: `GET`
- URL: `/api/v1/auth/oauth2/{provider}`
- 권한: 비회원
- 설명: 요청한 provider의 OAuth2 로그인 화면으로 리다이렉트합니다.

현재 지원 provider:

- `google`
- `kakao`
- `naver`

동작:

1. 프론트가 이 엔드포인트로 이동합니다.
2. 백엔드는 provider 인증 페이지로 리다이렉트합니다.
3. 백엔드는 로그인 성공 후 지정된 콜백 엔드포인트에서 후속 처리를 이어갑니다.

응답:

- 일반 JSON 응답 대신 `302 Redirect`

### 2. 소셜 로그인 콜백

- Method: `GET`
- URL: `/login/oauth2/code/{provider}`
- 권한: 비회원
- 설명: Spring Security OAuth2 Client가 provider 인증 결과를 수신하는 콜백 엔드포인트입니다.

Provider console 등록 기준:

- Local Backend Redirect URI: `http://localhost:8080/login/oauth2/code/google`
- Local Backend Redirect URI: `http://localhost:8080/login/oauth2/code/kakao`
- Local Backend Redirect URI: `http://localhost:8080/login/oauth2/code/naver`
- 운영 Backend Redirect URI: `https://api.matchuri.com/login/oauth2/code/google`
- 운영 Backend Redirect URI: `https://api.matchuri.com/login/oauth2/code/kakao`
- 운영 Backend Redirect URI: `https://api.matchuri.com/login/oauth2/code/naver`
- 운영 환경에서는 백엔드 공개 도메인 기준으로 동일 경로를 별도 등록합니다.
- Google OAuth Client의 `Authorized redirect URIs` 값은 Spring Security가 실제로 사용하는 콜백 URL과 완전히 일치해야 합니다.
- 프로토콜(`http`/`https`), 호스트, 포트, 경로 중 하나라도 다르면 `400 redirect_uri_mismatch`가 발생합니다.

동작:

1. provider가 authorization code를 포함해 콜백합니다.
2. 백엔드는 provider 사용자 정보를 조회합니다.
3. 기존 회원 조회 또는 신규 회원 생성을 수행합니다.
4. 백엔드는 Refresh Token을 발급하고 서버 저장소 및 쿠키 처리 기준을 반영합니다.
5. 백엔드는 Access Token 직접 전달 대신 짧게 유효한 단기 교환 코드를 생성합니다.
6. 프론트 지정 URL로 리다이렉트합니다.

## 프론트 복귀 계약

### 성공 시

- 백엔드는 프론트 성공 URL로 리다이렉트합니다.
- 프론트는 아래 값으로 후속 로그인 상태를 처리합니다.

최종 전달 방식:

- `HttpOnly` 쿠키에 Refresh Token 저장
- 백엔드는 짧게 유효한 토큰 교환용 단기 코드를 프론트에 전달합니다.
- 프론트는 후속 교환 API를 호출해 Access Token을 받습니다.
- 프론트는 교환 응답의 `data.onboarding.nextStep`을 기준으로 필수 온보딩 화면을 결정합니다.

확정 이유:

- URL 쿼리에 JWT를 직접 노출하지 않기 위해서입니다.
- 브라우저 히스토리, 리퍼러, 로그 노출 위험을 줄이기 위해서입니다.
- 모바일과 웹을 함께 고려하는 웹앱에서 더 안전한 기본 구조이기 때문입니다.

성공 리다이렉트 예시:

```text
GET https://www.matchuri.com/auth/callback/kakao?loginResult=success&provider=kakao&code=temporary_exchange_code
```

후속 교환 API 예시:

- Method: `POST`
- URL: `/api/v1/auth/oauth2/exchange`
- 권한: 비회원
- 요청 body 예시:

```json
{
  "provider": "NAVER",
  "code": "temporary_exchange_code"
}
```

- 응답:
- Access Token 반환
- 회원 요약 정보 반환
- 온보딩 상태 반환
- Refresh Token은 `HttpOnly` 쿠키 기준으로 처리

현재 구현 기준:

- 후속 교환 API 응답 body는 `accessToken`, `refreshToken(null)`, `expiresIn`, `member`, `onboarding`을 반환합니다.
- `data.onboarding.nextStep` 값은 `REQUIRED_AGREEMENTS`, `REQUIRED_NICKNAME`, `READY` 중 하나입니다.
- 브라우저 세션 복구와 access token 재발급은 `POST /api/v1/auth/refresh`로 처리합니다.
- 필수 약관 또는 닉네임 온보딩 미완료 상태에서 받은 Access Token은 핵심 API 접근용으로는 충분하지 않습니다.
- 필수 약관 동의 완료 후에는 `POST /api/v1/member-agreements/consents` 응답의 새 Access Token으로 교체해야 합니다.
- refresh token 쿠키의 `Secure` 속성은 환경 설정에 따라 달라질 수 있으며, 운영 HTTPS 환경에서는 `true`를 전제합니다.

### 실패 시

- 백엔드는 프론트 실패 URL로 리다이렉트합니다.
- 프론트는 `provider`, `errorCode` 기준으로 실패 화면 또는 재시도 UX를 구성합니다.

실패 리다이렉트 예시:

```text
GET https://www.matchuri.com/login?loginResult=failed&provider=kakao&errorCode=AUTH_OAUTH2_PROVIDER_REJECTED
```

## 회원 생성 규칙

- provider 사용자 고유 식별자가 기존 `members` 레코드에 있으면 기존 회원으로 로그인합니다.
- 없으면 신규 `Member`를 즉시 생성합니다.
- 신규 회원 생성 시:
- `isSocial=true`
- `socialProviderType=GOOGLE`, `KAKAO` 또는 `NAVER`
- provider 사용자 식별자 저장
- 비밀번호는 비워두거나 사용 불가 상태로 저장
- 이메일은 제공되는 경우 저장 가능하지만, 계정 병합 기준으로 사용하지 않습니다.
- 닉네임은 provider profile name을 그대로 쓰지 않고 `이메일 로컬파트_provider` 규칙의 임시 닉네임을 저장합니다.
  - 예시: `example@google.com` -> `example_google`
  - 예시: `example@kakao.com` -> `example_kakao`
  - 예시: `example@naver.com` -> `example_naver`
  - 이메일이 없으면 `user_provider` 규칙을 사용합니다.
  - 가정(Assumption): 같은 규칙으로 충돌이 발생하면 서버가 숫자 suffix를 붙여 유니크하게 저장합니다.
- 필수 약관 동의는 `members`에 직접 기록하지 않고 `member_agreements`에 별도로 저장합니다.
- 신규 소셜 회원은 생성 직후에도 필수 약관 동의와 닉네임 온보딩 완료 전까지는 핵심 API를 사용할 수 없습니다.
- 필수 약관 동의 이후 닉네임 설정 화면에서 별도 닉네임 중복검사 API를 호출해 최종 닉네임을 확정합니다.

## 현재 members 필드 방향

현재 구현 기준으로 `members` 모델은 아래 필드 또는 동등한 구조를 사용합니다.

- `is_social`
- `social_provider_type`
- `social_provider_user_id`
- `email`
- `status`
- `nickname_completed`

주의:

- 자체 로그인 회원의 `loginId`와 provider 사용자 식별자를 같은 필드로 섞어 쓰지 않습니다.
- provider 이메일이 같더라도 기존 자체 로그인 계정과 자동 병합하지 않습니다.

## 필수 약관 동의 처리 방향

- 신규 소셜 회원도 자체 로그인 회원과 동일한 필수 약관 동의 기준을 적용합니다.
- 로그인 성공은 허용하지만, 필수 약관 동의와 닉네임 온보딩 완료 전에는 핵심 서비스 이용 가능 상태로 간주하지 않습니다.
- 필수 약관 동의 정보는 `member_agreements`에 저장합니다.
- 최신 필수 버전은 서버 상수 기준으로 검증합니다.
- 프론트는 로그인 직후 약관 동의 상태를 확인하고, 미완료면 전용 약관 동의 화면으로 이동합니다.

## 에러 처리 초안

권장 코드:

- `AUTH_OAUTH2_PROVIDER_REJECTED`
- `AUTH_OAUTH2_PROVIDER_USERINFO_MISSING`
- `AUTH_OAUTH2_PROVIDER_NOT_SUPPORTED`
- `AUTH_OAUTH2_PROCESSING_FAILED`
- `AUTH_OAUTH2_EXCHANGE_CODE_INVALID`
- `MEMBER_INACTIVE_MEMBER`
- `MEMBER_AGREEMENT_REQUIRED`
- `MEMBER_NICKNAME_REQUIRED`

의미:

- 사용자가 provider 동의를 취소했거나 제공자가 인증을 거절한 경우
- 필수 사용자 식별 정보가 누락된 경우
- 지원하지 않는 provider로 요청한 경우
- 내부 회원 처리 또는 토큰 발급 단계가 실패한 경우
- 단기 교환 코드가 없거나 유효하지 않거나 만료된 경우
- 이미 비활성화된 회원이 다시 로그인하려는 경우
- 필수 약관 동의가 필요한 상태로 핵심 API를 호출한 경우
- 닉네임 온보딩이 필요한 상태로 핵심 API를 호출한 경우

## 검증 시나리오 초안

- Google 로그인 시작 요청 시 Google 인증 페이지로 리다이렉트된다.
- Kakao 로그인 시작 요청 시 Kakao 인증 페이지로 리다이렉트된다.
- Naver 로그인 시작 요청 시 Naver 인증 페이지로 리다이렉트된다.
- 기존 소셜 회원은 기존 `memberId`로 로그인된다.
- 신규 소셜 회원은 즉시 생성 후 로그인된다.
- 신규 소셜 회원의 초기 nickname은 provider 제공 닉네임이 아니라 서버가 생성한 임시 닉네임이다.
- 신규 소셜 회원은 필수 약관 동의 미완료 상태로 로그인될 수 있다.
- 소셜 로그인 성공 후 프론트는 단기 교환 코드로 후속 교환 API를 호출할 수 있다.
- 후속 교환 API 성공 시 프론트는 Matchuri Access Token 기준으로 동일하게 후속 호출을 할 수 있다.
- 프론트는 `POST /api/v1/auth/refresh`로 브라우저 세션 복구와 access token 재발급을 수행할 수 있다.
- 필수 약관 미동의 회원은 로그인 후 약관 동의 화면으로 이동한다.
- 필수 약관 동의 완료 후에는 약관 API 응답의 새 Access Token으로 교체해야 한다.
- 약관 동의 완료 후 프론트는 닉네임 설정 화면에서 닉네임 중복검사 API를 호출할 수 있다.
- 닉네임 설정 완료 전에는 핵심 API 호출이 `MEMBER_NICKNAME_REQUIRED`로 차단된다.
- 닉네임 설정 API `PATCH /api/v1/members/me`는 인증은 필요하지만 온보딩 미완료 상태에서도 호출할 수 있다.
- 필수 약관 동의 완료 전에는 핵심 API 호출이 차단된다.
- 단기 교환 코드가 만료되거나 잘못되면 후속 교환 API는 인증 실패를 반환한다.
- 사용자가 provider 동의를 취소하면 프론트 실패 URL로 복귀한다.
- provider 사용자 식별자가 누락되면 로그인에 실패하고 적절한 에러 코드가 남는다.
- 비활성 회원은 소셜 로그인 성공 후에도 서비스 로그인은 거절된다.

## 후속 문서화 항목

- 실제 OpenAPI 또는 REST Docs 결과 반영
- provider별 사용자 정보 매핑 필드 확정
