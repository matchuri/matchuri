# 보안 기준

이 문서는 Matchuri backend 보안의 현재 정책만 남깁니다. 실제 변경 리뷰 절차는 `.agents/skills/matchuri-backend-security-review/SKILL.md`를 사용합니다.

목표는 소수 인원이 운영 가능한 단순한 구조를 유지하면서 `Spring Security` 기반 자체 로그인과 `OAuth2` 소셜 로그인을 확장할 수 있게 하는 것입니다.

## 현재 전제

- Backend는 Spring Boot 4 기반입니다.
- Backend는 EC2에 배포합니다.
- DB는 초기에는 EC2 내부 MySQL로 운영합니다.
- Frontend는 Vercel에 배포합니다.
- 시크릿은 Infisical을 기준 저장소로 관리합니다.
- Redis는 즉시 도입하지 않습니다.
- 인증은 세션보다 token 기반 구조를 우선합니다.
- 배포 인프라 기준은 `docs/decisions/backend-deployment-infrastructure.md`를 봅니다.

## 기본 원칙

- 시크릿은 저장소에 커밋하지 않습니다.
- 인증과 인가는 분리해서 판단합니다.
- 입력 검증은 request 경계에서 수행합니다.
- 실패 응답은 일관되게 주되 내부 구현 정보는 노출하지 않습니다.
- 구현 복잡도보다 운영 가능성을 우선합니다.
- 회원 식별 모델은 자체 로그인과 소셜 로그인을 함께 수용해야 합니다.

## 보호 대상

민감 정보:

- DB 접속 정보
- JWT secret 또는 signing key
- OAuth2 Client ID / Client Secret
- 서버 접속 정보
- 배포 자동화용 secret

서비스 데이터:

- 회원 계정 정보
- loginId, email, password hash
- 회원 취향 및 제한 재료 정보
- 그룹 초대 코드
- 인증 token 또는 token metadata
- 민감 정보가 포함될 수 있는 운영 log

## 인증 모델

- 인증 프레임워크는 `Spring Security`를 사용합니다.
- 자체 로그인은 `loginId + password` 기반으로 처리합니다.
- 자체 로그인 요청은 회원 조회와 비밀번호 비교 전에 CAPTCHA를 검증합니다.
- CAPTCHA 검증은 로컬 로그인에만 적용하고 OAuth2 로그인에는 적용하지 않습니다.
- 도메인 로그인 흐름은 `CaptchaVerifier`와 `CaptchaPurpose`만 사용하며 현재 공급자인 Google reCAPTCHA v3의 action, score, API 형식은 infra 어댑터에 격리합니다.
- 소셜 로그인은 `Spring Security OAuth2 Client`를 사용합니다.
- API 인증은 Matchuri JWT Access Token 기반으로 통일합니다.
- Frontend는 backend가 발급한 token만 기준으로 로그인 상태를 해석합니다.
- `Member`는 서비스 내부 회원 식별의 최종 기준입니다.
- 자체 로그인과 소셜 로그인은 인증 수단만 다르며 최종 사용자는 `Member`로 통합합니다.
- MVP 단계에서는 자동 계정 병합을 제공하지 않습니다.

## 필수 약관 정책

- 현재는 필수 약관 동의만 고려합니다.
- 필수 약관 종류는 `서비스 이용약관`, `개인정보 처리방침`입니다.
- 자체 로그인과 소셜 로그인 신규 가입 모두 같은 필수 약관 동의 기준을 사용합니다.
- 최신 필수 버전은 서버 상수로 관리합니다.
- 동의 이력은 `members`가 아니라 `member_agreements` 구조로 관리합니다.
- 로그인은 허용하되, 필수 약관 2종의 최신 필수 버전에 모두 동의하기 전까지 핵심 API 접근은 허용하지 않습니다.
- 필수 약관 동의 완료 시 backend는 최신 revision을 반영한 새 Access Token을 재발급합니다.

## OAuth2 정책

- 현재 지원 provider는 `Google`, `Kakao`, `Naver`입니다.
- 최초 소셜 로그인 성공 시 연결된 계정이 있으면 해당 `Member`로 로그인합니다.
- 연결된 계정이 없으면 신규 회원을 즉시 생성합니다.
- 소셜 로그인 직후 추가 정보 입력은 회원 생성의 선행 조건으로 두지 않고 로그인 후 onboarding으로 분리합니다.
- 소셜 제공자 token은 로그인 처리에 필요한 최소 범위로만 사용합니다.
- Matchuri API 인증에 provider token을 직접 사용하지 않습니다.
- OAuth2 성공 redirect에는 Access Token을 직접 노출하지 않고 단기 exchange code를 사용합니다.

## JWT와 Refresh Token 정책

- Access Token은 API 인증용입니다.
- Access Token claim은 `memberId`, `role`, `loginId`, 필수 약관 revision 등 최소 정보만 담습니다.
- 현재 구현은 Access Token + Refresh Token 구조를 사용합니다.
- Redis 미도입 단계에서는 Access Token 즉시 전역 무효화보다 짧은 만료 시간과 Refresh Token 차단을 우선합니다.
- Refresh Token은 로그인 단위 다중 저장을 기준으로 합니다.
- 로그아웃은 현재 로그인 세션의 Refresh Token 삭제와 cookie 제거를 의미합니다.
- 다중 로그인은 허용합니다.
- MVP 단계에서는 강제 로그아웃 기능을 제공하지 않습니다.
- JWT 서명은 현재 단일 backend 운영 구조를 기준으로 HMAC 대칭키 방식을 사용합니다.

## 인가 정책

공개 API:

- 회원 가입
- 로그인
- loginId 중복 확인
- 이메일 인증 코드 발송/확인
- loginId 찾기와 password reset
- OAuth2 시작 및 callback
- 공개 문서 endpoint
- health check endpoint

보호 API:

- `members/me`
- 취향 프로필 관리
- 개인 추천 요청/조회/선택
- 그룹 생성/참여/탈퇴
- 그룹 추천 session 시작
- 그룹 투표 및 최종 확정

인가 원칙:

- 본인 정보는 본인만 접근해야 합니다.
- 필수 약관 미동의 회원은 로그인되어 있어도 핵심 API에서 차단해야 합니다.
- 그룹 기능은 group member 여부를 반드시 확인해야 합니다.
- owner 전용 동작은 일반 member와 구분합니다.
- admin API는 service API와 path 및 문서 수준에서 분리합니다.

## Spring Security 기준

- 공개 경로는 whitelist 방식으로 최소한만 엽니다.
- 나머지 service API는 기본적으로 인증 필요 상태를 기본값으로 둡니다.
- 인증 이후에는 `로그인 필요`와 `필수 약관 동의 완료 필요`를 별도 조건으로 구분합니다.
- 현재 `application.yaml`의 `public-api-patterns`는 구현 시작점으로 사용하되, 실제 Security 설정이 생기면 한 곳에서 관리합니다.
- Swagger UI 경로는 `/docs/swagger-ui.html`입니다.
- OpenAPI 문서 경로는 `/docs/openapi`입니다.
- local에서는 `/docs/**` 익명 접근을 허용합니다.
- dev/prod 외부 노출 통제는 application 권한이 아니라 Nginx Basic Auth 같은 외부 진입점 통제를 우선합니다.
- OAuth2 handshake 검증에 필요한 짧은 중간 상태만 서버 session에 저장할 수 있습니다.

## 비밀번호와 계정 복구

- password는 hash로만 저장합니다.
- 권장 구현은 `BCryptPasswordEncoder`입니다.
- 평문 password는 log에 남기지 않습니다.
- password 비교 실패 시 상세 원인을 노출하지 않습니다.
- 신규 자체 로그인 회원가입은 이메일 인증을 회원 생성 전 조건으로 둡니다.
- loginId 찾기와 password reset은 이메일 인증을 통과한 경우에만 허용합니다.
- 인증 코드와 recovery token 원문은 log에 남기지 않습니다.
- password reset 성공 후 자동 로그인하지 않습니다.
- password reset 성공 시 해당 회원의 기존 Refresh Token 전체를 폐기합니다.
- 상세 설계는 `docs/decisions/email-verification-and-account-recovery.md`와 `docs/api/auth-email-verification.md`를 봅니다.

## Error response와 log

- 인증 실패는 `401`로 응답합니다.
- 인가 실패는 `403`으로 응답합니다.
- 리소스 없음은 `404`로 응답합니다.
- 중복/상태 충돌은 `409`로 응답합니다.
- error response에는 내부 class name, SQL, stack trace를 노출하지 않습니다.
- login 실패 메시지는 `loginId`와 password 중 무엇이 틀렸는지 구분하지 않습니다.
- OAuth2 실패는 frontend가 처리 가능한 code와 message로 정리합니다.
- password, Access Token, Refresh Token 원문은 log에 남기지 않습니다.
- CAPTCHA token과 secret key 원문은 log에 남기지 않습니다.
- CAPTCHA 토큰 거절은 `400`, 공급자 검증 서비스 장애는 `503`으로 구분하며 둘 다 fail-closed로 처리합니다.
- OAuth2 provider response 원문도 민감 정보 masking 없이 저장하지 않습니다.
- 인증 실패, 권한 실패, token 검증 실패는 원인 추적이 가능한 구조화 log를 남깁니다.

## 시크릿 관리

- 모든 시크릿은 Infisical을 source of truth로 사용합니다.
- Frontend에는 공개 site key인 `NEXT_PUBLIC_RECAPTCHA_SITE_KEY`만 주입합니다.
- Backend에는 `MATCHURI_GOOGLE_RECAPTCHA_SECRET_KEY`를 주입하며 frontend 환경에는 전달하지 않습니다.
- Backend 공급자 선택은 `MATCHURI_CAPTCHA_PROVIDER`로 주입하며 현재 값은 `google`입니다.
- 환경은 `development`, `staging`, `production`으로 분리합니다.
- `.env` 파일은 저장소에 커밋하지 않습니다.
- GitHub Actions workflow는 OIDC 기반 단기 권한을 우선합니다.
- 애플리케이션 secret을 GitHub repository secret에 장기 저장하지 않습니다.
- Frontend 공개 환경 변수는 Infisical `App Connection + Secret Sync`를 통해 Vercel 프로젝트 환경 변수로 동기화합니다.

## 보류 항목

- Refresh Token 회전 전략의 최종안
- 추가 OAuth2 provider 범위와 우선순위
- 다중 기기 session 관리 UI
- 강제 로그아웃 정책
- JWT secret 회전 운영 절차

## 관련 skill

- security review: `.agents/skills/matchuri-backend-security-review/SKILL.md`
