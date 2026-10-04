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
- 실제 서비스 프론트는 `event-source-polyfill`의 `EventSourcePolyfill`로 `Authorization` header를 설정합니다. `/realtime-lab` 테스트 화면만 별도 `fetch` stream client를 사용합니다.

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
- 전송 시 활성 계정인지 다시 확인하고, 비활성 계정의 개인 연결은 종료합니다.
- 초대 이벤트는 지정 대상에게만 보내고 현재도 만료되지 않은 `PENDING` 초대인지 확인합니다.
- 투표 완료는 이벤트 생성 당시 대상이 현재도 활성 OWNER일 때만 보냅니다. OWNER가 변경되면 새 OWNER로 재전송하지 않습니다.

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
- 일반 그룹 이벤트는 전송 시 활성 계정·활성 멤버십·삭제되지 않은 그룹을 다시 확인합니다. 자격을 잃은 연결은 종료합니다.
- `GROUP_DELETED`는 삭제 직전 대상 목록 중 현재 활성 계정에 동일한 payload를 전송한 뒤 그룹의 모든 연결을 종료합니다.

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
| `GROUP_MEMBER_JOINED` | group | 닉네임 초대 수락 또는 UUID 링크 참여(유지 중인 고정 코드 API도 발행) | `groupId`, `memberId`, `memberNickname`, `joinedAt` |
| `GROUP_MEMBER_LEFT` | group | 멤버 탈퇴 | `groupId`, `memberId`, `memberNickname`, `leftAt` |
| `GROUP_DELETED` | group | OWNER 그룹 삭제 | `groupId`, `deletedByMemberId`, `deletedAt` |
| `GROUP_RECOMMENDATION_STARTED` | group | 그룹 추천 준비 세션 시작 | `sessionId`, `status`, `readinessProgress` |
| `GROUP_RECOMMENDATION_READINESS_UPDATED` | group | 멤버 준비 완료 | `sessionId`, `readyMemberId`, `readinessProgress` |
| `GROUP_RECOMMENDATION_OPENED` | group | 전원 준비 완료 후 후보 생성 | `sessionId`, `status`, `candidates`, `voteProgress` |
| `GROUP_RECOMMENDATION_VOTE_UPDATED` | group | 투표 저장 | `sessionId`, `voteProgress` |
| `GROUP_RECOMMENDATION_VOTE_COMPLETED` | personal | 전원 투표 완료 | `sessionId`, `voteProgress`, `finalizeRequired` |
| `GROUP_RECOMMENDATION_FINALIZED` | group | OWNER 최종 확정 | `sessionId`, `status`, `finalCandidate`, `finalizedAt` |

## Frontend 처리 기준

- 개인 stream은 로그인과 온보딩이 완료되면 app 공통 영역의 `MyRealtimeEventsInitializer`에서 연결합니다. 연결 완료와 `GROUP_INVITE_CREATED` 수신 시 초대 목록과 존재 여부를 REST로 재조회합니다.
- 그룹 stream은 그룹 상세·준비·투표 화면에서 연결하고, 해당 hook 해제 시 닫습니다. 이벤트 반영은 각 화면이 등록한 callback에 따라 다릅니다.
- `GROUP_MEMBER_JOINED`, `GROUP_MEMBER_LEFT` 수신 시 그룹 상세 화면은 그룹 목록/상세를, 준비·투표 화면은 그룹 상세와 해당 추천 상태를 재조회합니다.
- `GROUP_DELETED` 수신 후 `/group`으로 이동하는 callback은 현재 그룹 상세 화면에 연결되어 있습니다.
- `GROUP_RECOMMENDATION_VOTE_UPDATED` payload는 진행률만 제공합니다. 투표 화면은 진행률 반영 후 세션 상세와 그룹 상세를 REST로 재조회해 멤버별 투표 상태 등을 갱신합니다.
- `GROUP_RECOMMENDATION_VOTE_COMPLETED`는 개인 hook에서 수신·기록하지만, 공통 initializer에는 화면 처리 callback이 연결되어 있지 않습니다. 투표 화면은 그룹 이벤트와 세션 조회 결과를 사용합니다.
- `GROUP_RECOMMENDATION_FINALIZED`는 투표 화면의 세션을 최종 결과 상태로 바꾸고 그룹 상세를 재조회합니다.

### 연결 종료와 복구

- 그룹 stream은 `onerror`에서 오류를 기록하고 `close()`합니다. 해당 연결의 자동 재시도는 중단되며, 화면 재진입·새로고침 또는 hook 의존성 변경으로 effect가 다시 실행될 때 새 연결을 만듭니다.
- 개인 stream은 `onerror`에서 오류만 기록합니다. 네트워크 단절 등의 복구는 polyfill의 재연결 동작에 맡깁니다. 모든 오류에 재연결이 보장되는 것은 아닙니다.
- access token 변경 시 서비스 hook은 기존 연결을 닫고 새 token으로 연결합니다. SSE 자체의 401 token 갱신·재시도 정책은 없으며, REST client의 갱신 처리도 직접 사용하지 않습니다.
- 그룹 stream의 `REALTIME_CONNECTED`는 연결 로그만 남깁니다. 재연결 직후 그룹/추천 상태를 일괄 보정 조회하는 처리는 없습니다.
- 서버는 오프라인 이벤트를 저장하거나 재전송하지 않습니다. 연결이 끊긴 동안의 변경은 REST 조회가 다시 실행되는 시점에 반영됩니다.

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
- `OpenApiConfig.API_OPERATION_METADATA`의 RT entry와 backend Controller mapping drift
- SSE endpoint의 `Produces=text/event-stream` metadata 누락
- event envelope 필수 field와 frontend SSE client type drift
- `GROUP_RECOMMENDATION_*` event trigger와 group recommendation API 성공 path 테스트 연결
