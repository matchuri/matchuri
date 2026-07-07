# 실시간 이벤트 API

이 문서는 Matchuri 1차 실시간 이벤트 API의 현재 계약 요약입니다.
상세 schema, request/response 예시, error example은 Realtime 관련 `*Api.java`의 OpenAPI metadata와 `/docs/openapi` 산출물을 기준으로 봅니다.

## 범위

- 내 개인 실시간 이벤트 스트림
- 특정 그룹 실시간 이벤트 스트림
- 그룹 초대, 멤버 참여/탈퇴, 그룹 삭제 이벤트
- 그룹 추천 준비, 후보 생성, 투표, 최종 확정 이벤트
- 프론트가 기존 조회 API를 재호출할 수 있게 해주는 event envelope와 payload 계약

## 비범위

- WebSocket/STOMP
- 클라이언트에서 서버로 보내는 realtime publish API
- Redis 기반 다중 인스턴스 broadcast
- 오프라인 이벤트 저장과 재전송
- 정확한 online presence 관리
- 모바일 push notification

## 기술 기준

- 전송 방식: SSE
- 응답 Content-Type: `text/event-stream`
- 인증: `Authorization: Bearer <accessToken>`
- 서버 구현: Spring MVC `SseEmitter`
- 이벤트 저장: 1차 구현에서는 저장하지 않음
- 재전송: 1차 구현에서는 `Last-Event-ID` 기반 재전송을 지원하지 않음
- Frontend는 `Authorization` header 설정을 위해 browser 기본 `EventSource`보다 `fetch` stream 기반 SSE client를 사용합니다.

## Endpoint

| API ID | Method | Path | 상태 | 설명 |
| --- | --- | --- | --- | --- |
| `RT.010.000` | GET | `/api/v1/realtime/events` | `real` | 로그인 회원 개인에게 도착하는 event stream |
| `RT.020.000` | GET | `/api/v1/groups/{groupId}/realtime/events` | `real` | 특정 그룹 상세/추천 화면에서 필요한 group event stream |

## 개인 stream

수신 대상:

- `REALTIME_CONNECTED`
- `GROUP_INVITE_CREATED`
- `GROUP_RECOMMENDATION_VOTE_COMPLETED`

동작 기준:

- 서버는 인증된 `memberId` 기준으로 SSE 연결을 등록합니다.
- 같은 회원이 여러 browser tab이나 device에서 연결하면 모두 이벤트를 받을 수 있습니다.
- 연결 직후 `REALTIME_CONNECTED` event를 보냅니다.
- 연결 유지를 위해 heartbeat comment를 보낼 수 있습니다.

## 그룹 stream

수신 대상:

- `REALTIME_CONNECTED`
- `GROUP_MEMBER_JOINED`
- `GROUP_MEMBER_LEFT`
- `GROUP_DELETED`
- `GROUP_RECOMMENDATION_STARTED`
- `GROUP_RECOMMENDATION_READINESS_UPDATED`
- `GROUP_RECOMMENDATION_OPENED`
- `GROUP_RECOMMENDATION_VOTE_UPDATED`
- `GROUP_RECOMMENDATION_FINALIZED`

동작 기준:

- 현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 연결할 수 있습니다.
- 비멤버, 탈퇴 멤버, 삭제된 그룹에 대한 연결은 거절합니다.
- 그룹 멤버 변동과 추천 진행 이벤트는 그룹 stream으로 보냅니다.
- 그룹장 전용 `GROUP_RECOMMENDATION_VOTE_COMPLETED`는 개인 stream으로 보냅니다.

## SSE frame

서버는 SSE 표준 frame을 사용합니다.

```text
id: <eventId>
event: <eventType>
data: <json envelope>
```

heartbeat는 SSE comment 형식으로 보낼 수 있습니다.

```text
: heartbeat
```

## Event envelope

모든 event의 `data`는 JSON 문자열이며 아래 envelope를 따릅니다.

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `eventId` | string | X | 이벤트 식별자. 재전송 보장은 없지만 log 추적용으로 사용 |
| `eventType` | string | X | 이벤트 타입 |
| `occurredAt` | datetime | X | 서버 이벤트 발생 시각 |
| `groupId` | number | O | 그룹 관련 이벤트의 그룹 ID |
| `sessionId` | number | O | 그룹 추천 관련 이벤트의 세션 ID |
| `actorMemberId` | number | O | 이벤트를 유발한 회원 ID. 선택 노출 방지를 위해 `null`일 수 있음 |
| `payload` | object | X | 이벤트 타입별 payload |

`event` 값은 `data.eventType`과 같아야 합니다.
클라이언트는 알 수 없는 `eventType`을 무시하고 연결은 유지합니다.

## Event type 요약

| Event type | Stream | Trigger | Payload 핵심 |
| --- | --- | --- | --- |
| `REALTIME_CONNECTED` | personal/group | SSE 연결 성공 | `memberId`, `groupId`, `connectedAt` |
| `GROUP_INVITE_CREATED` | personal | nickname 기반 초대 생성 | `inviteId`, `groupId`, `groupName`, `requestMemberId`, `expiresAt` |
| `GROUP_MEMBER_JOINED` | group | 초대 수락 또는 코드 참여 | `groupId`, `memberId`, `memberNickname`, `joinedAt` |
| `GROUP_MEMBER_LEFT` | group | 멤버 탈퇴 | `groupId`, `memberId`, `memberNickname`, `leftAt` |
| `GROUP_DELETED` | group | OWNER 그룹 삭제 | `groupId`, `deletedByMemberId`, `deletedAt` |
| `GROUP_RECOMMENDATION_STARTED` | group | 그룹 추천 준비 세션 시작 | `sessionId`, `status`, `readinessProgress` |
| `GROUP_RECOMMENDATION_READINESS_UPDATED` | group | 멤버 준비 완료 | `sessionId`, `readyMemberId`, `readinessProgress` |
| `GROUP_RECOMMENDATION_OPENED` | group | 전원 준비 완료 후 후보 생성 | `sessionId`, `status`, `candidates`, `voteProgress` |
| `GROUP_RECOMMENDATION_VOTE_UPDATED` | group | 투표 저장 | `sessionId`, `voteProgress` |
| `GROUP_RECOMMENDATION_VOTE_COMPLETED` | personal | 전원 투표 완료 | `sessionId`, `voteProgress`, `finalizeRequired` |
| `GROUP_RECOMMENDATION_FINALIZED` | group | OWNER 최종 확정 | `sessionId`, `status`, `finalCandidate`, `finalizedAt` |

## Frontend 처리 기준

- 개인 stream은 로그인 후 app 공통 영역에서 1개 연결하는 것을 기본값으로 둡니다.
- 그룹 stream은 그룹 상세 또는 그룹 추천 화면 진입 시 연결하고 화면 이탈 시 닫습니다.
- event를 받으면 화면에 필요한 최소 상태를 반영합니다.
- 정확한 상세가 필요하면 기존 조회 API를 다시 호출합니다.
- `GROUP_MEMBER_JOINED`, `GROUP_MEMBER_LEFT` 수신 후에는 그룹 상세와 진행 중 추천 상태를 재조회합니다.
- `GROUP_DELETED` 수신 후에는 그룹 리스트 페이지로 이동합니다.
- `GROUP_RECOMMENDATION_VOTE_UPDATED`는 진행률만 갱신합니다.
- `GROUP_RECOMMENDATION_VOTE_COMPLETED`는 그룹장 화면에 최종 확정 버튼 활성화 또는 알림을 표시합니다.
- `GROUP_RECOMMENDATION_FINALIZED`는 모든 그룹원 화면을 최종 결과 상태로 전환합니다.

## 실패 기준

SSE 연결이 열리기 전에 실패하면 일반 API와 같은 공통 error envelope를 반환합니다.

| 조건 | HTTP Status | Error Code |
| --- | ---: | --- |
| access token 없음 | 401 | `AUTH_TOKEN_MISSING` |
| access token 유효하지 않음 | 401 | `AUTH_TOKEN_INVALID` |
| 그룹 stream에서 그룹이 없거나 삭제됨 | 404 | `GROUP_NOT_FOUND` |
| 그룹 stream에서 현재 회원이 활성 멤버가 아님 | 403 | `GROUP_ACCESS_DENIED` |

연결이 열린 뒤 전송 실패가 발생하면 서버는 해당 SSE 연결을 정리합니다.
1차 구현에서는 stream 내부 error event를 별도로 표준화하지 않습니다.

## 운영 기준

- 인메모리 SSE connection registry는 단일 backend instance에서만 완전하게 동작합니다.
- 다중 instance 운영이 필요해지면 Redis pub-sub 또는 message broker 기반 fan-out을 재검토합니다.
- load balancer와 proxy는 SSE buffering을 끄거나 streaming response를 지연시키지 않도록 설정해야 합니다.
- 서버는 heartbeat를 보내 idle connection이 중간 proxy에서 끊기는 문제를 줄입니다.

## Harness 후보

아래 항목은 prose보다 harness로 검증하는 방향을 우선합니다.

- `RealtimeEventType` enum과 이 문서의 event type 목록 drift
- `docs/api/api-status.md`의 RT row와 backend Controller mapping drift
- SSE endpoint의 `Produces=text/event-stream` metadata 누락
- event envelope 필수 field와 frontend SSE client type drift
- `GROUP_RECOMMENDATION_*` event trigger와 group recommendation API 성공 path 테스트 연결
