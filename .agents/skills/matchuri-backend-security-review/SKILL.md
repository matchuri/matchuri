---
name: matchuri-backend-security-review
description: Matchuri backend 보안을 리뷰한다. 인증, 인가, Spring Security, OAuth2, JWT, Refresh Token, 비밀번호, 필수 약관, 시크릿, 로그, error response, 공개/보호 API 변경을 점검할 때 사용한다.
---

# Matchuri Backend 보안 리뷰

## 개요

backend 변경이 인증, 인가, 시크릿, 로그, error response 기준을 깨지 않는지 확인한다. 구현 복잡도보다 소수 팀이 운영 가능한 보안 기준을 우선한다.

## 먼저 읽을 것

1. root `AGENTS.md`
2. `backend/AGENTS.md`
3. `docs/backend/security.md`
4. `docs/decisions/backend-deployment-infrastructure.md`
5. 인증/API 변경이면 관련 `docs/api/*.md`
6. 이메일 인증과 계정 복구 변경이면 `docs/decisions/email-verification-and-account-recovery.md`

구현 기준을 찾기 위해 GitHub Wiki나 local Wiki folder를 읽지 않는다.

## 절차

1. 보안 영향 범위를 식별한다.
   - 인증 수단: local login, OAuth2, JWT, Refresh Token
   - 인가 대상: public API, protected API, member-owned resource, group member/owner action
   - 민감 정보: password, token, email verification code, OAuth2 provider response, DB secret
   - 공개 surface: endpoint, redirect URL, Swagger/OpenAPI, log

2. 시크릿 노출을 확인한다.
   - `.env`, token, password, client secret, DB password가 repo에 추가되지 않았는지 확인한다.
   - secret source of truth가 Infisical 기준과 충돌하지 않는지 확인한다.
   - GitHub Actions, Vercel, EC2 설정값과 application secret을 구분한다.

3. 인증 흐름을 확인한다.
   - 자체 로그인은 `loginId + password` 기준을 유지한다.
   - password는 hash로만 저장하고 log에 남기지 않는다.
   - OAuth2 성공 후 provider token을 Matchuri API 인증에 직접 쓰지 않는다.
   - OAuth2 성공 redirect에는 Access Token을 직접 노출하지 않는다.
   - 단기 exchange code와 Matchuri JWT 발급 흐름을 확인한다.

4. token 정책을 확인한다.
   - Access Token은 API 인증용 최소 claim만 담는다.
   - Refresh Token은 재발급 차단과 logout 의미를 구현 기준과 맞춘다.
   - Redis 미도입 상태에서 Access Token 전역 즉시 무효화를 가정하지 않는다.
   - token 원문을 log, URL, response에 불필요하게 노출하지 않는다.

5. 인가와 필수 약관을 확인한다.
   - public API는 whitelist로 최소화한다.
   - 보호 API는 기본적으로 인증 필요로 둔다.
   - 본인 resource는 본인만 접근하게 한다.
   - group action은 group member 여부와 owner 권한을 분리한다.
   - 필수 약관 미동의 회원은 핵심 API에서 차단한다.
   - 약관 상태 조회/동의 제출 예외 범위를 명확히 한다.

6. error response와 log를 확인한다.
   - 인증 실패는 `401`, 인가 실패는 `403`으로 구분한다.
   - 내부 class name, SQL, stack trace를 response에 노출하지 않는다.
   - login 실패는 계정 존재 여부를 과도하게 드러내지 않는다.
   - 인증 실패, 권한 실패, token 검증 실패는 추적 가능한 구조화 log를 남긴다.
   - password, Access Token, Refresh Token, 인증 코드 원문은 log에 남기지 않는다.

7. 문서와 테스트를 확인한다.
   - 인증 필요 여부를 OpenAPI와 `docs/api`에 반영한다.
   - API 변경이면 `matchuri-backend-api-change`도 사용한다.
   - cross-stack 인증 흐름이 바뀌면 `matchuri-api-contract-sync`도 사용한다.
   - 가능한 경우 `backend`에서 `./gradlew test`를 실행한다.

## 주요 기준

- `Member`는 내부 회원 식별의 최종 기준이다.
- 자체 로그인과 OAuth2는 하나의 `Member` 모델로 수렴한다.
- 필수 약관 동의 완료와 계정 생성은 같은 개념이 아니다.
- 자동 계정 병합은 MVP 범위에서 제공하지 않는다.
- Swagger/OpenAPI endpoint는 application 권한보다 외부 진입점 통제로 보호한다.
- local 개발과 dev/prod 노출 정책을 섞지 않는다.

## 보고 형식

보안 리뷰를 끝낼 때 아래를 보고한다.

- 영향 받은 인증/인가 surface
- 확인한 secret/log/token 노출 위험
- public/protected API 변경 여부
- 실행한 test 또는 실행하지 못한 이유
- 즉시 수정할 보안 risk
- 후속 보류 항목
