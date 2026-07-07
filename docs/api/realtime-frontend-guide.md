# SSE 프론트 연동 가이드

이 문서는 팀원이 Matchuri의 1차 실시간 기능을 이해하고 프론트에서 테스트할 수 있도록 정리한 공유 자료입니다.
상세 API 계약은 `docs/api/realtime.md`를 기준으로 봅니다.

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
현재 Matchuri는 access token을 Bearer 헤더로 보내므로, 프론트는 `fetch`와 `ReadableStream`으로 SSE를 읽습니다.

구현 위치:

- 유틸: `frontend/src/features/realtime/infrastructure/sse/realtimeSseClient.ts`
- hook: `frontend/src/features/realtime/application/hooks/useRealtimeEventStream.ts`
- 테스트 화면: `frontend/src/app/realtime-lab/page.tsx`

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

## 화면별 권장 연결

앱 공통 영역:

- 로그인 완료 후 개인 스트림 1개 연결을 고려합니다.
- 1차 테스트 단계에서는 `/realtime-lab`에서만 수동 연결합니다.

그룹 상세/추천 화면:

- 화면 진입 시 그룹 스트림 연결
- 화면 이탈 시 연결 종료

## 이벤트별 프론트 반응

| 이벤트 | 권장 처리 |
| --- | --- |
| `GROUP_INVITE_CREATED` | 초대 배지/토스트 표시, 필요 시 내 초대 목록 재조회 |
| `GROUP_MEMBER_JOINED` | 멤버 참여 토스트 표시 후 그룹 상세/진행 상태 재조회 |
| `GROUP_MEMBER_LEFT` | 멤버 탈퇴 토스트 표시 후 그룹 상세/진행 상태 재조회 |
| `GROUP_DELETED` | 현재 그룹 화면을 닫고 그룹 리스트 페이지로 이동 |
| `GROUP_RECOMMENDATION_STARTED` | 준비 대기 화면으로 전환 또는 recentlyRecommendation 재조회 |
| `GROUP_RECOMMENDATION_READINESS_UPDATED` | 준비 진행률 갱신 |
| `GROUP_RECOMMENDATION_OPENED` | 후보/투표 화면으로 전환 |
| `GROUP_RECOMMENDATION_VOTE_UPDATED` | 투표 진행률만 갱신 |
| `GROUP_RECOMMENDATION_VOTE_COMPLETED` | 그룹장에게 최종 확정 가능 상태 표시 |
| `GROUP_RECOMMENDATION_FINALIZED` | 최종 결과 화면으로 전환 |

## 확정된 제품 정책

- 새 멤버 참여/탈퇴 알림은 그룹 활성 멤버가 받습니다.
- 그룹 삭제 알림은 삭제 직전 그룹 활성 멤버가 받으며, 클라이언트는 그룹 리스트로 이동합니다.
- 투표 현황 이벤트는 후보별 투표 수를 노출하지 않고 진행률만 보냅니다.
- 전원 투표가 끝나도 서버가 자동 확정하지 않습니다.
- 최종 확정은 그룹장이 기존 확정 API로 수동 호출합니다.
- 멤버 탈퇴로 진행률 분모가 바뀌면 클라이언트가 기존 조회 API로 재조회합니다.

## 운영상 주의

- 현재 백엔드는 인메모리 SSE 연결 registry를 사용합니다.
- 단일 서버 기준으로 동작합니다.
- 다중 인스턴스 배포가 필요해지면 Redis pub-sub 또는 메시지 브로커가 필요합니다.
- 서버는 30초 heartbeat를 보내고, 연결 timeout은 30분입니다.
