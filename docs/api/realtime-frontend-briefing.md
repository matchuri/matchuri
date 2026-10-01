# SSE 프론트엔드 구현 브리핑

## 목적

현재 서비스 화면과 테스트 화면의 SSE 구현, 오류 처리와 복구 범위를 정리합니다.
상세 계약은 [실시간 이벤트 API](./realtime.md), 화면별 반응은 [프론트 연동 가이드](./realtime-frontend-guide.md)를 기준으로 봅니다.

## 현재 연결 방식

상태 변경은 기존 HTTP API가 처리하고, SSE는 관련 사용자에게 변경을 알립니다.
인증은 `Authorization: Bearer <accessToken>` 헤더를 사용합니다.

| 구분 | 현재 구현 | 용도 |
| --- | --- | --- |
| 서비스 개인 스트림 | `event-source-polyfill`의 `EventSourcePolyfill` | 초대 수신, 그룹장 전용 전원 투표 완료 이벤트 수신 |
| 서비스 그룹 스트림 | `EventSourcePolyfill` | 그룹 멤버·추천·투표·확정 상태 변화 수신 |
| `/realtime-lab` | 직접 구현한 `fetch` + `ReadableStream` client | 수동 연결·종료와 이벤트 로그 확인 |

브라우저 기본 `EventSource`에 임의 헤더를 붙이는 대신 서비스 client는 polyfill의 헤더 옵션을 사용합니다.
두 서비스 client의 `heartbeatTimeout`은 60초입니다. 서버 기본 heartbeat는 30초, 연결 timeout은 30분입니다.

## 구현 위치

- 서비스 client: `app/frontend/src/infrastructure/sse/myRealtimeClient.ts`, `groupRealtimeClient.ts`
- 개인 hook: `app/frontend/src/features/realtime/application/hooks/useMyRealtimeEvents.ts`
- 그룹 hook: `app/frontend/src/features/group/application/hooks/useGroupRealtimeEvents.ts`
- 공통 연결: `app/frontend/src/features/realtime/ui/components/MyRealtimeEventsInitializer.tsx`
- 테스트 client: `app/frontend/src/features/realtime/infrastructure/sse/realtimeSseClient.ts`
- 테스트 hook: `app/frontend/src/features/realtime/application/hooks/useRealtimeEventStream.ts`
- 테스트 화면: `app/frontend/src/app/realtime-lab/page.tsx`

## 서비스 연결 생명주기

- 개인 스트림은 로그인·온보딩 완료 후 앱 공통 initializer에서 연결합니다.
- 그룹 스트림은 그룹 상세·준비·투표 화면에서 연결합니다.
- 서비스 hook은 해제 시 연결을 닫습니다. access token, groupId 또는 등록 callback 등 effect 의존성이 변경되면 기존 연결을 닫고 새로 연결합니다.
- 개별 화면이 등록한 이벤트 callback에 따라 상태를 반영하거나 REST로 재조회합니다. 모든 화면이 같은 이벤트를 처리하지는 않습니다.

## 현재 오류 처리

| 구분 | 오류 시 동작 | 복구 범위 |
| --- | --- | --- |
| 그룹 스트림 | Sentry·로그 기록 후 `close()` | 해당 연결의 자동 재시도 중단; 화면 재진입·새로고침 또는 effect 재실행 시 새 연결 |
| 개인 스트림 | 로그 기록, 오류 handler에서 연결을 닫지 않음 | 네트워크 단절 등의 재연결은 polyfill 동작에 맡김; 모든 오류의 복구를 보장하지 않음 |
| `/realtime-lab` | 오류 상태와 메시지 표시 | 자동 재연결 없음; 수동으로 다시 연결 |

SSE는 REST `httpClient`의 401 token 갱신·재시도 처리를 직접 사용하지 않습니다.
SSE 자체의 상태 코드별 token 갱신·이동·재시도 정책도 없습니다. 다른 인증 처리에서 access token이 바뀌면 서비스 hook이 새 token으로 연결합니다.
서비스 이벤트 handler의 `JSON.parse`에는 공통 오류 복구 처리가 없으며, 이벤트 중복 방어는 일부 화면의 `eventId` 집합에서 수행합니다.

## 이벤트 유실과 상태 동기화

- 서버는 이벤트를 저장하지 않으며 `Last-Event-ID` 기반 재전송과 오프라인 재전송을 지원하지 않습니다.
- 개인 스트림의 `REALTIME_CONNECTED`와 `GROUP_INVITE_CREATED` 수신 시 초대 목록·존재 여부를 REST로 재조회합니다. 연결 중 누락된 초대 상태는 이 조회로 보정할 수 있습니다.
- 그룹 스트림의 `REALTIME_CONNECTED`는 연결 로그만 남깁니다. 연결 완료 시 그룹/추천 상태를 일괄 재조회하는 callback은 없습니다.
- 그룹 멤버 변동 시 각 화면은 그룹 상세나 추천 상태를 재조회합니다.
- `GROUP_RECOMMENDATION_VOTE_UPDATED` payload는 진행률만 제공합니다. 투표 화면은 이를 반영한 뒤 세션 상세·그룹 상세를 재조회합니다.
- 그룹장 전용 `GROUP_RECOMMENDATION_VOTE_COMPLETED`는 개인 hook에서 수신·기록하지만 공통 initializer에는 화면 처리 callback이 연결되어 있지 않습니다.
- 연결이 끊긴 동안의 그룹 변경은 이후 화면 진입이나 이벤트 처리 등으로 REST 조회가 실행될 때 반영됩니다. 연결 복구만으로 최신 상태가 보장되지는 않습니다.

## 테스트 client의 범위

`/realtime-lab`의 직접 구현 client는 응답 성공 여부와 body 존재 여부를 확인하고, chunk buffer와 SSE frame의 `id`, `event`, 여러 줄 `data`를 파싱합니다.
heartbeat comment는 무시하며 `AbortController`로 수동 종료합니다.
자동 재연결, token 갱신, `Content-Type` 검증과 이벤트 재전송 처리는 없습니다. 잘못된 JSON은 오류 callback으로 전달됩니다.

## 개선 제안(후속 검토)

- 그룹 스트림에 제한된 backoff 재시도와 재연결 후 그룹/추천 REST 보정 조회를 함께 검토합니다.
- 인증·권한 오류의 재시도 중단 기준과 token 갱신 후 연결 정책을 명시하면 복구 범위를 예측하기 쉬워집니다.

위 제안은 후속 개선이며 현재 구현된 동작이 아닙니다.
