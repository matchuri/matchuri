# 그룹 의사결정 API

이 문서는 그룹 점심 메뉴 의사결정 API의 현재 계약 요약입니다.
상세 schema, request/response 예시, error example은 `GroupApi.java`의 OpenAPI metadata와 `/docs/openapi` 산출물을 기준으로 봅니다.

## 범위

- 그룹 생성, 목록/상세 조회, 정보 수정, 탈퇴, 삭제
- nickname 기반 그룹 초대 생성과 초대 수락/거절
- UUID 링크 기반 초대 발급, 재발급, 현재 링크 조회와 그룹 참여
- 기존 초대 코드 기반 그룹 참여
- 그룹 추천 준비 세션 시작, 준비 완료, 준비 상태 조회
- 그룹 추천 목록/상세/후보 조회
- 후보 투표와 최종 메뉴 확정
- MVP 이후 재도입 검토용 deprecated reroll endpoint

전체 endpoint, method, schema와 deprecated 여부는 `GroupApi.java`의 OpenAPI metadata와 `/docs/openapi`에서 확인합니다. 이 문서에는 권한, 만료, 상태 전이처럼 코드 목록을 복사해서는 설명되지 않는 정책만 유지합니다.

## 핵심 계약

- 그룹 생성자는 `OWNER` 멤버로 함께 저장합니다.
- 그룹마다 하나의 고정 초대 코드를 유지합니다.
- 그룹 상세는 현재 회원이 해당 그룹의 `ACTIVE` 멤버일 때만 조회할 수 있습니다.
- 그룹 상세의 member 목록은 활성 멤버만 포함합니다.
- 그룹 수정과 삭제는 `OWNER` 역할의 활성 멤버만 수행할 수 있습니다.
- 일반 멤버 탈퇴는 허용하고, `OWNER` 탈퇴는 그룹 삭제 API로 분리합니다.
- 삭제된 그룹은 목록과 상세에서 노출하지 않습니다.

## 링크 기반 초대 계약

- 링크 관리 API와 링크 참여 API는 모두 Bearer 인증이 필요한 보호 API입니다. 비회원의 로그인 유도와 로그인 후 재시도는 클라이언트가 담당합니다.
- 링크 발급·재발급·조회는 해당 그룹의 `ACTIVE` OWNER만 수행할 수 있습니다.
- 초대 토큰은 UUID 문자열이며 발급 시점부터 1일 뒤 만료됩니다.
- 활성 링크는 `expiresAt > 현재 시각`인 링크입니다. 만료 스케줄러나 상태 컬럼 없이 조회 시각을 기준으로 자동 만료를 판단합니다.
- 신규 발급은 활성 링크가 없을 때만 허용합니다. 활성 링크가 있으면 `409 GROUP_INVITE_LINK_ALREADY_EXISTS`를 반환합니다.
- 재발급은 현재 활성 링크의 `expiresAt`을 재발급 시각으로 당긴 뒤 새 링크를 생성합니다. 따라서 이전 토큰은 즉시 사용할 수 없습니다.
- 현재 링크 조회는 만료된 링크를 반환하지 않으며 활성 링크가 없으면 `404 GROUP_INVITE_LINK_NOT_FOUND`를 반환합니다.
- 링크 참여는 토큰이 존재하되 만료됐으면 `409 GROUP_INVITE_LINK_EXPIRED`, 토큰 자체가 없으면 `404 GROUP_INVITE_LINK_NOT_FOUND`를 반환합니다.
- backend access log에 토큰이 경로로 남지 않도록 링크 참여 API는 `{"token":"..."}` request body로 토큰을 받습니다.
- 그룹 삭제 시 남아 있는 활성 링크도 삭제 시각으로 만료합니다.
- 서버는 클라이언트 배포 URL을 소유하지 않으므로 응답에는 완성 URL 대신 `groupId`, `token`, `expiresAt`을 반환합니다. 클라이언트가 `token`을 초대 화면 URL 끝에 조합합니다.

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
- 그룹 추천의 `contextJson`은 후보 생성 및 `OPEN` 전환 시에는 `null`입니다. 최종 확정 요청에 `latitude`, `longitude`, `radiusMeters`, `address`가 모두 있으면 해당 위치를 스냅샷으로 저장하고, 요청 body가 없거나 하나라도 없으면 확정만 처리한 뒤 `null`을 유지합니다. 이 위치는 `GroupLocation`을 조회하거나 갱신하지 않습니다.

그룹 최종 확정 요청 body와 위치 필드는 이전 클라이언트와의 호환을 위해 선택 사항입니다. 아래 네 필드를 모두 전달하면 클라이언트가 후보 주변 식당을 탐색하며 확장한 최종 검색 반경을 보존합니다. 일부만 전달하면 최종 확정은 정상 처리하고 위치 컨텍스트는 저장하지 않습니다.

```json
{
  "latitude": 37.498095,
  "longitude": 127.027610,
  "radiusMeters": 1500,
  "address": "서울 강남구 테헤란로 123"
}
```

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
- `GROUP_INVITE_FORBIDDEN`
- `GROUP_INVITE_LINK_ALREADY_EXISTS`
- `GROUP_INVITE_LINK_NOT_FOUND`
- `GROUP_INVITE_LINK_EXPIRED`
- `GROUP_RECOMMENDATION_ACTIVE_EXISTS`
- `GROUP_RECOMMENDATION_NOT_OPEN`
- `GROUP_RECOMMENDATION_ALREADY_VOTED`
- `GROUP_RECOMMENDATION_REROLL_DISABLED`
- `GROUP_RECOMMENDATION_NO_CANDIDATES`

정확한 error envelope와 example은 OpenAPI metadata를 기준으로 봅니다.

## 관련 데이터

최신 저장 구조는 backend의 group JPA Entity를 기준으로 봅니다. 이력·만료·삭제 정책은 `docs/data/policies.md`의 그룹 절을 따릅니다.

## Harness 후보

아래 항목은 prose보다 harness로 검증하는 방향을 우선합니다.

- `OpenApiConfig.API_OPERATION_METADATA`의 GROUP/GREC entry와 backend Controller mapping drift
- `GroupApi.java` operation의 API ID, method, path, status metadata 누락
- group recommendation 상태 enum과 문서의 대표 상태 목록 drift
- group error code enum과 문서의 대표 error code 목록 drift
- `PREPARING`/`OPEN`/`EXPIRED` 상태 전이 테스트 존재 여부
- deprecated reroll endpoint가 410과 `GROUP_RECOMMENDATION_REROLL_DISABLED`를 유지하는지 여부
