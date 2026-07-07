# 실시간 이벤트 API

이 문서는 Matchuri의 1차 실시간 이벤트 API 계약을 정리합니다.
현재 요구사항은 기존 HTTP API로 상태를 변경한 뒤 관련 사용자에게 서버가 알려주는 단방향 푸시가 핵심이므로, 1차 구현은 SSE(Server-Sent Events)를 사용합니다.

## 범위

- 내 개인 실시간 이벤트 스트림
- 특정 그룹 실시간 이벤트 스트림
- 그룹 초대, 멤버 참여/탈퇴, 그룹 추천 준비/후보/투표/확정 이벤트
- 프론트 테스트성 기능에서 사용할 수 있는 이벤트 envelope와 payload 계약

## 비범위

- WebSocket/STOMP
- 클라이언트에서 서버로 보내는 실시간 publish API
- Redis 기반 다중 인스턴스 브로드캐스트
- 오프라인 이벤트 저장과 재전송
- 정확한 온라인 presence 관리
- 모바일 push notification

## 기술 기준

- 전송 방식: SSE
- 응답 Content-Type: `text/event-stream`
- 인증: `Authorization: Bearer <accessToken>`
- 서버 구현: Spring MVC `SseEmitter`
- 이벤트 저장: 1차 구현에서는 저장하지 않음
- 재전송: 1차 구현에서는 `Last-Event-ID` 기반 재전송을 지원하지 않음

주의:

- 브라우저 기본 `EventSource`는 `Authorization` 헤더를 직접 설정할 수 없습니다.
- 현재 Matchuri 프론트는 access token을 Bearer 헤더로 사용하므로, 1차 테스트성 FE는 `fetch` 스트림 기반 SSE 클라이언트를 사용합니다.
- refresh token 쿠키는 SSE 인증 수단으로 사용하지 않습니다.

## 엔드포인트

### 1. 내 실시간 이벤트 스트림

- API ID: `RT.010.000`
- Method: `GET`
- URL: `/api/v1/realtime/events`
- 권한: 회원
- Produces: `text/event-stream`
- 설명: 로그인 회원 개인에게 도착하는 실시간 이벤트를 수신합니다.

요청 header:

| Header | 필수 | 설명 |
| --- | --- | --- |
| `Authorization` | Y | `Bearer <accessToken>` |
| `Accept` | 권장 | `text/event-stream` |

수신 대상 이벤트:

- `REALTIME_CONNECTED`
- `GROUP_INVITE_CREATED`
- `GROUP_RECOMMENDATION_VOTE_COMPLETED`

동작 기준:

- 서버는 인증된 회원 ID 기준으로 SSE 연결을 등록합니다.
- 같은 회원이 여러 브라우저 탭이나 디바이스에서 연결하면 모두 이벤트를 받을 수 있습니다.
- 서버는 연결 직후 `REALTIME_CONNECTED` 이벤트를 보냅니다.
- 서버는 연결 유지를 위해 heartbeat comment를 주기적으로 보낼 수 있습니다.

### 2. 그룹 실시간 이벤트 스트림

- API ID: `RT.020.000`
- Method: `GET`
- URL: `/api/v1/groups/{groupId}/realtime/events`
- 권한: 회원
- Produces: `text/event-stream`
- 설명: 특정 그룹 상세/추천 화면에서 필요한 그룹 실시간 이벤트를 수신합니다.

Path variable:

| Field | Type | 필수 | 설명 |
| --- | --- | --- | --- |
| `groupId` | number | Y | 그룹 ID |

요청 header:

| Header | 필수 | 설명 |
| --- | --- | --- |
| `Authorization` | Y | `Bearer <accessToken>` |
| `Accept` | 권장 | `text/event-stream` |

수신 대상 이벤트:

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
- 그룹 멤버 변동과 추천 진행 이벤트는 그룹 실시간 이벤트 스트림으로 보냅니다.
- 그룹장 전용 이벤트인 `GROUP_RECOMMENDATION_VOTE_COMPLETED`는 내 실시간 이벤트 스트림으로 보냅니다.

## SSE 프레임 형식

서버는 아래 형식으로 이벤트를 보냅니다.

```text
id: 01HZREALTIME0001
event: GROUP_RECOMMENDATION_VOTE_UPDATED
data: {"eventId":"01HZREALTIME0001","eventType":"GROUP_RECOMMENDATION_VOTE_UPDATED","occurredAt":"2026-06-01T10:15:30","groupId":3001,"sessionId":5001,"actorMemberId":null,"payload":{"voteProgress":{"totalMemberCount":4,"votedMemberCount":3,"allVoted":false}}}

```

heartbeat는 SSE comment 형식으로 보낼 수 있습니다.

```text
: heartbeat

```

프론트 처리 기준:

- `event` 값은 `data.eventType`과 같아야 합니다.
- 클라이언트는 알 수 없는 `eventType`을 무시하고 연결은 유지합니다.
- 이벤트를 받은 뒤 상세 데이터가 필요하면 기존 조회 API를 다시 호출합니다.
- 연결이 끊기면 클라이언트가 재연결합니다. 1차 구현에서는 누락 이벤트 재전송을 보장하지 않습니다.

## 공통 이벤트 envelope

모든 이벤트의 `data`는 JSON 문자열이며 아래 envelope를 따릅니다.

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `eventId` | string | X | 이벤트 식별자. 재전송 보장은 없지만 로그 추적용으로 사용합니다. |
| `eventType` | string | X | 이벤트 타입 |
| `occurredAt` | datetime | X | 서버 이벤트 발생 시각 |
| `groupId` | number | O | 그룹 관련 이벤트의 그룹 ID |
| `sessionId` | number | O | 그룹 추천 관련 이벤트의 세션 ID |
| `actorMemberId` | number | O | 이벤트를 유발한 회원 ID. 투표 진행 이벤트에서는 선택 노출 방지를 위해 `null`일 수 있습니다. |
| `payload` | object | X | 이벤트 타입별 payload |

datetime은 ISO-8601 local datetime 문자열을 사용합니다.

## 이벤트 타입과 payload

### `REALTIME_CONNECTED`

연결 성공 확인용 이벤트입니다.

수신자:

- 연결 요청자

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `memberId` | number | X | 현재 회원 ID |
| `groupId` | number | O | 그룹 스트림이면 그룹 ID, 개인 스트림이면 `null` |
| `connectedAt` | datetime | X | 연결 등록 시각 |

예시:

```json
{
  "eventId": "01HZCONNECTED0001",
  "eventType": "REALTIME_CONNECTED",
  "occurredAt": "2026-06-01T10:00:00",
  "groupId": null,
  "sessionId": null,
  "actorMemberId": 1001,
  "payload": {
    "memberId": 1001,
    "groupId": null,
    "connectedAt": "2026-06-01T10:00:00"
  }
}
```

### `GROUP_INVITE_CREATED`

그룹장이 nickname 기반 초대를 생성했을 때 초대 대상에게 보냅니다.

트리거:

- `POST /api/v1/groups/invites/nickname` 성공

수신자:

- 초대 대상 회원

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `inviteId` | number | X | 그룹 초대 ID |
| `groupId` | number | X | 그룹 ID |
| `groupName` | string | X | 그룹 이름 |
| `requestMemberId` | number | X | 초대한 회원 ID |
| `requestMemberNickname` | string | X | 초대한 회원 닉네임 |
| `expiresAt` | datetime | X | 초대 만료 시각 |

### `GROUP_MEMBER_JOINED`

새 멤버가 그룹에 들어왔을 때 그룹 활성 멤버에게 보냅니다.

트리거:

- `POST /api/v1/groups/join` 성공
- `POST /api/v1/groups/invites/{inviteId}/response`에서 `ACCEPT` 성공

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `groupId` | number | X | 그룹 ID |
| `memberId` | number | X | 참여 회원 ID |
| `memberNickname` | string | X | 참여 회원 닉네임 |
| `joinedAt` | datetime | X | 참여 시각 |

정책:

- 클라이언트는 이 이벤트를 받으면 그룹 멤버 목록을 재조회할 수 있습니다.

### `GROUP_MEMBER_LEFT`

기존 멤버가 그룹을 나갔을 때 남아 있는 그룹 활성 멤버에게 보냅니다.

트리거:

- `POST /api/v1/groups/{groupId}/leave` 성공

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `groupId` | number | X | 그룹 ID |
| `memberId` | number | X | 탈퇴 회원 ID |
| `memberNickname` | string | X | 탈퇴 회원 닉네임 |
| `leftAt` | datetime | X | 탈퇴 시각 |

정책:

- 탈퇴로 준비/투표 분모가 바뀔 수 있더라도 서버는 이 이벤트만 보냅니다.
- 클라이언트는 이 이벤트를 받으면 기존 조회 API로 그룹 상세, readiness, vote progress를 재조회합니다.

### `GROUP_DELETED`

그룹장이 그룹을 삭제했을 때 삭제 직전 그룹 활성 멤버에게 보냅니다.

트리거:

- `DELETE /api/v1/groups/{groupId}` 성공

수신자:

- 삭제 직전 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `groupId` | number | X | 삭제된 그룹 ID |
| `deletedByMemberId` | number | X | 삭제한 회원 ID |
| `deletedAt` | datetime | X | 삭제 시각 |

정책:

- 클라이언트는 이 이벤트를 받으면 해당 그룹 화면에서 그룹 리스트 페이지로 이동합니다.
- 삭제된 그룹의 상세/추천 상태는 재조회하지 않습니다.

### `GROUP_RECOMMENDATION_STARTED`

그룹장이 추천 준비 세션을 시작했을 때 그룹 활성 멤버에게 보냅니다.

트리거:

- `POST /api/v1/groups/{groupId}/recommendations` 성공

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `sessionId` | number | X | 그룹 추천 세션 ID |
| `status` | string | X | `PREPARING` |
| `readinessProgress.totalMemberCount` | number | X | 준비 대상 활성 멤버 수 |
| `readinessProgress.readyMemberCount` | number | X | 준비 완료 멤버 수 |
| `readinessProgress.allReady` | boolean | X | 전원 준비 여부 |

### `GROUP_RECOMMENDATION_READINESS_UPDATED`

그룹원이 준비 완료를 눌렀을 때 그룹 활성 멤버에게 보냅니다.

트리거:

- `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/ready` 성공

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `sessionId` | number | X | 그룹 추천 세션 ID |
| `status` | string | X | 현재 추천 상태. 보통 `PREPARING` |
| `readyMemberId` | number | X | 준비 완료한 회원 ID |
| `readyMemberNickname` | string | X | 준비 완료한 회원 닉네임 |
| `readinessProgress.totalMemberCount` | number | X | 준비 대상 활성 멤버 수 |
| `readinessProgress.readyMemberCount` | number | X | 준비 완료 멤버 수 |
| `readinessProgress.allReady` | boolean | X | 전원 준비 여부 |

정책:

- 전원 준비가 된 마지막 ready 요청에서는 이 이벤트와 `GROUP_RECOMMENDATION_OPENED`가 함께 발행될 수 있습니다.
- 클라이언트는 `GROUP_RECOMMENDATION_OPENED`를 받으면 후보 화면으로 전환합니다.

### `GROUP_RECOMMENDATION_OPENED`

모든 그룹원이 준비 완료하여 후보가 생성되고 추천 세션이 `OPEN`으로 전환됐을 때 보냅니다.

트리거:

- 마지막 `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/ready` 성공 후 후보 생성

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `sessionId` | number | X | 그룹 추천 세션 ID |
| `status` | string | X | `OPEN` |
| `candidates` | array | X | 추천 후보 목록 |
| `voteProgress.totalMemberCount` | number | X | 투표 대상 활성 멤버 수 |
| `voteProgress.votedMemberCount` | number | X | 투표 완료 멤버 수 |
| `voteProgress.allVoted` | boolean | X | 전원 투표 여부 |

`candidates` item:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `candidateId` | number | X | 후보 ID |
| `menuId` | number | X | 메뉴 ID |
| `menuName` | string | X | 메뉴 이름 |
| `rankNo` | number | X | 추천 순위 |

정책:

- MVP에서는 후보 3개 안팎을 보냅니다.
- 후보별 투표 수는 이 이벤트에 포함하지 않습니다.

### `GROUP_RECOMMENDATION_VOTE_UPDATED`

투표 진행률이 바뀌었을 때 그룹 활성 멤버에게 보냅니다.

트리거:

- `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/votes` 성공

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `sessionId` | number | X | 그룹 추천 세션 ID |
| `voteProgress.totalMemberCount` | number | X | 투표 대상 활성 멤버 수 |
| `voteProgress.votedMemberCount` | number | X | 투표 완료 멤버 수 |
| `voteProgress.allVoted` | boolean | X | 전원 투표 여부 |

정책:

- 후보별 투표 수를 포함하지 않습니다.
- 어떤 후보에 투표했는지도 포함하지 않습니다.
- 투표자가 누구인지 화면에 노출하지 않도록 `actorMemberId`는 `null`로 둘 수 있습니다.

### `GROUP_RECOMMENDATION_VOTE_COMPLETED`

모든 현재 활성 그룹원이 투표를 완료했을 때 그룹장에게 보냅니다.

트리거:

- `POST /api/v1/groups/{groupId}/recommendations/{sessionId}/votes` 성공 후 `votedMemberCount == totalMemberCount`

수신자:

- 그룹 OWNER

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `sessionId` | number | X | 그룹 추천 세션 ID |
| `voteProgress.totalMemberCount` | number | X | 투표 대상 활성 멤버 수 |
| `voteProgress.votedMemberCount` | number | X | 투표 완료 멤버 수 |
| `voteProgress.allVoted` | boolean | X | 항상 `true` |
| `finalizeRequired` | boolean | X | 항상 `true` |

정책:

- 서버가 자동으로 최종 후보를 확정하지 않습니다.
- 그룹장은 기존 `PATCH /api/v1/groups/{groupId}/recommendations/{sessionId}/finalize` API로 수동 확정합니다.

### `GROUP_RECOMMENDATION_FINALIZED`

그룹장이 최종 후보를 확정했을 때 그룹 활성 멤버에게 보냅니다.

트리거:

- `PATCH /api/v1/groups/{groupId}/recommendations/{sessionId}/finalize` 성공

수신자:

- 그룹 활성 멤버 전체

payload:

| Field | Type | Nullable | 설명 |
| --- | --- | --- | --- |
| `sessionId` | number | X | 그룹 추천 세션 ID |
| `status` | string | X | `FINALIZED` |
| `finalizedAt` | datetime | X | 최종 확정 시각 |
| `finalCandidate.candidateId` | number | X | 최종 후보 ID |
| `finalCandidate.menuId` | number | X | 최종 메뉴 ID |
| `finalCandidate.menuName` | string | X | 최종 메뉴 이름 |
| `finalCandidate.rankNo` | number | X | 추천 순위 |

## 실패 응답

SSE 연결이 열리기 전에 실패하면 일반 API와 같은 공통 error envelope를 반환합니다.

인증 실패 예시:

```json
{
  "success": false,
  "data": null,
  "error": {
    "status": 401,
    "code": "AUTH_TOKEN_MISSING",
    "message": "인증 토큰이 필요합니다.",
    "details": []
  }
}
```

대표 실패 기준:

| 조건 | HTTP Status | Error Code |
| --- | --- | --- |
| access token 없음 | 401 | `AUTH_TOKEN_MISSING` |
| access token 유효하지 않음 | 401 | `AUTH_TOKEN_INVALID` |
| 그룹 스트림에서 그룹이 없거나 삭제됨 | 404 | `GROUP_NOT_FOUND` |
| 그룹 스트림에서 현재 회원이 활성 멤버가 아님 | 403 | `GROUP_ACCESS_DENIED` |

연결이 열린 뒤 전송 실패가 발생하면 서버는 해당 SSE 연결을 정리합니다.
1차 구현에서는 스트림 내부 error event를 별도로 표준화하지 않습니다.

## 프론트 연동 기준

- 개인 스트림은 로그인 후 앱 공통 영역에서 1개 연결하는 것을 기본값으로 둡니다.
- 그룹 스트림은 그룹 상세 또는 그룹 추천 화면 진입 시 연결하고 화면 이탈 시 닫습니다.
- 이벤트를 받으면 화면에 필요한 최소 상태를 즉시 반영하되, 정확한 상세가 필요하면 기존 조회 API를 호출합니다.
- `GROUP_MEMBER_JOINED`, `GROUP_MEMBER_LEFT` 수신 후에는 그룹 상세와 진행 중 추천 상태를 재조회합니다.
- `GROUP_DELETED` 수신 후에는 그룹 리스트 페이지로 이동합니다.
- `GROUP_RECOMMENDATION_VOTE_UPDATED`는 진행률만 갱신합니다.
- `GROUP_RECOMMENDATION_VOTE_COMPLETED`는 그룹장 화면에 최종 확정 버튼 활성화 또는 알림을 표시합니다.
- `GROUP_RECOMMENDATION_FINALIZED`는 모든 그룹원 화면을 최종 결과 상태로 전환합니다.

## 운영 메모

- 인메모리 SSE 연결 registry는 단일 백엔드 인스턴스에서만 완전하게 동작합니다.
- 다중 인스턴스 운영이 필요해지면 Redis pub-sub 또는 메시지 브로커 기반 fan-out을 재검토합니다.
- 로드밸런서와 프록시는 SSE buffering을 끄거나 스트리밍 응답을 지연시키지 않도록 설정해야 합니다.
- 서버는 heartbeat를 보내 유휴 연결이 중간 프록시에서 끊기는 문제를 줄입니다.
