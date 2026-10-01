# SSE 프론트 연동 가이드

이 문서는 팀원이 Matchuri의 1차 실시간 기능을 이해하고 프론트에서 테스트할 수 있도록 정리한 공유 자료입니다.
상세 API 계약은 [실시간 이벤트 API](./realtime.md)를 기준으로 봅니다.

## 한 줄 요약

Matchuri 1차 실시간 기능은 WebSocket이 아니라 SSE(Server-Sent Events)를 사용합니다.
클라이언트가 서버로 실시간 메시지를 보내는 구조가 아니라, 기존 HTTP API 성공 후 서버가 관련 사용자에게 이벤트를 밀어주는 구조입니다.

## 왜 SSE인가

- 현재 요구사항은 대부분 단방향 알림입니다.
- 투표, 준비 완료, 최종 확정 같은 상태 변경은 이미 HTTP API가 담당합니다.
- 프론트는 실시간 이벤트를 받으면 화면 상태를 갱신하거나 기존 조회 API로 최신 데이터를 다시 가져오면 됩니다.
- WebSocket/STOMP는 양방향 메시징, 정확한 presence, 다중 인스턴스 동기화가 필요해질 때 재검토합니다.

## 연결 API

### 개인 스트림

```http
GET /api/v1/realtime/events
Authorization: Bearer {accessToken}
Accept: text/event-stream
```

용도:

- 그룹 초대 수신
- 그룹장 전용 전원 투표 완료 알림

### 그룹 스트림

```http
GET /api/v1/groups/{groupId}/realtime/events
Authorization: Bearer {accessToken}
Accept: text/event-stream
```

용도:

- 멤버 참여/탈퇴 알림
- 그룹 삭제 알림
- 그룹 추천 시작
- 준비 상태 갱신
- 후보 생성
- 투표 진행률 갱신
- 최종 확정

## 프론트 구현 포인트

브라우저 기본 `EventSource`는 `Authorization` 헤더를 직접 붙일 수 없습니다.
현재 서비스 화면은 `event-source-polyfill`의 `EventSourcePolyfill`에 Bearer 헤더를 설정합니다. `/realtime-lab`만 `fetch`와 `ReadableStream`으로 SSE를 읽습니다.

서비스 구현 위치:

- client: `app/frontend/src/infrastructure/sse/myRealtimeClient.ts`, `groupRealtimeClient.ts`
- 개인 hook: `app/frontend/src/features/realtime/application/hooks/useMyRealtimeEvents.ts`
- 그룹 hook: `app/frontend/src/features/group/application/hooks/useGroupRealtimeEvents.ts`
- 공통 연결: `app/frontend/src/features/realtime/ui/components/MyRealtimeEventsInitializer.tsx`

테스트 구현 위치:

- 유틸: `app/frontend/src/features/realtime/infrastructure/sse/realtimeSseClient.ts`
- hook: `app/frontend/src/features/realtime/application/hooks/useRealtimeEventStream.ts`
- 테스트 화면: `app/frontend/src/app/realtime-lab/page.tsx`

테스트 화면은 로그인 후 `/realtime-lab`에서 접근합니다.

## 이벤트 envelope

모든 이벤트 data는 JSON입니다.

```json
{
  "eventId": "uuid",
  "eventType": "GROUP_RECOMMENDATION_VOTE_UPDATED",
  "occurredAt": "2026-06-02T13:00:00",
  "groupId": 3001,
  "sessionId": 5001,
  "actorMemberId": null,
  "payload": {}
}
```

프론트 기본 처리:

- 알 수 없는 `eventType`은 무시합니다.
- 이벤트를 받으면 필요한 최소 state만 갱신합니다.
- 정확한 상세 데이터가 필요하면 기존 조회 API를 다시 호출합니다.

## 현재 화면별 연결

앱 공통 영역:

- 로그인·온보딩 완료 후 공통 initializer가 개인 스트림을 연결합니다.
- 연결 완료 시 초대 목록과 존재 여부를 재조회합니다.

그룹 상세/추천 화면:

- 그룹 상세·준비·투표 화면에서 그룹 스트림을 연결합니다.
- hook 해제 시 연결을 종료하며, access token이나 callback 등 의존성이 바뀌면 새 연결을 만듭니다.

`/realtime-lab`은 별도의 수동 연결·종료 테스트 화면입니다.

## 이벤트별 프론트 반응

| 이벤트 | 현재 처리 |
| --- | --- |
| `GROUP_INVITE_CREATED` | 공통 initializer가 초대 목록과 존재 여부 재조회 |
| `GROUP_MEMBER_JOINED` | 화면별 그룹 상세/목록 또는 추천 상태 재조회 |
| `GROUP_MEMBER_LEFT` | 화면별 그룹 상세/목록 또는 추천 상태 재조회 |
| `GROUP_DELETED` | 그룹 상세 화면에서 `/group`으로 이동; 준비·투표 화면에는 처리 callback 없음 |
| `GROUP_RECOMMENDATION_STARTED` | 그룹 상세 재조회 후 다른 멤버가 시작한 세션의 준비 화면으로 이동 |
| `GROUP_RECOMMENDATION_READINESS_UPDATED` | 준비 진행률 갱신 |
| `GROUP_RECOMMENDATION_OPENED` | 후보/투표 화면으로 전환 |
| `GROUP_RECOMMENDATION_VOTE_UPDATED` | 투표 진행률 반영 후 세션 상세·그룹 상세 재조회 |
| `GROUP_RECOMMENDATION_VOTE_COMPLETED` | 개인 hook 수신·기록; 공통 initializer의 화면 처리 callback 없음 |
| `GROUP_RECOMMENDATION_FINALIZED` | 투표 화면을 최종 결과 상태로 전환하고 그룹 상세 재조회 |

## 확정된 제품 정책

- 새 멤버 참여/탈퇴 알림은 그룹 활성 멤버가 받습니다.
- 그룹 삭제 알림은 삭제 직전 그룹 활성 멤버에게 발행합니다. 현재 그룹 상세 화면이 목록 이동을 처리합니다.
- 투표 현황 이벤트는 후보별 투표 수를 노출하지 않고 진행률만 보냅니다.
- 전원 투표가 끝나도 서버가 자동 확정하지 않습니다.
- 최종 확정은 그룹장이 기존 확정 API로 수동 호출합니다.
- 멤버 탈퇴로 진행률 분모가 바뀌면 클라이언트가 기존 조회 API로 재조회합니다.

## 현재 오류·복구 처리

- 그룹 스트림은 오류 기록 후 `close()`하며 해당 연결의 자동 재시도를 중단합니다. 화면 재진입·새로고침 또는 hook effect 재실행 시 새로 연결합니다.
- 개인 스트림은 오류만 기록하고 polyfill의 네트워크 오류 재연결 동작을 유지합니다.
- SSE 자체의 401 token 갱신·재시도 정책은 없습니다. access token이 변경되면 hook effect가 새 token으로 연결합니다.
- `/realtime-lab`의 직접 구현 client에는 자동 재연결이 없습니다.
- 오프라인 이벤트 재전송은 없습니다. 개인 연결 완료 시 초대 상태는 재조회하지만, 그룹 연결 완료 시에는 연결 로그만 남깁니다.
- 개선 제안은 [구현 브리핑 하단](./realtime-frontend-briefing.md#개선-제안후속-검토)을 참고합니다.

## 운영상 주의

- 현재 백엔드는 인메모리 SSE 연결 registry를 사용합니다.
- 단일 서버 기준으로 동작합니다.
- 다중 인스턴스 배포가 필요해지면 Redis pub-sub 또는 메시지 브로커가 필요합니다.
- 서버는 30초 heartbeat를 보내고, 연결 timeout은 30분입니다.
