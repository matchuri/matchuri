# 열린 의사결정

이 문서는 Matchuri에서 아직 확정하지 않은 중요한 설계/운영 결정을 모아둡니다.
목적은 사람과 에이전트가 빈칸을 임의로 확정하지 않도록 막고, 현재 미정 상태를 명시적으로 관리하는 것입니다.

## 사용 원칙

- 이미 확정된 내용은 이 문서가 아니라 해당 운영 문서로 옮깁니다.
- 이 문서에는 "아직 안 정했지만 작업에 영향을 주는 것"만 남깁니다.
- 임시 방침이 있으면 함께 적고, 최종 결정 전까지는 그 범위 안에서만 작업합니다.

## 1. Refresh Token 전략

- 상태: Closed
- 왜 중요한가:
  로그인/로그아웃, 재인증, 보안 정책, 프론트 세션 처리에 직접 영향을 줍니다.
- 현재 옵션:
  - 옵션 A. 회원당 단일 Refresh Token 저장
  - 옵션 B. 로그인 단위 다중 Refresh Token 저장
  - 옵션 C. Refresh Token 무저장 운영
- 현재 임시 방침:
  자체 로그인과 Google OAuth2 로그인 모두 같은 Refresh Token 정책을 사용합니다.
  재발급 API는 2단계 범위에서 제외하고, 로그아웃은 Refresh Token 차단 중심으로 정의합니다.
- 옵션 비교:
  - 옵션 A. 회원당 단일 Refresh Token 저장
    - 장점: 구현이 가장 단순하고 로그아웃 의미가 명확합니다.
    - 단점: 다른 기기에서 새 로그인 시 이전 로그인 세션이 사실상 무효화됩니다.
    - 적합한 경우: 빠른 MVP, 소규모 사용자, 기기별 세션 제어가 아직 필요 없을 때
  - 옵션 B. 로그인 단위 다중 Refresh Token 저장
    - 장점: 다중 로그인 허용 정책과 가장 잘 맞고 이후 재발급 API로 확장하기 쉽습니다.
    - 단점: 저장 구조, 만료 관리, 정리 작업이 더 복잡합니다.
    - 적합한 경우: 모바일/웹 병행 사용, 기기별 세션 관리가 곧 필요할 때
  - 옵션 C. Refresh Token 무저장 운영
    - 장점: 구현과 저장 구조가 단순합니다.
    - 단점: 로그아웃, 탈퇴, 의심 세션 차단 같은 서버 제어가 약합니다.
    - 적합한 경우: 완전 단기 프로토타입
- 권장안:
  - 현재는 옵션 B를 권장합니다.
  - 이유: 모바일과 웹을 함께 고려하는 웹앱 특성상 다중 기기 로그인 경험을 자연스럽게 유지하기 더 적합합니다.
- 결정 필요 시점:
  결정 완료
- 최종 결정:
  - 2단계 회원/인증 구현은 `로그인 단위 다중 Refresh Token 저장`을 사용합니다.
  - 자체 로그인과 Google OAuth2 로그인은 같은 Refresh Token 정책을 사용합니다.
  - 로그아웃은 현재 로그인 세션의 Refresh Token만 삭제합니다.
  - `POST /api/v1/auth/refresh` 재발급 API를 제공합니다.
  - 현재 구현은 재발급 시 기존 Refresh Token을 같은 로그인 세션 안에서 회전합니다.
  - 기기 식별 기반 세션 관리나 재발급 정책 고도화는 후속 단계로 미룹니다.
- 관련 문서:
  - 내부 실행 계획 기록
  - `docs/backend/security.md`

## 2. 로그아웃의 서버 의미

- 상태: Closed
- 왜 중요한가:
  인증 필터, 프론트 세션 처리, 추후 Redis 도입 여부에 영향을 줍니다.
- 현재 옵션:
  - 클라이언트 토큰 폐기 중심
  - 서버 측 최소 상태 변경 중심
- 현재 임시 방침:
  Redis 없이 시작하므로 즉시 전역 무효화는 전제로 두지 않습니다.
- 결정 필요 시점:
  결정 완료
- 최종 결정:
  - 2단계 로그아웃은 현재 로그인 세션의 Refresh Token 삭제와 쿠키 제거를 의미합니다.
  - 이미 발급된 Access Token은 서버에서 즉시 전역 무효화하지 않습니다.
  - Access Token은 만료 시점까지 유효하며, 보호 API는 기존과 동일하게 호출될 수 있습니다.
  - 강제 로그아웃, 전역 토큰 차단, 블랙리스트 저장소는 후속 단계로 미룹니다.
- 관련 문서:
  - 내부 실행 계획 기록
  - `docs/decisions/domain-language.md`

## 3. Infisical 시크릿 주입 방식

- 상태: Closed
- 왜 중요한가:
  CI/CD, EC2 런타임, Vercel 연동 방식과 직접 연결됩니다.
- 현재 옵션:
  - GitHub Actions에서 시크릿을 받아 서버 환경 변수로 주입
  - EC2에서 Infisical CLI 또는 런타임 주입 방식 사용
  - Frontend/Vercel과 별도 연동
- 현재 임시 방침:
  Infisical은 source of truth로 사용하되, 백엔드 CD는 `GitHub Actions OIDC -> Infisical Secrets Action -> EC2 환경 파일 반영` 흐름을 사용합니다.
- 결정 필요 시점:
  결정 완료
- 최종 결정:
  - 백엔드 CD의 애플리케이션 시크릿은 GitHub Actions가 OIDC로 Infisical에 인증한 뒤 실행 시점에 가져옵니다.
  - GitHub Actions workflow에는 `id-token: write` 권한을 부여합니다.
  - Infisical identity는 GitHub repository, branch 또는 environment 조건으로 좁혀서 허용합니다.
  - 애플리케이션 환경 변수는 배포 시 EC2의 `/etc/matchuri/backend.env`로 반영합니다.
  - 운영 배포 보호는 GitHub Environment 규칙과 Infisical OIDC subject 제한을 함께 사용합니다.
  - 프론트 공개 환경 변수는 Infisical `Secret Sync`가 Vercel 프로젝트 환경 변수로 동기화합니다.
  - 프론트 Preview/Production 배포는 Vercel 기본 Git 배포를 사용합니다.
- 관련 문서:
  - `docs/backend/security.md`
  - 내부 운영 문서
  - 내부 운영 문서

## 4. Redis 도입 시점

- 상태: Open
- 왜 중요한가:
  실시간 상태 공유, 세션 관리, 캐싱, 로그아웃 전략과 연결됩니다.
- 현재 옵션:
  - MVP 단계에서 도입하지 않는다.
  - 실시간성 또는 성능 병목이 확인되면 이후 도입한다.
- 현재 임시 방침:
  Redis는 지금 즉시 도입하지 않습니다.
  먼저 단순 구조에서 병목을 체감하고 필요성이 분명해질 때 도입합니다.
- 결정 필요 시점:
  그룹 추천/투표의 실시간 요구가 커지거나 성능 이슈가 발생할 때
- 관련 문서:
  - `docs/backend/architecture.md`
  - `docs/backend/reliability.md`
  - `docs/backend/guide.md`

## 5. 비회원 추천 범위

- 상태: Open
- 왜 중요한가:
  인증 경계, 개인 추천 흐름, 프론트 온보딩 설계에 직접 영향을 줍니다.
- 현재 옵션:
  - 비회원은 일회성 개인 추천만 허용
  - 비회원도 일부 저장형 기능 직전까지 허용
  - 회원 전용으로 제한
- 현재 임시 방침:
  비회원 추천 기능은 존재하지만, 회원 전용 기능과 동일한 권한 경계로 취급하지 않습니다.
- 결정 필요 시점:
  개인 추천 API와 프론트 온보딩 흐름 연결 전
- 관련 문서:
  - `docs/product/product-sense.md`
  - `docs/product/specs/new-user-onboarding.md`
  - `docs/backend/security.md`

## 6. 소셜 로그인 도입 시점

- 상태: Closed
- 왜 중요한가:
  회원 가입/로그인 UX와 인증 구조가 달라집니다.
- 현재 옵션:
  - 자체 로그인 먼저 구현
  - OAuth2/SNS 로그인까지 MVP에 포함
- 현재 임시 방침:
  2단계 회원/인증 구현에 자체 로그인과 Google OAuth2 소셜 로그인을 함께 포함합니다.
- 결정 필요 시점:
  결정 완료
- 최종 결정:
  - 2단계 1차 제공자는 `Google`만 지원합니다.
  - 소셜 로그인 성공 후에는 Matchuri JWT만 사용합니다.
  - 신규 소셜 회원은 즉시 생성합니다.
  - 계정 통합 기능은 제공하지 않습니다.
- 관련 문서:
  - 내부 실행 계획 기록
  - `docs/api/auth-google-oauth2.md`
  - `docs/product/product-sense.md`

## 7. Frontend 기술 스택 최종 확정

- 상태: Open
- 왜 중요한가:
  프론트 문서화, API 연동 방식, 배포/환경 변수 방식에 영향을 줍니다.
- 현재 옵션:
  - 현재 코드베이스 기준 유지
  - UI/상태관리/데이터 패칭 패턴을 별도 확정
- 현재 임시 방침:
  현재 세션에서는 백엔드/서버/인프라에 집중하고, 프론트 최종 스택은 나중에 확정합니다.
- 결정 필요 시점:
  프론트 구현 규칙을 본격 문서화할 때
- 관련 문서:
  - `AGENTS.md`
  - `docs/backend/architecture.md`

## 8. Member 도메인의 Custom Repository 도입 시점

- 상태: Open
- 왜 중요한가:
  패키지 구조, 서비스 책임, 쿼리 복잡도에 영향을 줍니다.
- 현재 옵션:
  - 초기에는 기본 `JpaRepository`만 사용
  - 동적 쿼리나 조회 모델이 필요해질 때 Custom Repository 도입
- 현재 임시 방침:
  지금은 Custom Repository를 서두르지 않고 `TBD`로 둡니다.
- 결정 필요 시점:
  서비스에 쿼리 조립 책임이 새기 시작할 때
- 관련 문서:
  - `docs/frontend/guide.md`
  - `docs/backend/guide.md`

## 9. 그룹 투표 상태의 프론트 반영 방식

- 상태: Closed
- 왜 중요한가:
  실시간 처리 방식, API 설계, 향후 Redis/WebSocket 구조와 연결됩니다.
- 현재 옵션:
  - 단순 폴링 기반
  - WebSocket 기반 실시간 반영
  - 혼합 방식
- 최종 결정:
  1차 구현은 SSE(Server-Sent Events)로 진행합니다.
  현재 요구는 클라이언트가 서버로 실시간 메시지를 보내는 양방향 협업보다, 기존 HTTP 상태 변경 이후 관련 사용자에게 서버가 알려주는 단방향 푸시 성격이 강합니다.
  WebSocket/STOMP와 Redis pub-sub은 다중 인스턴스, 정확한 presence, 양방향 메시징 요구가 분명해질 때 재검토합니다.
- 관련 문서:
  - `docs/backend/architecture.md`
  - `docs/product/specs/group-lunch-recommendation.md`
  - 내부 실행 계획 기록

## 10. 자체 로그인 이메일 필수화와 계정 복구 정책

- 상태: Closed
- 왜 중요한가:
  로그인 ID 찾기와 비밀번호 재설정은 계정 소유 확인 수단이 필요하며, 자체 로그인 회원가입에서 이메일을 언제 필수화할지에 따라 프론트 회원가입 흐름과 기존 회원 복구 가능 범위가 달라집니다.
- 현재 옵션:
  - 신규 자체 회원가입부터 이메일 인증을 필수로 둔다.
  - 계정 복구 기능 배포 이후 생성되는 계정부터 이메일 인증을 필수로 둔다.
  - 이메일은 선택 입력으로 두고, 이메일이 등록된 계정만 복구를 허용한다.
- 최종 결정:
  신규 자체 회원가입부터 이메일 인증을 필수로 둡니다.
  자체 회원가입 요청은 검증된 이메일을 포함해야 하며, 회원 생성 전에 `SIGNUP` 목적의 이메일 인증이 완료되어야 합니다.
  한 이메일에 여러 자체 로그인 ID를 허용하지 않습니다.
  비밀번호 재설정 성공 시 해당 회원의 기존 refresh token을 모두 폐기합니다.
  기존 `POST /api/v1/auth/email`은 별도 호환 경로를 두지 않고 직접 수정합니다.
  기존 자체 로그인 계정 중 이메일이 없는 계정은 별도 이메일 보강 흐름이 생기기 전까지 ID/PW 찾기 대상에서 제외합니다.
- 관련 문서:
  - `docs/decisions/email-verification-and-account-recovery.md`
  - `docs/api/auth-email-verification.md`
  - 내부 실행 계획 기록

## 닫는 방법

- 결정이 끝나면 해당 항목의 상태를 `Closed`로 바꾸고, 최종 결론을 적습니다.
- 이후 이 문서에만 남기지 말고, 관련 운영 문서에도 반영합니다.
