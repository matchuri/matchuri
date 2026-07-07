# API 문서 인덱스

이 문서는 Matchuri의 현재 API 문서 기준 위치를 빠르게 안내합니다.
최신 계약과 운영 규칙은 이 인덱스에서 시작합니다.

## 관련 문서

- 상위 포털: `docs/README.md`
- 설계 판단: `docs/decisions/index.md`
- 데이터 모델: `docs/data/index.md`

## 현재 기준

- 계약 기준: 코드와 함께 유지되는 OpenAPI 메타데이터와 `/docs/openapi` 산출물
- 전체 API 상태표: `docs/api/api-status.md`
- API 넘버링/버저닝 정책: `docs/api/api-numbering-policy.md`
- 문서화 전략: `docs/decisions/api-docs-strategy.md`
- 구현 실무 기준: `docs/backend/guide.md`

## 먼저 볼 문서

1. `docs/decisions/documentation-source-of-truth.md`
2. `docs/decisions/api-docs-strategy.md`
3. `docs/api/api-status.md`
4. `docs/api/api-numbering-policy.md`
5. `docs/backend/guide.md`

## 도메인별 API 문서

### Auth

- Google/Kakao/Naver OAuth2 로그인 API: `docs/api/auth-google-oauth2.md`
- 인증 세션 API: `docs/api/auth-session.md`
- 이메일 인증과 계정 복구 API: `docs/api/auth-email-verification.md`

### Member

- 자체 회원가입 통합 API: `docs/api/member-local-signup.md`
- 회원 프로필 및 공개 조회 API: `docs/api/member-profile.md`
- 회원 필수 약관 동의 API: `docs/api/member-required-agreements.md`
- 필수 약관 동의 에러 코드: `docs/api/member-required-agreements-error-codes.md`
- 필수 약관 동의 테스트 시나리오: `docs/api/member-required-agreements-test-scenarios.md`

### Menu

- 메뉴 참조 데이터 API: `docs/api/menu-reference.md`
- 메뉴 카탈로그 API: `docs/api/menu-catalog.md`

### Recommendation

- 추천 API: `docs/api/recommendation.md`

### Group

- 그룹 의사결정 API: `docs/api/group.md`

### Realtime

- 실시간 이벤트 API: `docs/api/realtime.md`
- SSE 프론트 연동 가이드: `docs/api/realtime-frontend-guide.md`

### Ops

- 헬스체크 API: `docs/api/health.md`

## 읽는 방법

- "현재 어떤 방식으로 API 문서를 관리하나?"가 궁금하면 문서화 전략 문서를 먼저 봅니다.
- "전체 API 중 무엇이 real/mock/planned 상태인가?"가 궁금하면 `docs/api/api-status.md`를 봅니다.
- "API ID를 어떻게 부여하고 유지하나?"가 궁금하면 `docs/api/api-numbering-policy.md`를 봅니다.
- "현재 계약의 authoritative source가 어디인가?"가 궁금하면 문서 기준 위치 문서를 봅니다.
- "백엔드 구현 시 어떤 규칙을 따라야 하나?"가 궁금하면 백엔드 가이드를 봅니다.
- 특정 도메인의 API 계약이 궁금하면 위 도메인별 API 문서에서 시작합니다.
- 특정 endpoint의 구현 상태가 궁금하면 `docs/api/api-status.md`에서 상태와 기준 문서를 확인합니다.

## 유지보수 원칙

- API 계약이 바뀌면 OpenAPI와 관련 `docs/` 문서를 먼저 갱신하고, 필요한 테스트를 함께 맞춥니다.
- 새 API를 추가하거나 mock에서 real로 전환하면 `docs/api/api-status.md` 상태표를 갱신합니다.
- 문서가 어긋나면 구현과 OpenAPI 산출물을 우선 확인합니다.
