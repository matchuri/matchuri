# SSE 프론트엔드 구현 브리핑

## 목적

현재 Matchuri의 인증 정책에서는 브라우저 기본 `EventSource`를 사용할 수 없다.
이 문서는 그 이유와 `fetch` 기반 SSE 클라이언트가 담당해야 하는 기능, 현재 구현 상태, 운영 적용 권장안을 정리한다.

상세 SSE API와 이벤트 payload 계약은 [`docs/api/realtime.md`](./realtime.md)를 기준으로 한다.

## SSE 맥락

SSE(Server-Sent Events)는 서버가 이미 연결된 HTTP 응답 스트림을 통해 클라이언트로 이벤트를 지속적으로 전송하는 방식이다.

Matchuri에서 실제 상태 변경은 기존 HTTP API가 담당한다.
SSE는 서버 상태가 변경되었음을 관련 사용자에게 알리는 신호로 사용한다.

```text
투표 요청
POST /api/v1/groups/{groupId}/recommendations/{sessionId}/votes

투표 진행률 변경 알림
GROUP_RECOMMENDATION_VOTE_UPDATED SSE 이벤트
```

프론트는 SSE 이벤트를 받으면 payload의 최소 상태를 반영하거나 기존 REST 조회 API를 다시 호출한다.

## EventSource

브라우저는 SSE 연결을 위한 `EventSource` API를 기본 제공한다.

```ts
const source = new EventSource("/api/v1/realtime/events");

source.addEventListener("GROUP_INVITE_CREATED", (event) => {
  const data = JSON.parse(event.data);
});
```

`EventSource`는 다음 기능을 기본 제공한다.

- SSE frame 파싱
- 연결 종료 감지
- 자동 재연결
- 서버가 전달한 `retry` 값 반영
- `Last-Event-ID` 전송
- named event 처리

참고 자료: [MDN - Using server-sent events](https://developer.mozilla.org/ko/docs/Web/API/Server-sent_events/Using_server-sent_events)

## EventSource를 사용하지 않는 이유

Matchuri는 access token을 `Authorization` header로 전달하여 인증한다.

```http
Authorization: Bearer {accessToken}
```

하지만 브라우저 기본 `EventSource`는 요청에 임의의 HTTP header를 추가할 수 없다.

```ts
new EventSource("/api/v1/realtime/events");
// Authorization header 설정 불가능
```

따라서 현재 인증 정책을 유지하면서 SSE를 사용하려면 `fetch` 기반 연결이 필요하다.

```ts
const response = await fetch("/api/v1/realtime/events", {
  headers: {
    Accept: "text/event-stream",
    Authorization: `Bearer ${accessToken}`,
  },
});
```

## EventSource를 사용할 수 있는 경우

- 인증을 HTTP-only cookie로 처리하는 경우
- SSE 전용 단기 연결 token을 발급하는 경우
- 인증이 필요 없는 공개 SSE인 경우

일반 access token을 query parameter로 전달하는 방식은 사용하지 않는다.
URL, 브라우저 기록, 프록시 및 접근 로그 등에 token이 노출될 위험이 있기 때문이다.

## fetch 기반 SSE가 직접 처리해야 하는 것

`fetch`는 응답 stream만 제공한다.
`EventSource`가 처리하던 SSE 관련 동작은 클라이언트가 직접 구현해야 한다.

### 연결 관리

- `Authorization` header를 포함한 연결
- 응답 status 및 `Content-Type` 검증
- 화면 이탈 및 로그아웃 시 `AbortController`로 연결 종료
- React 재렌더링으로 인한 중복 연결 방지
- access token 변경 시 기존 연결 종료 후 재연결

### Stream 처리

- `ReadableStream` chunk 읽기
- 여러 chunk에 걸쳐 잘린 SSE frame 복원
- 하나의 chunk에 포함된 여러 frame 분리
- `id`, `event`, `data`, `retry` field 파싱
- 여러 줄로 구성된 `data` 결합
- heartbeat comment와 일반 이벤트 구분
- 잘못된 JSON이나 알 수 없는 `eventType` 처리

### 재연결 정책

- 네트워크 단절 감지
- 재연결 횟수 및 exponential backoff 관리
- 정상 종료와 오류 종료 구분
- `401`, `403`, `404`, `5xx`별 처리 분리
- 필요하면 마지막 `eventId`를 `Last-Event-ID` header로 전달

## Matchuri SSE 연결

### 개인 스트림

```http
GET /api/v1/realtime/events
Authorization: Bearer {accessToken}
Accept: text/event-stream
```

로그인 후 앱 공통 영역에서 하나만 연결하는 것을 권장한다.

주요 수신 이벤트:

- `GROUP_INVITE_CREATED`
- `GROUP_RECOMMENDATION_VOTE_COMPLETED`

### 그룹 스트림

```http
GET /api/v1/groups/{groupId}/realtime/events
Authorization: Bearer {accessToken}
Accept: text/event-stream
```

그룹 상세 또는 추천 화면 진입 시 연결하고, 화면 이탈 시 종료한다.

주요 수신 이벤트:

- `GROUP_MEMBER_JOINED`
- `GROUP_MEMBER_LEFT`
- `GROUP_DELETED`
- `GROUP_RECOMMENDATION_STARTED`
- `GROUP_RECOMMENDATION_READINESS_UPDATED`
- `GROUP_RECOMMENDATION_OPENED`
- `GROUP_RECOMMENDATION_VOTE_UPDATED`
- `GROUP_RECOMMENDATION_FINALIZED`

서버는 연결 직후 `REALTIME_CONNECTED` 이벤트를 보낸다.
연결 유지를 위해 30초마다 heartbeat comment를 보내며, 연결 timeout은 30분이다.

## 이벤트 처리 원칙

SSE 이벤트는 서버 상태 변경을 알리는 신호로 처리한다.

```ts
switch (event.eventType) {
  case "GROUP_MEMBER_JOINED":
  case "GROUP_MEMBER_LEFT":
    // 그룹 상세 및 진행 상태 재조회
    break;

  case "GROUP_DELETED":
    // 그룹 리스트 페이지로 이동
    break;

  case "GROUP_RECOMMENDATION_VOTE_UPDATED":
    // payload의 투표 진행률만 화면에 반영
    break;
}
```

권장 원칙:

- 이벤트에 포함된 최소 정보만 즉시 반영한다.
- 정확한 최신 상태가 필요하면 기존 REST 조회 API를 호출한다.
- 알 수 없는 `eventType`은 무시하고 연결은 유지한다.
- 동일 `eventId`를 다시 받더라도 문제가 없도록 멱등하게 처리한다.
- SSE 이벤트가 일부 유실되어도 다음 조회로 상태를 복구할 수 있게 한다.

## 오류별 권장 처리

| 상황 | 처리 |
| --- | --- |
| 사용자가 화면을 이탈하거나 로그아웃함 | 재연결하지 않고 종료 |
| 네트워크 오류 또는 `5xx` | backoff 후 재연결 |
| `401 Unauthorized` | token 갱신 후 새 token으로 재연결 |
| `403 Forbidden` | 그룹 접근 권한 오류로 처리하고 재연결 중단 |
| `404 Not Found` | 삭제되었거나 존재하지 않는 그룹으로 처리하고 그룹 리스트로 이동 |
| 잘못된 event JSON | 해당 이벤트만 무시하고 오류 기록 |
| 알 수 없는 `eventType` | 해당 이벤트만 무시하고 연결 유지 |

## 현재 프론트 구현 상태

현재 프론트에는 테스트 목적의 fetch 기반 SSE 유틸이 구현되어 있다.

### `realtimeSseClient.ts`

구현된 기능:

- Bearer token을 포함한 SSE 연결
- `ReadableStream` chunk buffer 처리
- SSE frame 분리 및 파싱
- 여러 줄 `data` 결합
- heartbeat comment 무시
- `AbortController` 기반 연결 종료

### `useRealtimeEventStream.ts`

구현된 기능:

- 연결 상태 관리
- 새 연결 전 기존 연결 종료
- 수신 이벤트 로그 관리

### 운영 적용 전 부족한 기능

- 자동 재연결 및 exponential backoff
- token 만료 및 갱신 처리
- HTTP status별 오류 정책
- `Content-Type` 검증
- `Last-Event-ID` 처리
- 중복 이벤트 방어
- 운영 로그 및 모니터링

현재 구현은 `/realtime-lab` 테스트 용도로는 충분하지만, 운영 화면에서 그대로 사용하기에는 보강이 필요하다.

## 권장 구현 방향

### 권장안: 검증된 fetch 기반 SSE 라이브러리 사용

운영 기능에서는 SSE parser와 재연결 로직을 직접 확장하기보다, `Authorization` header와 재연결 제어를 지원하는 검증된 fetch 기반 SSE 라이브러리를 사용하는 것을 권장한다.

검토 후보:

- [`@microsoft/fetch-event-source`](https://github.com/Azure/fetch-event-source)

```ts
await fetchEventSource("/api/v1/realtime/events", {
  headers: {
    Authorization: `Bearer ${accessToken}`,
  },
  signal: abortController.signal,

  onopen(response) {
    // status 및 Content-Type 검증
  },

  onmessage(message) {
    const event = JSON.parse(message.data);
    handleRealtimeEvent(event);
  },

  onerror(error) {
    // 재연결 여부와 대기 시간을 결정
  },
});
```

이 라이브러리는 일반 `fetch`처럼 header를 설정하면서 SSE parsing과 재연결 흐름을 제어할 수 있다.
도입 전에는 현재 유지보수 상태와 프로젝트의 React/Next.js 환경에서 정상 동작하는지 확인한다.

## 프로젝트 적용 제안

1. 현재 직접 구현 유틸은 `/realtime-lab` 테스트 용도로 유지한다.
2. 실제 화면 연동 전 검증된 fetch 기반 SSE 라이브러리를 사용한 운영용 client를 작성한다.
3. 개인 스트림은 앱 전역에서 하나만 관리한다.
4. 그룹 스트림은 그룹 화면 생명주기에 맞춰 연결하고 종료한다.
5. 이벤트 수신 후 REST 재조회 방식으로 상태 일관성을 복구한다.
6. MVP에서는 이벤트 재전송을 보장하지 않고, `Last-Event-ID` 지원은 후속 과제로 둔다.

이 방향은 현재 Bearer 인증 정책을 유지하면서 직접 구현 범위와 장애 대응 비용을 줄이는 현실적인 선택이다.
