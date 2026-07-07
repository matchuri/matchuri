# Matchuri API 상태표

이 문서는 Matchuri 공식 API의 전체 현황을 한눈에 보기 위한 상태표입니다.
상세 계약은 각 API 문서와 코드의 OpenAPI 메타데이터, `/docs/openapi`, Swagger UI를 기준으로 봅니다.

- 마지막 정리일: 2026-06-01
- API ID 정책: `docs/api/api-numbering-policy.md`

## API ID 기준

API ID는 FE-BE 간 커뮤니케이션과 Swagger UI 정렬을 위한 고유 식별자입니다.
URL 경로나 `/api/v1` 같은 API path version을 대체하지 않습니다.

- 형식: `FLOW.NNN.NNN`
- `FLOW`: 큰 사용자 플로우를 나타내는 고유 영문 코드
- 첫 번째 숫자 구간: 플로우 안의 기본 API 순서
- 두 번째 숫자 구간: 중간 삽입이나 세부 변형을 위한 여백
- 기본 API는 `AUTH.020.000`처럼 마지막 숫자 구간을 `000`으로 둡니다.
- 중간 API 추가가 필요하면 `AUTH.020.500`처럼 마지막 숫자 구간을 사용합니다.
- 이미 공유된 API ID는 원칙적으로 변경하거나 재사용하지 않습니다.
- 마지막 정리일: 2026-06-01
- API ID 정책: `docs/api/api-numbering-policy.md`

## API ID 기준

API ID는 FE-BE 간 커뮤니케이션과 Swagger UI 정렬을 위한 고유 식별자입니다.
URL 경로나 `/api/v1` 같은 API path version을 대체하지 않습니다.

- 형식: `FLOW.NNN.NNN`
- `FLOW`: 큰 사용자 플로우를 나타내는 고유 영문 코드
- 첫 번째 숫자 구간: 플로우 안의 기본 API 순서
- 두 번째 숫자 구간: 중간 삽입이나 세부 변형을 위한 여백
- 기본 API는 `AUTH.020.000`처럼 마지막 숫자 구간을 `000`으로 둡니다.
- 중간 API 추가가 필요하면 `AUTH.020.500`처럼 마지막 숫자 구간을 사용합니다.
- 이미 공유된 API ID는 원칙적으로 변경하거나 재사용하지 않습니다.

## 상태 기준

| 상태 | 의미 |
| --- | --- |
| `real` | 실제 service/domain 로직과 연결된 API입니다. |
| `mock` | 실제 API 경로와 DTO를 사용하지만, Controller에서 더미 응답을 반환하는 API입니다. |
| `planned` | 제품/아키텍처상 필요하지만 아직 현재 기준 API 계약이나 Controller가 완성되지 않은 API입니다. |
| `docs-only` | 문서 기준은 있으나 구현 상태 확인이나 코드 연결이 필요한 API입니다. |
| `deprecated` | 호환 목적으로 남아 있으나 신규 구현의 기본 경로가 아닌 API입니다. |

## 유지보수 규칙

- 새 API 계약을 추가하면 이 문서에 행을 추가합니다.
- 새 API에는 `docs/api/api-numbering-policy.md` 기준에 맞는 API ID를 부여합니다.
- 새 API에는 `docs/api/api-numbering-policy.md` 기준에 맞는 API ID를 부여합니다.
- Mock API를 추가하면 상태를 `mock`으로 표시합니다.
- 실제 비즈니스 로직 전환이 끝나면 상태를 `real`로 변경합니다.
- 기존 API를 대체하는 새 API가 생기면 이전 API를 `deprecated`로 표시하고 비고에 대체 경로를 적습니다.
- Deprecated API의 API ID는 재사용하지 않습니다.
- Deprecated API의 API ID는 재사용하지 않습니다.
- API 상세 계약이 바뀌면 이 상태표, 관련 `docs/api/*` 문서, `XXXApi.java` Swagger 메타데이터를 함께 확인합니다.

## OPS. 공통/운영
## OPS. 공통/운영

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `OPS.010.000` | Health | GET | `/api/v1/health` | `real` | `docs/api/health.md` | 공개 헬스체크 |
| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `OPS.010.000` | Health | GET | `/api/v1/health` | `real` | `docs/api/health.md` | 공개 헬스체크 |

## AUTH. 인증/가입 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `AUTH.010.000` | Auth | POST | `/api/v1/auth/email` | `real` | `docs/api/auth-email-verification.md` | 이메일 인증 코드 발송 |
| `AUTH.020.000` | Auth | POST | `/api/v1/auth/email/confirm` | `real` | `docs/api/auth-email-verification.md` | 이메일 인증 확인 |
| `AUTH.030.000` | Member | GET | `/api/v1/members/exists/{loginId}` | `real` | `docs/api/member-profile.md` | 로그인 ID 중복 확인 |
| `AUTH.040.000` | Member | GET | `/api/v1/members/exists/nickname/{nickname}` | `real` | `docs/api/member-profile.md` | 닉네임 중복 확인 |
| `AUTH.050.000` | Member | POST | `/api/v1/members/signup` | `real` | `docs/api/member-local-signup.md` | 자체 회원가입 기본 경로 |
| `AUTH.060.000` | Auth | GET | `/api/v1/auth/oauth2/{provider}` | `real` | `docs/api/auth-google-oauth2.md` | Google/Kakao/Naver OAuth2 시작 |
| `AUTH.070.000` | Auth | POST | `/api/v1/auth/oauth2/exchange` | `real` | `docs/api/auth-google-oauth2.md` | OAuth2 code 교환 |
| `AUTH.080.000` | Auth | POST | `/api/v1/auth/login` | `real` | `docs/api/auth-session.md` | 로컬 로그인 |
| `AUTH.090.000` | Auth | POST | `/api/v1/auth/refresh` | `real` | `docs/api/auth-session.md` | refresh token 기반 재발급 |
| `AUTH.100.000` | Auth | POST | `/api/v1/auth/logout` | `real` | `docs/api/auth-session.md` | 현재 세션 로그아웃 |
| `AUTH.110.000` | Auth | POST | `/api/v1/auth/recovery/login-id` | `real` | `docs/api/auth-email-verification.md` | 로그인 ID 찾기 |
| `AUTH.120.000` | Auth | POST | `/api/v1/auth/recovery/password` | `real` | `docs/api/auth-email-verification.md` | 비밀번호 재설정 |
| `AUTH.900.000` | Member | POST | `/api/v1/members` | `deprecated` | `docs/api/member-profile.md` | 레거시 회원 생성. 신규 구현은 `/api/v1/members/signup` 사용 |
## AUTH. 인증/가입 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `AUTH.010.000` | Auth | POST | `/api/v1/auth/email` | `real` | `docs/api/auth-email-verification.md` | 이메일 인증 코드 발송 |
| `AUTH.020.000` | Auth | POST | `/api/v1/auth/email/confirm` | `real` | `docs/api/auth-email-verification.md` | 이메일 인증 확인 |
| `AUTH.030.000` | Member | GET | `/api/v1/members/exists/{loginId}` | `real` | `docs/api/member-profile.md` | 로그인 ID 중복 확인 |
| `AUTH.040.000` | Member | GET | `/api/v1/members/exists/nickname/{nickname}` | `real` | `docs/api/member-profile.md` | 닉네임 중복 확인 |
| `AUTH.050.000` | Member | POST | `/api/v1/members/signup` | `real` | `docs/api/member-local-signup.md` | 자체 회원가입 기본 경로 |
| `AUTH.060.000` | Auth | GET | `/api/v1/auth/oauth2/{provider}` | `real` | `docs/api/auth-google-oauth2.md` | Google/Kakao/Naver OAuth2 시작 |
| `AUTH.070.000` | Auth | POST | `/api/v1/auth/oauth2/exchange` | `real` | `docs/api/auth-google-oauth2.md` | OAuth2 code 교환 |
| `AUTH.080.000` | Auth | POST | `/api/v1/auth/login` | `real` | `docs/api/auth-session.md` | 로컬 로그인 |
| `AUTH.090.000` | Auth | POST | `/api/v1/auth/refresh` | `real` | `docs/api/auth-session.md` | refresh token 기반 재발급 |
| `AUTH.100.000` | Auth | POST | `/api/v1/auth/logout` | `real` | `docs/api/auth-session.md` | 현재 세션 로그아웃 |
| `AUTH.110.000` | Auth | POST | `/api/v1/auth/recovery/login-id` | `real` | `docs/api/auth-email-verification.md` | 로그인 ID 찾기 |
| `AUTH.120.000` | Auth | POST | `/api/v1/auth/recovery/password` | `real` | `docs/api/auth-email-verification.md` | 비밀번호 재설정 |
| `AUTH.900.000` | Member | POST | `/api/v1/members` | `deprecated` | `docs/api/member-profile.md` | 레거시 회원 생성. 신규 구현은 `/api/v1/members/signup` 사용 |

## ONB. 온보딩/내 정보 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `ONB.010.000` | Member Agreement | GET | `/api/v1/member-agreements/required-status` | `real` | `docs/api/member-required-agreements.md` | 필수 약관 상태 조회 |
| `ONB.020.000` | Member Agreement | POST | `/api/v1/member-agreements/consents` | `real` | `docs/api/member-required-agreements.md` | 필수 약관 동의 제출 |
| `ONB.030.000` | Member | GET | `/api/v1/members/me` | `real` | `docs/api/member-profile.md` | 내 프로필 조회 |
| `ONB.040.000` | Member | PATCH | `/api/v1/members/me` | `real` | `docs/api/member-profile.md` | 내 기본 정보 수정 |
| `ONB.050.000` | Member | PATCH | `/api/v1/members/me/password` | `real` | `docs/api/member-profile.md` | 로그인 상태 비밀번호 변경 |
| `ONB.060.000` | Member | GET | `/api/v1/members/me/taste-profile` | `real` | `docs/api/member-profile.md` | 내 취향 프로필 조회 |
| `ONB.070.000` | Member | PATCH | `/api/v1/members/me/taste-profile` | `real` | `docs/api/member-profile.md` | 내 취향 프로필 전체 교체 저장 |
| `ONB.080.000` | Member | DELETE | `/api/v1/members/me` | `real` | `docs/api/member-profile.md` | 회원 탈퇴 |

## REF. 메뉴/취향 참조 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `REF.010.000` | Menu | GET | `/api/v1/attribute-categories` | `real` | `docs/api/menu-reference.md` | 공개 attribute category 목록 |
| `REF.020.000` | Menu | GET | `/api/v1/restriction-ingredients` | `real` | `docs/api/menu-reference.md` | 공개 restriction ingredient 목록 |
| `REF.030.000` | Menu | GET | `/api/v1/menu-items` | `real` | `docs/api/menu-catalog.md` | 공개 메뉴 목록 |
| `REF.040.000` | Menu | GET | `/api/v1/menu-items/{menuItemId}` | `real` | `docs/api/menu-catalog.md` | 공개 메뉴 상세 |
## ONB. 온보딩/내 정보 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `ONB.010.000` | Member Agreement | GET | `/api/v1/member-agreements/required-status` | `real` | `docs/api/member-required-agreements.md` | 필수 약관 상태 조회 |
| `ONB.020.000` | Member Agreement | POST | `/api/v1/member-agreements/consents` | `real` | `docs/api/member-required-agreements.md` | 필수 약관 동의 제출 |
| `ONB.030.000` | Member | GET | `/api/v1/members/me` | `real` | `docs/api/member-profile.md` | 내 프로필 조회 |
| `ONB.040.000` | Member | PATCH | `/api/v1/members/me` | `real` | `docs/api/member-profile.md` | 내 기본 정보 수정 |
| `ONB.050.000` | Member | PATCH | `/api/v1/members/me/password` | `real` | `docs/api/member-profile.md` | 로그인 상태 비밀번호 변경 |
| `ONB.060.000` | Member | GET | `/api/v1/members/me/taste-profile` | `real` | `docs/api/member-profile.md` | 내 취향 프로필 조회 |
| `ONB.070.000` | Member | PATCH | `/api/v1/members/me/taste-profile` | `real` | `docs/api/member-profile.md` | 내 취향 프로필 전체 교체 저장 |
| `ONB.080.000` | Member | DELETE | `/api/v1/members/me` | `real` | `docs/api/member-profile.md` | 회원 탈퇴 |

## REF. 메뉴/취향 참조 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `REF.010.000` | Menu | GET | `/api/v1/attribute-categories` | `real` | `docs/api/menu-reference.md` | 공개 attribute category 목록 |
| `REF.020.000` | Menu | GET | `/api/v1/restriction-ingredients` | `real` | `docs/api/menu-reference.md` | 공개 restriction ingredient 목록 |
| `REF.030.000` | Menu | GET | `/api/v1/menu-items` | `real` | `docs/api/menu-catalog.md` | 공개 메뉴 목록 |
| `REF.040.000` | Menu | GET | `/api/v1/menu-items/{menuItemId}` | `real` | `docs/api/menu-catalog.md` | 공개 메뉴 상세 |

## REC. 개인 추천 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `REC.010.000` | Guest Recommendation | POST | `/api/v1/guest/recommendations` | `real` | `docs/api/recommendation.md` | 비회원 개인 추천 실행. 저장 이력 없이 후보만 반환 |
| `REC.020.000` | Personal Recommendation | GET | `/api/v1/personal/recommendations` | `real` | `docs/api/recommendation.md` | 내 개인 추천 이력 목록 조회 |
| `REC.030.000` | Personal Recommendation | POST | `/api/v1/personal/recommendations` | `real` | `docs/api/recommendation.md` | 열린 개인 추천이 없을 때 개인 추천 실행 요청 |
| `REC.040.000` | Personal Recommendation | POST | `/api/v1/personal/recommendations/{requestId}/reroll` | `real` | `docs/api/recommendation.md` | 이전 개인 추천이 아직 닫히지 않았으면 종료하고 새 개인 추천 실행 |
| `REC.050.000` | Personal Recommendation | GET | `/api/v1/personal/recommendations/{requestId}` | `real` | `docs/api/recommendation.md` | 개인 추천 요청 상세 |
| `REC.060.000` | Personal Recommendation | GET | `/api/v1/personal/recommendations/{requestId}/candidates` | `real` | `docs/api/recommendation.md` | 개인 추천 후보 목록 |
| `REC.070.000` | Personal Recommendation | PATCH | `/api/v1/personal/recommendations/{requestId}` | `real` | `docs/api/recommendation.md` | 닫히지 않은 개인 추천 선택 반영, `SELECTED` 종료, CHOOSE 로그 저장 |
## REC. 개인 추천 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `REC.010.000` | Guest Recommendation | POST | `/api/v1/guest/recommendations` | `real` | `docs/api/recommendation.md` | 비회원 개인 추천 실행. 저장 이력 없이 후보만 반환 |
| `REC.020.000` | Personal Recommendation | GET | `/api/v1/personal/recommendations` | `real` | `docs/api/recommendation.md` | 내 개인 추천 이력 목록 조회 |
| `REC.030.000` | Personal Recommendation | POST | `/api/v1/personal/recommendations` | `real` | `docs/api/recommendation.md` | 열린 개인 추천이 없을 때 개인 추천 실행 요청 |
| `REC.040.000` | Personal Recommendation | POST | `/api/v1/personal/recommendations/{requestId}/reroll` | `real` | `docs/api/recommendation.md` | 이전 개인 추천이 아직 닫히지 않았으면 종료하고 새 개인 추천 실행 |
| `REC.050.000` | Personal Recommendation | GET | `/api/v1/personal/recommendations/{requestId}` | `real` | `docs/api/recommendation.md` | 개인 추천 요청 상세 |
| `REC.060.000` | Personal Recommendation | GET | `/api/v1/personal/recommendations/{requestId}/candidates` | `real` | `docs/api/recommendation.md` | 개인 추천 후보 목록 |
| `REC.070.000` | Personal Recommendation | PATCH | `/api/v1/personal/recommendations/{requestId}` | `real` | `docs/api/recommendation.md` | 닫히지 않은 개인 추천 선택 반영, `SELECTED` 종료, CHOOSE 로그 저장 |

## GROUP. 그룹 생성/참여 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `GROUP.010.000` | Group | POST | `/api/v1/groups` | `real` | `docs/api/group.md` | 그룹 생성. 생성자를 `OWNER` 멤버로 함께 저장하고 고정 초대 코드 생성 |
| `GROUP.020.000` | Group | GET | `/api/v1/groups` | `real` | `docs/api/group.md` | 내 활성 멤버십 기준 그룹 목록. 최신 추천 상태 포함 |
| `GROUP.030.000` | Group | GET | `/api/v1/groups/{groupId}` | `real` | `docs/api/group.md` | 그룹 상세. 활성 멤버에게 고정 초대 코드와 진행 중 추천 세션 노출 |
| `GROUP.040.000` | Group | PATCH | `/api/v1/groups/{groupId}` | `real` | `docs/api/group.md` | OWNER 전용 그룹 이름/위치 수정 |
| `GROUP.050.000` | Group Invite | POST | `/api/v1/groups/invites/nickname` | `real` | `docs/api/group.md` | OWNER 전용 nickname 기반 초대 생성 |
| `GROUP.060.000` | Group Invite | GET | `/api/v1/groups/invites/me` | `real` | `docs/api/group.md` | 내가 받은 그룹 초대 목록 |
| `GROUP.070.000` | Group Invite | POST | `/api/v1/groups/invites/{inviteId}/response` | `real` | `docs/api/group.md` | 내가 받은 그룹 초대 수락/거절 |
| `GROUP.080.000` | Group | POST | `/api/v1/groups/join` | `real` | `docs/api/group.md` | 기존 초대 코드 기반 참여. 신규 코드 입장 API 전환은 보류 |
| `GROUP.090.000` | Group | POST | `/api/v1/groups/{groupId}/leave` | `real` | `docs/api/group.md` | 일반 멤버 탈퇴. OWNER 탈퇴 거절 |
| `GROUP.100.000` | Group | DELETE | `/api/v1/groups/{groupId}` | `real` | `docs/api/group.md` | OWNER 전용 soft delete. 활성 초대 revoke |

## GREC. 그룹 추천/투표 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `GREC.010.000` | Group Recommendation | POST | `/api/v1/groups/{groupId}/recommendations` | `real` | `docs/api/group.md` | OWNER 전용 그룹 추천 준비 세션 시작 |
| `GREC.020.000` | Group Recommendation | GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}/readiness` | `real` | `docs/api/group.md` | 그룹 추천 준비 단계의 멤버별 준비 상태 조회 |
| `GREC.030.000` | Group Recommendation | POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/ready` | `real` | `docs/api/group.md` | 현재 회원의 그룹 추천 준비 완료. 전원 준비 시 후보 생성 |
| `GREC.040.000` | Group Recommendation | GET | `/api/v1/groups/{groupId}/recommendations` | `real` | `docs/api/group.md` | 그룹 추천 요청 리스트 조회 |
| `GREC.050.000` | Group Recommendation | GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}` | `real` | `docs/api/group.md` | 추천 세션 상세. PREPARING이면 readiness, OPEN이면 후보별 투표 수와 투표 진행률 |
| `GREC.060.000` | Group Recommendation | GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}/candidates` | `real` | `docs/api/group.md` | OPEN 추천 후보 목록과 후보별 투표 수. PREPARING이면 409 |
| `GREC.070.000` | Group Recommendation | POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/reroll` | `deprecated` | `docs/api/group.md` | MVP 8단계 클라이언트 계약에서 제외. 호출 시 410, 기존 구현은 MVP 이후 재도입 검토용으로 보존 |
| `GREC.080.000` | Group Vote | POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/votes` | `real` | `docs/api/group.md` | 후보 1개 선택 투표. 중복 투표 거절 |
| `GREC.090.000` | Group Recommendation | PATCH | `/api/v1/groups/{groupId}/recommendations/{sessionId}/finalize` | `real` | `docs/api/group.md` | OWNER 전용 최종 메뉴 확정. 동률 시 rank 우선 |

## RT. 실시간 이벤트 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `RT.010.000` | Realtime | GET | `/api/v1/realtime/events` | `real` | `docs/api/realtime.md` | 내 개인 SSE 이벤트 스트림. 그룹 초대와 그룹장 전용 알림 수신 |
| `RT.020.000` | Realtime | GET | `/api/v1/groups/{groupId}/realtime/events` | `real` | `docs/api/realtime.md` | 그룹 상세/추천 화면용 SSE 이벤트 스트림 |

## ADMIN. 관리자 데이터 운영 플로우

| API ID | Domain | Method | Path | 상태 | 기준 문서 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| `ADMIN.010.000` | Menu Admin | GET | `/api/v1/admin/attribute-categories` | `real` | `docs/api/menu-reference.md` | 관리자 attribute category 목록 |
| `ADMIN.020.000` | Menu Admin | POST | `/api/v1/admin/attribute-categories` | `real` | `docs/api/menu-reference.md` | 관리자 attribute category 생성 |
| `ADMIN.030.000` | Menu Admin | PATCH | `/api/v1/admin/attribute-categories/{attributeCategoryId}` | `real` | `docs/api/menu-reference.md` | 관리자 attribute category 수정 |
| `ADMIN.040.000` | Menu Admin | DELETE | `/api/v1/admin/attribute-categories/{attributeCategoryId}` | `real` | `docs/api/menu-reference.md` | 관리자 attribute category 비활성화 |
| `ADMIN.050.000` | Menu Admin | GET | `/api/v1/admin/ingredients` | `real` | `docs/api/menu-reference.md` | 관리자 ingredient 목록 |
| `ADMIN.060.000` | Menu Admin | POST | `/api/v1/admin/ingredients` | `real` | `docs/api/menu-reference.md` | 관리자 ingredient 생성 |
| `ADMIN.070.000` | Menu Admin | PATCH | `/api/v1/admin/ingredients/{ingredientId}` | `real` | `docs/api/menu-reference.md` | 관리자 ingredient 수정 |
| `ADMIN.080.000` | Menu Admin | DELETE | `/api/v1/admin/ingredients/{ingredientId}` | `real` | `docs/api/menu-reference.md` | 관리자 ingredient 비활성화 |
| `ADMIN.090.000` | Menu Admin | GET | `/api/v1/admin/menu-items` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 목록 |
| `ADMIN.100.000` | Menu Admin | PATCH | `/api/v1/admin/menu-items/{menuItemId}` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 수정 |
| `ADMIN.110.000` | Menu Admin | DELETE | `/api/v1/admin/menu-items/{menuItemId}` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 비활성화 |
| `ADMIN.120.000` | Menu Image Admin | POST | `/api/v1/admin/menu-items/{menuItemId}/images` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 대표 이미지 업로드 |
| `ADMIN.130.000` | Menu Image Admin | DELETE | `/api/v1/admin/menu-items/{menuItemId}/images/primary` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 대표 이미지 삭제 |
| `ADMIN.135.000` | Menu Admin | GET | `/api/v1/admin/menu-items/{menuItemId}` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 상세 |
| `ADMIN.140.000` | Menu Admin | POST | `/api/v1/admin/menu-items` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 생성 |
| `ADMIN.150.000` | Menu Admin | PATCH | `/api/v1/admin/menu-items/{menuItemId}/references` | `real` | `docs/api/menu-catalog.md` | 관리자 메뉴 속성/재료 연결 수정 |

## 다음 정리 대상

- Swagger UI에는 `OpenApiConfig` customizer로 API ID summary prefix, `x-api-id`, 플로우 tag를 노출합니다.
- Swagger UI에는 `OpenApiConfig` customizer로 API ID summary prefix, `x-api-id`, 플로우 tag를 노출합니다.
- 그룹 추천 요청 리스트 조회 API를 실제 service/domain 로직으로 전환했습니다.
- 그룹 추천 시작 API는 `PREPARING` 준비 세션 생성으로 전환했습니다. 준비 완료 API와 준비 상태 조회 API는 실제 구현되었습니다.
- 그룹 상세/추천 상세/내 그룹 목록은 `PREPARING` 추천 세션을 조회 응답에서 표현합니다.
- 지금까지의 그룹 추천 기능 추가 구현은 MVP 7단계로 정의합니다.
- 그룹 추천 재요청 API는 MVP 8단계 클라이언트 계약에서 제외하고 `deprecated`로 남깁니다.
- 그룹 추천 진행 중 세션은 24시간 뒤 만료되며, 별도 주기 스케줄러 없이 조회/생성/상태 변경 API 접근 시점에 `EXPIRED` 상태로 lazy expire 처리합니다.
- 준비 세션 취소 API는 MVP 8단계에서 보류했으며, 필요 시 별도 계획으로 분리합니다.
- 그룹 상세/추천 상세/후보 응답의 추가 경량화는 MVP 8단계에서 수행하지 않습니다.
- 그룹 추천 MVP 흐름 이후 정책 고도화 대상은 별도 실행 계획으로 분리합니다.
- 비회원 추천 후보 선택, 비회원 추천 이력 저장, guest session 추적이 필요해지면 별도 API 계약으로 분리합니다.
