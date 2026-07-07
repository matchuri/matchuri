# 그룹 의사결정 API

이 문서는 그룹 점심 메뉴 의사결정 API의 현재 계약 요약입니다.
상세 schema, request/response 예시, error example은 `GroupApi.java`의 OpenAPI metadata와 `/docs/openapi` 산출물을 기준으로 봅니다.

## 범위

- 그룹 생성, 목록/상세 조회, 정보 수정, 탈퇴, 삭제
- nickname 기반 그룹 초대 생성과 초대 수락/거절
- 기존 초대 코드 기반 그룹 참여
- 그룹 추천 준비 세션 시작, 준비 완료, 준비 상태 조회
- 그룹 추천 목록/상세/후보 조회
- 후보 투표와 최종 메뉴 확정
- MVP 이후 재도입 검토용 deprecated reroll endpoint

## 상태 기준

- 그룹 관리 API는 실제 service/domain 로직과 연결된 `real` 상태입니다.
- 그룹 추천 준비, 후보 생성, 투표, 최종 확정 API는 실제 service/domain 로직과 연결된 `real` 상태입니다.
- 그룹 추천 reroll endpoint는 MVP 8단계 클라이언트 계약에서 제외되어 `deprecated` 상태입니다.
- API 상태표의 전체 행은 `docs/api/api-status.md`를 기준으로 봅니다.

## API 목록

| Method | Path | 상태 | 설명 |
| --- | --- | --- | --- |
| POST | `/api/v1/groups` | `real` | 그룹 생성 |
| GET | `/api/v1/groups` | `real` | 내 그룹 목록 조회 |
| GET | `/api/v1/groups/{groupId}` | `real` | 그룹 상세 조회 |
| PATCH | `/api/v1/groups/{groupId}` | `real` | OWNER 전용 그룹 이름/위치 수정 |
| POST | `/api/v1/groups/invites/nickname` | `real` | OWNER 전용 nickname 기반 초대 생성 |
| GET | `/api/v1/groups/invites/me` | `real` | 내가 받은 그룹 초대 목록 조회 |
| POST | `/api/v1/groups/invites/{inviteId}/response` | `real` | 내가 받은 그룹 초대 수락/거절 |
| POST | `/api/v1/groups/join` | `real` | 기존 초대 코드 기반 참여 |
| POST | `/api/v1/groups/{groupId}/leave` | `real` | 일반 멤버 탈퇴 |
| DELETE | `/api/v1/groups/{groupId}` | `real` | OWNER 전용 soft delete |
| POST | `/api/v1/groups/{groupId}/recommendations` | `real` | 그룹 추천 준비 세션 시작 |
| GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}/readiness` | `real` | 그룹 추천 준비 상태 조회 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/ready` | `real` | 현재 회원의 그룹 추천 준비 완료 |
| GET | `/api/v1/groups/{groupId}/recommendations` | `real` | 그룹 추천 요청 목록 조회 |
| GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}` | `real` | 그룹 추천 상세 조회 |
| GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}/candidates` | `real` | 그룹 추천 후보 목록 조회 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/reroll` | `deprecated` | MVP 8단계 클라이언트 계약 제외, 호출 시 410 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/votes` | `real` | 후보 1개 선택 투표 |
| PATCH | `/api/v1/groups/{groupId}/recommendations/{sessionId}/finalize` | `real` | OWNER 전용 최종 메뉴 확정 |

## 핵심 계약

- 그룹 생성자는 `OWNER` 멤버로 함께 저장합니다.
- 그룹마다 하나의 고정 초대 코드를 유지합니다.
- 그룹 상세는 현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 조회할 수 있습니다.
- 그룹 상세의 member 목록은 활성 멤버만 포함합니다.
- 그룹 수정과 삭제는 `OWNER` 역할의 활성 멤버만 수행할 수 있습니다.
- 일반 멤버 탈퇴는 허용하고, `OWNER` 탈퇴는 그룹 삭제 API로 분리합니다.
- 삭제된 그룹은 목록과 상세에서 노출하지 않습니다.

## 그룹 추천 계약

- 그룹 추천 시작은 `PREPARING` 세션을 생성합니다.
- 추천 시작 직후에는 후보를 생성하지 않으며 `candidates`는 빈 배열입니다.
- 모든 현재 `ACTIVE` 그룹 멤버가 준비 완료하면 서버가 후보를 생성하고 세션을 `OPEN`으로 전환합니다.
- 준비 진행률의 분모는 현재 `ACTIVE` 그룹 멤버입니다.
- `PREPARING` 또는 `OPEN` 세션은 `startedAt + 24h` 이후 만료됩니다.
- 만료 처리는 별도 scheduler 없이 생성/조회/상태 변경 API 접근 시점에 lazy expire로 수행합니다.
- 후보 조회 API는 `OPEN` 세션에서만 후보 목록을 반환합니다. `PREPARING`이면 `409 GROUP_RECOMMENDATION_NOT_OPEN`으로 거절합니다.
- 투표는 추천 세션당 회원 1표만 허용합니다.
- 최종 확정은 `OWNER`만 수행합니다.
- 최종 확정에서 동률이면 `rankNo`가 가장 낮은 후보를 선택합니다.
- 투표가 0건이면 `rankNo=1` 후보를 선택합니다.

## 상태와 error code

대표 상태:

- `PREPARING`
- `OPEN`
- `FINALIZED`
- `EXPIRED`
- `REROLLED_WITH_SKIP`
- `REROLLED_WITHOUT_SKIP`

대표 error code:

- `GROUP_NOT_FOUND`
- `GROUP_ACCESS_DENIED`
- `GROUP_UPDATE_FORBIDDEN`
- `GROUP_RECOMMENDATION_ACTIVE_EXISTS`
- `GROUP_RECOMMENDATION_NOT_OPEN`
- `GROUP_RECOMMENDATION_ALREADY_VOTED`
- `GROUP_RECOMMENDATION_REROLL_DISABLED`
- `GROUP_RECOMMENDATION_NO_CANDIDATES`

정확한 error envelope와 example은 OpenAPI metadata를 기준으로 봅니다.

## 관련 데이터

최신 저장 모델은 아래 테이블을 사용합니다.

- `group_rooms`
- `group_room_members`
- `group_locations`
- `group_invites`
- `group_recommendations`
- `group_recommendation_readiness`
- `group_recommendation_candidates`
- `group_recommendation_votes`
- `group_menu_actions`
- `group_presence_events`

데이터 상세는 `docs/data/group-rooms-schema.md`와 `docs/data/group-recommendations-schema.md`를 봅니다.

## Harness 후보

아래 항목은 prose보다 harness로 검증하는 방향을 우선합니다.

- `docs/api/api-status.md`의 GROUP/GREC row와 backend Controller mapping drift
- `GroupApi.java` operation의 API ID, method, path, status metadata 누락
- group recommendation 상태 enum과 문서의 대표 상태 목록 drift
- group error code enum과 문서의 대표 error code 목록 drift
- `PREPARING`/`OPEN`/`EXPIRED` 상태 전이 테스트 존재 여부
- deprecated reroll endpoint가 410과 `GROUP_RECOMMENDATION_REROLL_DISABLED`를 유지하는지 여부
