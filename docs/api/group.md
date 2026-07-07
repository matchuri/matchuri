# 그룹 의사결정 API

이 문서는 그룹 점심 메뉴 의사결정 API의 현재 계약과 구현 상태를 정리합니다.
상세 schema와 예시는 Swagger UI와 `GroupApi.java`의 OpenAPI 메타데이터를 함께 봅니다.

## 현재 범위

- 그룹 생성
- 내 그룹 목록/상세 조회
- 그룹 정보 수정
- nickname 기반 그룹 초대 생성
- 내 그룹 초대 목록 조회
- 그룹 초대 수락/거절
- 초대 코드 기반 참여
- 그룹 탈퇴
- 그룹 삭제
- 그룹 추천 시작
- 그룹 추천 준비 완료
- 그룹 추천 준비 상태 조회
- 그룹 추천 요청 리스트 조회
- 그룹 추천 상세/후보 조회
- 후보 투표
- 최종 메뉴 확정

## 현재 상태

그룹 관리 API는 MVP 6단계에서 실제 service/domain 로직으로 전환했습니다.
그룹 추천 시작, 그룹 추천 상세/후보 조회, 그룹 추천 재요청, 투표, 최종 확정, 준비 완료 흐름은 MVP 7단계 "그룹 추천 기능 추가 구현" 범위로 실제 service/domain 로직 전환을 진행했습니다.
회의 이후 변경/확정 요구사항에 맞춘 수정 중심 작업은 MVP 8단계 "그룹 추천 변경 요구사항 반영 리팩토링" 범위에서 관리합니다.
MVP 8단계부터 그룹 추천 재요청은 클라이언트 연동 범위에서 제외합니다. 기존 엔드포인트와 도메인 구현은 MVP 이후 재도입 검토를 위해 deprecated 상태로 보존합니다.
MVP 8단계부터 그룹 추천 재요청은 클라이언트 연동 범위에서 제외합니다. 기존 엔드포인트와 도메인 구현은 MVP 이후 재도입 검토를 위해 deprecated 상태로 보존합니다.

MVP 6단계 그룹 관리 구현 이력과 검증 기준은 내부 실행 계획 기록에서 관리합니다.

API 경로에서는 사용자 흐름을 표현하기 위해 `recommendations`를 사용하며, 최신 저장 모델은 아래 테이블을 기준으로 합니다.

- `group_rooms`
- `group_room_members`
- `group_invites`
- `group_recommendations`
- `group_recommendation_readiness`
- `group_recommendation_candidates`
- `group_recommendation_votes`
- `group_menu_actions`
- `group_presence_events`

## API 목록

| Method | Path | 상태 | 설명 |
| --- | --- | --- | --- |
| POST | `/api/v1/groups` | `real` | 그룹 생성 |
| GET | `/api/v1/groups` | `real` | 내 그룹 목록 조회 |
| GET | `/api/v1/groups/{groupId}` | `real` | 그룹 상세 조회 |
| PATCH | `/api/v1/groups/{groupId}` | `real` | 그룹 정보 수정. MVP에서는 이름과 위치 수정 |
| POST | `/api/v1/groups/invites/nickname` | `real` | nickname 기반 그룹 초대 생성 |
| GET | `/api/v1/groups/invites/me` | `real` | 내가 받은 그룹 초대 목록 조회 |
| POST | `/api/v1/groups/invites/{inviteId}/response` | `real` | 내가 받은 그룹 초대 수락/거절 |
| POST | `/api/v1/groups/join` | `real` | 기존 초대 코드 기반 참여. 신규 코드 입장 API 전환은 보류 |
| POST | `/api/v1/groups/{groupId}/leave` | `real` | 그룹 탈퇴 |
| DELETE | `/api/v1/groups/{groupId}` | `real` | 그룹 삭제 |
| POST | `/api/v1/groups/{groupId}/recommendations` | `real` | 그룹 추천 준비 세션 시작 |
| GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}/readiness` | `real` | 그룹 추천 준비 상태 조회 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/ready` | `real` | 현재 회원의 그룹 추천 준비 완료 |
| GET | `/api/v1/groups/{groupId}/recommendations` | `real` | 그룹 추천 요청 리스트 조회 |
| GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}` | `real` | 그룹 추천 상세 조회 |
| GET | `/api/v1/groups/{groupId}/recommendations/{sessionId}/candidates` | `real` | 그룹 추천 후보 목록 조회 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/reroll` | `deprecated` | 그룹 추천 재요청. MVP 8단계 클라이언트 계약 제외, 호출 시 410 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/reroll` | `deprecated` | 그룹 추천 재요청. MVP 8단계 클라이언트 계약 제외, 호출 시 410 |
| POST | `/api/v1/groups/{groupId}/recommendations/{sessionId}/votes` | `real` | 후보 투표 |
| PATCH | `/api/v1/groups/{groupId}/recommendations/{sessionId}/finalize` | `real` | 최종 메뉴 확정 |

## 페이지네이션 기준

내 그룹 목록 조회는 공통 `PageResponse` 구조를 사용합니다.
현재 로그인 회원이 `ACTIVE` 멤버로 속한 그룹만 반환하며, `DELETED` 그룹은 목록에서 제외합니다.
현재 `latestRecommendationStatus`는 목록 조회 응답 계약에 남아 있지만, MVP 그룹 추천 구현에서는 아직 값을 채우지 않아 `null`일 수 있습니다.

| Query parameter | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `status` | N | 없음 | 그룹 상태 필터입니다. `DELETED`는 목록 노출 대상에서 제외됩니다. |
| `page` | N | `0` | 0부터 시작하는 페이지 번호입니다. |
| `size` | N | `20` | 페이지 크기입니다. 최대 100까지 허용합니다. |

응답의 `pageInfo`는 요청한 `page`, `size`를 반영합니다.

## 그룹 상세 기준

그룹 상세 API는 `GET /api/v1/groups/{groupId}`입니다.
현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 상세를 조회할 수 있습니다.

`members` 항목은 현재 활성 멤버만 포함하며, 각 멤버 summary는 다음 핵심 필드를 반환합니다.

| Field | 설명 |
| --- | --- |
| `memberId` | 회원 ID입니다. |
| `nickname` | 회원 닉네임입니다. |
| `role` | 그룹 내 역할입니다. |
| `status` | 그룹 멤버 상태입니다. 그룹 상세에서는 현재 활성 멤버만 반환하므로 기본적으로 `ACTIVE`입니다. |
| `joinedAt` | 그룹 참여 시각입니다. |
| `isMe` | 현재 로그인한 회원 본인이면 `true`, 아니면 `false`입니다. |

## 그룹 상세 기준

그룹 상세 API는 `GET /api/v1/groups/{groupId}`입니다.
현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 상세를 조회할 수 있습니다.

`members` 항목은 현재 활성 멤버만 포함하며, 각 멤버 summary는 다음 핵심 필드를 반환합니다.

| Field | 설명 |
| --- | --- |
| `memberId` | 회원 ID입니다. |
| `nickname` | 회원 닉네임입니다. |
| `role` | 그룹 내 역할입니다. |
| `status` | 그룹 멤버 상태입니다. 그룹 상세에서는 현재 활성 멤버만 반환하므로 기본적으로 `ACTIVE`입니다. |
| `joinedAt` | 그룹 참여 시각입니다. |
| `isMe` | 현재 로그인한 회원 본인이면 `true`, 아니면 `false`입니다. |

## 그룹 수정 기준

그룹 수정 API는 `PATCH /api/v1/groups/{groupId}`입니다.
MVP에서는 그룹 이름과 위치를 수정하며, 이후 설명, 설정 같은 수정 요소를 추가할 수 있도록 partial update object로 설계합니다.
위치는 그룹이 마지막으로 기억하는 추천 기준 위치이며, 개인 추천의 위치 기억은 클라이언트 저장소 책임으로 둡니다.
위치는 그룹이 마지막으로 기억하는 추천 기준 위치이며, 개인 추천의 위치 기억은 클라이언트 저장소 책임으로 둡니다.

요청 body:

| Field | 필수 | 설명 |
| --- | --- | --- |
| `name` | N | 변경할 그룹 이름입니다. 포함 시 blank 불가, max 100 기준을 따릅니다. |
| `latitude` | N | 변경할 그룹 추천 기준 위치의 위도입니다. 포함 시 -90 이상 90 이하 기준을 따릅니다. |
| `longitude` | N | 변경할 그룹 추천 기준 위치의 경도입니다. 포함 시 -180 이상 180 이하 기준을 따릅니다. |
| `radiusMeters` | N | 변경할 그룹 추천 기준 위치의 반경 거리(미터)입니다. 포함 시 0 이상 기준을 따릅니다. |
| `address` | N | 변경할 그룹 추천 기준 위치의 주소 문자열입니다. 포함 시 blank 불가, max 255 기준을 따릅니다. |
| `radiusMeters` | N | 변경할 그룹 추천 기준 위치의 반경 거리(미터)입니다. 포함 시 0 이상 기준을 따릅니다. |
| `address` | N | 변경할 그룹 추천 기준 위치의 주소 문자열입니다. 포함 시 blank 불가, max 255 기준을 따릅니다. |

요청 규칙:

- 생략된 필드는 변경하지 않습니다.
- 요청에는 최소 1개 이상의 지원 필드가 포함되어야 합니다.
- MVP에서는 명시적 `null`을 값 삭제 의미로 사용하지 않습니다. nullable field 삭제가 필요해지면 별도 clear flag 또는 명확한 null 처리 정책을 추가합니다.
- 현재 지원하지 않는 수정 필드는 API 계약에 포함하지 않습니다.

권한과 상태:

- 로그인한 활성 회원만 사용할 수 있습니다.
- `ACTIVE` 그룹만 수정할 수 있습니다.
- 현재 회원이 해당 그룹의 `ACTIVE` OWNER 멤버일 때만 수정할 수 있습니다.
- 삭제된 그룹은 `GROUP_NOT_FOUND`, OWNER가 아닌 활성 멤버는 `GROUP_UPDATE_FORBIDDEN`, 비멤버 또는 비활성 멤버는 `GROUP_ACCESS_DENIED` 방향으로 처리합니다.

응답 방향:

- 수정 후 `groupId`, `name`, `latitude`, `longitude`, `radiusMeters`, `address`, `status`, `updatedAt`을 반환합니다.
- 그룹 추천 재요청은 MVP 8단계 클라이언트 계약에서 제외되었으므로 수정 응답은 재요청용 추천 ID를 반환하지 않습니다.
- 수정 후 `groupId`, `name`, `latitude`, `longitude`, `radiusMeters`, `address`, `status`, `updatedAt`을 반환합니다.
- 그룹 추천 재요청은 MVP 8단계 클라이언트 계약에서 제외되었으므로 수정 응답은 재요청용 추천 ID를 반환하지 않습니다.
- 향후 수정 필드가 늘어나도 응답은 현재 그룹의 최신 핵심 상태를 반환하는 방향을 유지합니다.
- 그룹 수정 후 `PREPARING` 세션의 후보 생성은 후보 생성 시점의 최신 그룹 위치를 사용합니다.
- 그룹 수정 후 `PREPARING` 세션의 후보 생성은 후보 생성 시점의 최신 그룹 위치를 사용합니다.

## 구현 상태 기준

- `POST /api/v1/groups`는 실제 저장 모델과 연결되어 생성자를 `OWNER` 멤버로 함께 저장하고, 그룹마다 하나의 고정 초대 코드를 생성합니다.
- `GET /api/v1/groups`는 현재 회원의 활성 membership 기준으로 실제 데이터를 조회하며, 최신 그룹 추천이 있으면 `latestRecommendationStatus`에 `PREPARING`을 포함한 최신 상태를 반환합니다.
- `GET /api/v1/groups/{groupId}`는 현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 상세, 고정 초대 코드, 활성 멤버 목록, 가장 최근 그룹 추천을 조회합니다. 멤버 목록에는 현재 로그인 회원 표시용 `isMe`를 포함합니다.
- 그룹 상세의 `recentlyRecommendation`은 가장 최근 그룹 추천 세션을 반환합니다. `PREPARING`이면 readiness 진행률과 빈 후보 목록, null 투표 진행률을 반환하고, `OPEN` 또는 종료 상태이면 기존 후보/투표 진행률과 최종 후보 정보를 반환합니다.
- `PATCH /api/v1/groups/{groupId}`는 `OWNER` 역할의 활성 멤버만 호출할 수 있으며, MVP에서는 그룹 이름과 위치를 수정합니다. 그룹 추천 재요청은 MVP 8단계 클라이언트 계약에서 제외되었으므로 수정 응답은 재요청용 추천 ID를 반환하지 않습니다.
- `POST /api/v1/groups/invites/nickname`은 `OWNER` 역할의 활성 멤버만 호출할 수 있으며, 활성 회원의 nickname으로 `PENDING` 초대 요청을 생성합니다. 같은 그룹/대상에 대기 중인 초대가 있으면 409로 거절합니다.
- `GET /api/v1/groups/invites/me`는 현재 회원이 받은 초대 요청을 조회합니다. `status`를 생략하면 `PENDING` 초대만 조회합니다.
- `POST /api/v1/groups/invites/{inviteId}/response`는 현재 회원이 받은 `PENDING` 초대를 수락하거나 거절합니다. 수락 시 membership을 생성하거나 기존 `LEFT` membership을 재활성화하고, 거절 시 membership은 변경하지 않습니다. 만료된 초대는 409로 거절하며, 만료 상태 정리는 후속 lazy expire 또는 배치 정책에서 다룹니다.
- `POST /api/v1/groups/join`은 기존 초대 코드 기반 참여 API입니다. 신규 코드 입장 API 전환은 이번 nickname 초대 리모델링 범위에서 보류하며, 고정 초대 코드 발급과 그룹 상세 노출은 유지합니다.
- `POST /api/v1/groups/{groupId}/leave`는 일반 활성 멤버를 `LEFT`로 전환하며, `OWNER`는 그룹 삭제 API를 사용해야 하므로 거절합니다.
- `DELETE /api/v1/groups/{groupId}`는 `OWNER`만 호출할 수 있으며, 그룹을 `DELETED`로 전환하고 대기 중인 초대 요청을 `REVOKED`, 활성 멤버를 `LEFT`로 정리합니다.
- `POST /api/v1/groups/{groupId}/recommendations`는 `OWNER` 역할의 활성 멤버만 호출할 수 있으며, `PREPARING` 그룹 추천 준비 세션을 `group_recommendations`에 저장합니다.
- 그룹 추천 시작 요청의 정상 위치 값(`latitude`, `longitude`, `radiusMeters`, `address`)은 `group_locations`의 최신 기억 위치로만 반영합니다.
- `PREPARING` 상태의 그룹 추천은 아직 후보 생성 기준이 확정되지 않았으므로 `group_recommendations.context_json`을 `null`로 둡니다.
- 모든 현재 활성 멤버가 준비 완료해 후보를 생성하는 순간, 현재 그룹 기억 위치를 확정 `contextJson` 스냅샷으로 기록합니다.
- 그룹 추천 시작 요청의 정상 위치 값(`latitude`, `longitude`, `radiusMeters`, `address`)은 `group_locations`의 최신 기억 위치로만 반영합니다.
- `PREPARING` 상태의 그룹 추천은 아직 후보 생성 기준이 확정되지 않았으므로 `group_recommendations.context_json`을 `null`로 둡니다.
- 모든 현재 활성 멤버가 준비 완료해 후보를 생성하는 순간, 현재 그룹 기억 위치를 확정 `contextJson` 스냅샷으로 기록합니다.
- 추천 시작 직후에는 후보를 생성하지 않으므로 응답의 `candidates`는 빈 배열입니다.
- 같은 그룹에 `PREPARING` 또는 `OPEN` 추천 세션이 이미 있으면 `GROUP_RECOMMENDATION_ACTIVE_EXISTS`로 거절합니다.
- `PREPARING` 또는 `OPEN` 추천 세션은 `startedAt + 24h` 이후 만료됩니다. 별도 주기 스케줄러 없이 생성/조회/상태 변경 API 접근 시점에 `status=EXPIRED`, `endedAt=now`로 lazy expire 처리합니다.
- `GET /api/v1/groups`, 그룹 추천 목록 조회, 그룹 상세의 `recentlyRecommendation`, 추천 상세 조회는 시간상 만료된 `PREPARING`/`OPEN` 세션을 먼저 `EXPIRED`로 전환한 뒤 응답합니다.
- 준비 완료, 투표, 최종 확정 등 상태 변경 API는 시간상 만료된 추천 세션을 `EXPIRED`로 전환한 뒤 409로 거절합니다.
- `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/ready`는 현재 회원을 `READY`로 저장합니다. 같은 회원의 중복 호출은 준비 세션이 계속 `PREPARING`이면 idempotent하게 READY를 유지합니다.
- 모든 현재 `ACTIVE` 그룹 멤버가 준비 완료하면 서버가 후보를 생성하고 그룹 추천을 `OPEN`으로 전환합니다.
- 준비 완료 API의 200 응답은 아직 전원 준비 전이면 `status=PREPARING`, `candidates=[]`를 반환하고, 마지막 인원이 준비 완료한 경우 `status=OPEN`과 생성된 추천 후보를 함께 반환합니다.
- `GET /api/v1/groups/{groupId}/recommendations/{sessionId}/readiness`는 준비 진행률과 현재 활성 멤버별 `ready` 여부를 반환합니다.
- `GET /api/v1/groups/{groupId}/recommendations/{sessionId}/readiness`는 준비 진행률과 현재 활성 멤버별 `ready` 여부를 반환합니다.
- 준비 진행률의 분모는 현재 `ACTIVE` 그룹 멤버이며, `status=READY`인 현재 활성 멤버만 준비 완료로 계산합니다.
- MVP 8단계 응답에서는 멤버별 `readinessStatus`, `readinessUpdatedAt`을 노출하지 않습니다.
- MVP 8단계 응답에서는 멤버별 `readinessStatus`, `readinessUpdatedAt`을 노출하지 않습니다.
- `GET /api/v1/groups/{groupId}/recommendations`는 개인 추천 목록 조회처럼 공통 `PageResponse`를 사용하고, 해당 그룹의 `ACTIVE` 멤버에게 그룹 추천 요청 summary 목록을 최신순으로 반환합니다.
- 1차 계약에서 그룹 추천 요청 리스트 summary는 `sessionId`, `status`, `startedAt`, `endedAt`만 포함합니다. `finalCandidate`, `finalMenuName`, `voteProgress`, `status` 필터, 모든 그룹 통합 목록은 제외합니다.
- `GET /api/v1/groups/{groupId}/recommendations/{sessionId}`는 현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 추천 상태, 추천 당시 `contextJson` 문자열, readiness 진행률, 후보, 후보별 투표 수, 투표 진행률, 투표 상태, 최종 후보를 조회합니다.
- 추천 상세의 `contextJson`은 `group_recommendations.context_json`에 저장된 추천 당시 위치 등 컨텍스트 스냅샷이며, 서버가 파싱하지 않고 문자열 그대로 반환합니다.
- 추천 상세의 `memberVotes`는 현재 활성 그룹원별 투표 여부, 현재 로그인 회원 본인 여부(`isMe`), 선택 후보 ID를 반환합니다.
- `memberVotes.candidateId`는 해당 회원이 투표하지 않았으면 `null`입니다.
- 그룹 추천 상세/후보 응답에는 메뉴 대표 이미지 URL인 `thumbnailUrl`을 포함합니다. 대표 이미지가 없으면 `null`이며, 첫 구현에서는 별도 썸네일 파일 없이 원본 이미지 URL을 반환합니다.
- 그룹 추천 후보 응답의 `score`는 프론트 노출용 0~100 정규화 추천 점수입니다. 알고리즘 원점수는 API에 노출하지 않습니다.
- 추천 상세에서 `PREPARING` 세션은 후보 빈 배열, `voteProgress=null`, `memberVotes=[]`, readiness 진행률을 반환합니다. `OPEN` 세션은 readiness 없이 기존 후보/투표 정보를 반환합니다.
- `GET /api/v1/groups/{groupId}/recommendations/{sessionId}/candidates`는 현재 회원이 해당 그룹의 `ACTIVE` 멤버이고 추천이 `OPEN`일 때만 후보 목록과 후보별 투표 수를 조회합니다.
- 후보 조회 API는 후보 생성 이후의 리소스이므로 `PREPARING` 상태에서는 빈 배열이 아니라 `409 GROUP_RECOMMENDATION_NOT_OPEN`으로 거절합니다. 준비 단계 정보는 추천 상세 또는 준비 상태 조회 API를 사용합니다.
- `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/reroll`은 MVP 8단계 클라이언트 계약에서 제외된 deprecated API입니다. 호출하면 `410 Gone`과 `GROUP_RECOMMENDATION_REROLL_DISABLED`를 반환합니다. 기존 도메인 구현은 MVP 이후 재도입 검토를 위해 보존합니다.
- 보존된 재요청 구현은 `OWNER` 역할의 활성 멤버만 호출할 수 있으며, source 추천을 닫고 새 그룹 추천을 생성합니다.
- `NOT_SATISFIED` 재요청은 source 후보 전체를 `group_menu_actions.SKIP`으로 저장하고 source를 `REROLLED_WITH_SKIP`으로 종료합니다.
- `INPUT_CHANGED` 재요청은 `SKIP` 로그 없이 source를 `REROLLED_WITHOUT_SKIP`으로 종료합니다.
- 보존된 새 그룹 추천 후보 계산에서는 같은 그룹의 최근 24시간 `SKIP` 메뉴를 제외합니다.
- 보존된 새 그룹 추천 후보 계산에서는 같은 그룹의 최근 24시간 `SKIP` 메뉴를 제외합니다.
- `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/votes`는 현재 회원이 해당 그룹의 `ACTIVE` 멤버이고 추천이 `OPEN`일 때만 후보 1개 선택 투표를 저장합니다.
- 투표 API는 `voteValue`를 사용하지 않습니다.
- 투표 API는 `voteValue`를 사용하지 않습니다.
- 투표 API는 추천 세션당 회원 1표만 허용하며, 중복 투표는 `GROUP_RECOMMENDATION_ALREADY_VOTED`로 거절합니다.
- `PATCH /api/v1/groups/{groupId}/recommendations/{sessionId}/finalize`는 `OWNER` 역할의 활성 멤버만 호출할 수 있으며, 최다 득표 후보를 최종 후보로 저장하고 추천을 `FINALIZED`로 종료합니다.
- 최종 확정에서 동률이면 `rankNo`가 가장 낮은 후보를 선택하고, 투표가 0건이면 `rankNo=1` 후보를 선택합니다.
- 후보가 없는 추천은 `GROUP_RECOMMENDATION_NO_CANDIDATES`, `OPEN`이 아닌 추천은 `GROUP_RECOMMENDATION_NOT_OPEN`으로 거절합니다.

## 구현 이력 메모

그룹 관리와 그룹 추천 관련 세부 구현 이력은 내부 실행 계획 기록에서 관리합니다.
